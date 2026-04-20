"""
State definition for HR Policy Assistant LangGraph
Defines the complete state flow through the agent
"""

from typing import TypedDict, Literal


class CapstoneState(TypedDict):
    """
    Core state dictionary for LangGraph StateGraph.
    Tracks all information flowing through the agent.
    """
    question: str                    # Current user question
    messages: list                   # Conversation history
    route: Literal["retrieve", "tool", "skip"]  # Router decision
    retrieved: str                   # Retrieved context from RAG
    sources: list                    # Source documents metadata
    tool_result: str                 # Tool execution result
    answer: str                      # Generated answer
    faithfulness: float              # Evaluation score (0-1)
    eval_retries: int               # Retry counter for evaluation
    employee_name: str              # Extracted employee name from conversation
