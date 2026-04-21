"""
Node functions for HR Policy Assistant LangGraph
Implements all 8 nodes: memory, router, retrieval, skip, tool, answer, eval, save
"""

import re
import logging
from typing import Any
from langchain_core.language_models import BaseLanguageModel
import chromadb
from state import CapstoneState
from rag import retrieve_documents
from tools import execute_tool

logger = logging.getLogger(__name__)


def memory_node(state: CapstoneState, llm: BaseLanguageModel) -> dict:
    """
    Memory node: Manages conversation history and extracts employee name.
    - Appends current question to messages
    - Maintains sliding window of last 6 messages
    - Extracts employee name from "my name is ___" pattern
    
    Args:
        state: Current state
        llm: Language model
    
    Returns:
        dict: Updated state with messages and employee_name
    """
    # Add current question to messages
    messages = state.get("messages", [])
    messages.append({"role": "user", "content": state["question"]})
    
    # Keep sliding window of last 6 messages
    if len(messages) > 6:
        messages = messages[-6:]
    
    # Extract employee name from question
    employee_name = state.get("employee_name", "")
    
    # Pattern: "my name is ___" or "I am ___"
    name_patterns = [
        r"my name is\s+([A-Za-z]+)",
        r"i am\s+([A-Za-z]+)",
        r"i'm\s+([A-Za-z]+)",
        r"call me\s+([A-Za-z]+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, state["question"].lower())
        if match:
            employee_name = match.group(1).capitalize()
            break
    
    return {
        "messages": messages,
        "employee_name": employee_name
    }


def router_node(state: CapstoneState, llm: BaseLanguageModel) -> dict:
    """
    Router node: Decides routing based on question type.
    Routes to: "retrieve" (RAG), "tool" (calculator/datetime), or "skip" (no retrieval needed)
    
    Args:
        state: Current state
        llm: Language model
    
    Returns:
        dict: Route decision
    """
    question = state["question"].lower()
    
    # System prompt for router
    system_prompt = """You are a router that decides how to handle employee questions about HR policies.

Your task: Analyze the question and decide ONLY ONE of:
1. "retrieve" - Question is about HR policies (retrieve from knowledge base)
2. "tool" - Question needs calculator or date/time tool
3. "skip" - Question is greeting, general chat, or needs no retrieval

Rules:
- HR Policy topics: leave, salary, attendance, working hours, benefits, dress code, ID card, work from home, holidays, resignation
- Tool topics: "calculate", "what is today", "current date", "time", "math"
- Skip topics: "hello", "hi", "how are you", "thanks", greetings, small talk

Output ONLY the word: retrieve, tool, or skip"""

    # Classify question
    classification_prompt = f"{system_prompt}\n\nQuestion: {state['question']}\n\nDecision:"
    
    try:
        response = llm.invoke(classification_prompt).content.strip().lower()
        
        # Extract first word and validate
        first_word = response.split()[0] if response else "skip"
        
        if first_word in ["retrieve", "tool", "skip"]:
            route = first_word
        else:
            # Default routing based on keywords
            if any(keyword in question for keyword in ["calculate", "math", "compute", "date", "time", "today", "when"]):
                route = "tool"
            elif any(keyword in question for keyword in ["leave", "salary", "attendance", "policy", "benefits", "working", "dress", "holiday", "resignation", "work from home", "hours", "card"]):
                route = "retrieve"
            else:
                route = "skip"
    except:
        # Fallback keyword-based routing
        if any(keyword in question for keyword in ["calculate", "math", "date", "time", "today"]):
            route = "tool"
        elif any(keyword in question for keyword in ["leave", "salary", "attendance", "policy", "benefits", "working", "dress", "holiday", "resignation", "work from home", "hours", "card"]):
            route = "retrieve"
        else:
            route = "skip"
    
    return {"route": route}


def retrieval_node(state: CapstoneState, collection: chromadb.Collection) -> dict:
    """
    Retrieval node: Retrieves relevant documents from RAG.
    - Embeds query
    - Retrieves top 3 documents
    - Formats as [Topic]\ncontent
    
    Args:
        state: Current state
        collection: ChromaDB collection
    
    Returns:
        dict: Retrieved documents and sources
    """
    question = state["question"]
    
    # Retrieve documents
    retrieved_context, sources = retrieve_documents(question, collection, top_k=3)
    
    return {
        "retrieved": retrieved_context,
        "sources": sources
    }


def skip_retrieval_node(state: CapstoneState) -> dict:
    """
    Skip retrieval node: Used when retrieval is not needed.
    Returns empty retrieved context and no sources.
    
    Args:
        state: Current state
    
    Returns:
        dict: Empty retrieved and sources
    """
    return {
        "retrieved": "",
        "sources": []
    }


def tool_node(state: CapstoneState) -> dict:
    """
    Tool node: Executes tools (datetime or calculator).
    
    Args:
        state: Current state
    
    Returns:
        dict: Tool result
    """
    question = state["question"].lower()
    tool_result = ""
    
    # Detect and execute tool
    if any(keyword in question for keyword in ["calculate", "math", "compute", "=", "+"]):
        # Extract expression for calculator
        # Find arithmetic expression in question
        import re
        numbers_pattern = r'\d+(?:\.\d+)?[+\-*/%()]*\d+[+\-*/%()]*(?:\d+|\.|\))*'
        match = re.search(numbers_pattern, question)
        
        if match:
            expression = match.group(0)
            tool_result = execute_tool("calculator", expression)
        else:
            # Try to find calculation request
            tool_result = execute_tool("calculator", question)
    elif any(keyword in question for keyword in ["date", "time", "today", "current", "when"]):
        tool_result = execute_tool("datetime")
    else:
        tool_result = "Tool not recognized."
    
    return {"tool_result": tool_result}


def answer_node(state: CapstoneState, llm: BaseLanguageModel) -> dict:
    """
    Answer node: Generates answer based on context.
    Uses strict system prompt to prevent hallucination.
    Includes context, tool_result, and conversation history.
    
    Args:
        state: Current state
        llm: Language model
    
    Returns:
        dict: Generated answer
    """
    # Build context for answer generation
    context = state.get("retrieved", "")
    tool_result = state.get("tool_result", "")
    messages = state.get("messages", [])
    employee_name = state.get("employee_name", "")
    
    # Strict system prompt to prevent hallucination
    system_prompt = """You are an HR Policy Assistant. Your role is to help employees understand company HR policies.

CRITICAL RULES:
1. Answer ONLY using the provided context/knowledge base
2. If context is empty or doesn't contain the answer, clearly say: "I don't have information about this in the company HR policies."
3. Never hallucinate or invent policies
4. If a question is outside HR policies, politely decline
5. Be accurate, concise, and professional
6. Reference the specific policy section when relevant

If employee name was provided, use it in responses. Be helpful but honest about knowledge limitations."""

    # Build conversation context
    conversation = ""
    for msg in messages[-4:]:  # Last 4 messages for context
        role = msg.get("role", "").upper()
        content = msg.get("content", "")
        conversation += f"\n{role}: {content}"
    
    # Build answer prompt
    answer_prompt = f"""{system_prompt}

Employee Name: {employee_name if employee_name else "Not provided"}

Company Context:
{context if context else "No specific policy document found for this query."}

Tool Information:
{tool_result if tool_result else "No tool information available."}

Recent Conversation:
{conversation}

Current Question: {state['question']}

Answer:"""

    try:
        response = llm.invoke(answer_prompt).content
        answer = response.strip()
    except Exception as e:
        logger.error(f"ANSWER_NODE FAILED: {str(e)}", exc_info=True)
        print(f"\n\n!!! ANSWER_NODE ERROR !!!")
        print(f"Exception: {type(e).__name__}: {str(e)}")
        print(f"Question: {state['question']}")
        print(f"Context length: {len(state.get('retrieved', ''))}")
        print(f"Tool result: {state.get('tool_result', '')}")
        print("!!! END ERROR !!!\n\n")
        answer = f"I apologize, but I encountered an error processing your question. Please rephrase and try again."
    
    return {"answer": answer}


def eval_node(state: CapstoneState, llm: BaseLanguageModel) -> dict:
    """
    Evaluation node: Assesses faithfulness of answer using LLM.
    - Scores answer from 0 to 1
    - If score < 0.7, marks for retry
    - Max retries = 2
    
    Args:
        state: Current state
        llm: Language model
    
    Returns:
        dict: Faithfulness score and retry decision
    """
    question = state["question"]
    answer = state["answer"]
    context = state.get("retrieved", "")
    eval_retries = state.get("eval_retries", 0)
    
    # Evaluation prompt
    eval_prompt = f"""You are an evaluator assessing whether an HR assistant's answer is faithful to the provided context.

Context (Knowledge Base):
{context if context else "No context provided"}

Question: {question}

Answer: {answer}

Task: Rate the answer's faithfulness on a scale of 0 to 1:
- 1.0: Answer is perfectly grounded in the context and accurate
- 0.7-0.9: Answer is mostly accurate with minor issues
- 0.4-0.6: Answer has significant inaccuracies or hallucinations
- 0.0-0.3: Answer is not grounded in context, mostly hallucinated

Output ONLY a single decimal number between 0 and 1. No explanation."""

    try:
        response = llm.invoke(eval_prompt).content.strip()
        # Extract first number found
        import re
        match = re.search(r'0\.\d+|[01]', response)
        if match:
            faithfulness = float(match.group(0))
        else:
            logger.warning(f"Could not parse faithfulness score from LLM response: {response}")
            faithfulness = 0.7
    except Exception as e:
        logger.error(f"EVAL_NODE FAILED: {str(e)}", exc_info=True)
        faithfulness = 0.7
    
    # Determine if retry is needed
    retry_needed = (faithfulness < 0.7) and (eval_retries < 2)
    
    return {
        "faithfulness": faithfulness,
        "eval_retries": eval_retries + (1 if retry_needed else 0)
    }


def save_node(state: CapstoneState) -> dict:
    """
    Save node: Saves assistant answer to message history.
    Appends to conversation history for memory.
    
    Args:
        state: Current state
    
    Returns:
        dict: Updated messages with answer
    """
    messages = state.get("messages", [])
    answer = state.get("answer", "")
    
    # Add assistant answer to messages
    messages.append({
        "role": "assistant",
        "content": answer
    })
    
    # Keep sliding window of last 6 messages
    if len(messages) > 6:
        messages = messages[-6:]
    
    return {"messages": messages}
