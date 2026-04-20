"""
LangGraph StateGraph builder for HR Policy Assistant
Creates complete graph with 8 nodes and conditional routing
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.language_model import BaseLanguageModel
import chromadb

from state import CapstoneState
from nodes import (
    memory_node,
    router_node,
    retrieval_node,
    skip_retrieval_node,
    tool_node,
    answer_node,
    eval_node,
    save_node
)


def build_graph(llm: BaseLanguageModel, collection: chromadb.Collection):
    """
    Build complete StateGraph for HR Policy Assistant.
    
    Graph structure:
    memory → router → (retrieval | tool | skip) → answer → eval → (retry | save) → END
    
    Args:
        llm: Language model instance
        collection: ChromaDB collection
    
    Returns:
        Compiled graph with MemorySaver
    """
    
    # Create StateGraph
    graph = StateGraph(CapstoneState)
    
    # Add nodes (8 total)
    graph.add_node(
        "memory",
        lambda state: memory_node(state, llm)
    )
    
    graph.add_node(
        "router",
        lambda state: router_node(state, llm)
    )
    
    graph.add_node(
        "retrieval",
        lambda state: retrieval_node(state, collection)
    )
    
    graph.add_node(
        "skip_retrieval",
        lambda state: skip_retrieval_node(state)
    )
    
    graph.add_node(
        "tool",
        lambda state: tool_node(state)
    )
    
    graph.add_node(
        "answer",
        lambda state: answer_node(state, llm)
    )
    
    graph.add_node(
        "eval",
        lambda state: eval_node(state, llm)
    )
    
    graph.add_node(
        "save",
        lambda state: save_node(state)
    )
    
    # Add edges
    # Entry point
    graph.set_entry_point("memory")
    
    # memory → router (always)
    graph.add_edge("memory", "router")
    
    # router → conditional routing
    def route_decision(state):
        route = state.get("route", "skip")
        if route == "retrieve":
            return "retrieval"
        elif route == "tool":
            return "tool"
        else:
            return "skip_retrieval"
    
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "retrieval": "retrieval",
            "tool": "tool",
            "skip_retrieval": "skip_retrieval"
        }
    )
    
    # retrieval → answer (always)
    graph.add_edge("retrieval", "answer")
    
    # tool → answer (always)
    graph.add_edge("tool", "answer")
    
    # skip_retrieval → answer (always)
    graph.add_edge("skip_retrieval", "answer")
    
    # answer → eval (always)
    graph.add_edge("answer", "eval")
    
    # eval → conditional routing (retry or save)
    def eval_decision(state):
        faithfulness = state.get("faithfulness", 0.7)
        eval_retries = state.get("eval_retries", 0)
        
        # Retry if score < 0.7 and retries < 2
        if faithfulness < 0.7 and eval_retries < 2:
            return "answer"  # Go back to answer for retry
        else:
            return "save"  # Proceed to save
    
    graph.add_conditional_edges(
        "eval",
        eval_decision,
        {
            "answer": "answer",
            "save": "save"
        }
    )
    
    # save → END (always)
    graph.add_edge("save", END)
    
    # Compile with MemorySaver for conversation persistence
    memory = MemorySaver()
    compiled_graph = graph.compile(checkpointer=memory)
    
    return compiled_graph
