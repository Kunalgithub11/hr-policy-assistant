"""
Agent execution module for HR Policy Assistant
Initializes LLM, embedder, ChromaDB, and graph
Provides ask() function for agent interaction
"""

from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
import chromadb

from state import CapstoneState
from rag import initialize_chromadb
from graph import build_graph


class HRPolicyAgent:
    """
    Main HR Policy Agent class.
    Manages LLM, embeddings, knowledge base, and execution.
    """
    
    def __init__(self, groq_api_key: str = None):
        """
        Initialize HR Policy Agent.
        
        Args:
            groq_api_key: Groq API key for LLM
        """
        # Initialize LLM
        if groq_api_key:
            self.llm = ChatGroq(
                api_key=groq_api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
        else:
            # Fallback to default Groq (expects env variable)
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )
        
        # Initialize embedder
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize knowledge base
        self.collection = initialize_chromadb()
        
        # Build graph
        self.graph = build_graph(self.llm, self.collection)
    
    def ask(self, question: str, thread_id: str) -> dict:
        """
        Ask the agent a question and get response.
        
        Args:
            question: User question
            thread_id: Conversation thread ID for memory persistence
        
    Returns:
            dict: Full state with question, answer, route, faithfulness, sources
        """
        # Initialize state
        initial_state = {
            "question": question,
            "messages": [],
            "route": "skip",
            "retrieved": "",
            "sources": [],
            "tool_result": "",
            "answer": "",
            "faithfulness": 1.0,
            "eval_retries": 0,
            "employee_name": ""
        }
        
        # Execute graph with thread_id for memory persistence
        config = {"configurable": {"thread_id": thread_id}}
        
        result = self.graph.invoke(initial_state, config)
        
        return result
    
    def get_state(self, thread_id: str) -> dict:
        """
        Get conversation state for a thread.
        
        Args:
            thread_id: Conversation thread ID
        
        Returns:
            dict: Current conversation state
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            # Get state from graph
            state = self.graph.get_state(config)
            if state:
                return state.values
            return None
        except:
            return None


# Global agent instance (for Streamlit caching)
_agent_instance = None


def get_agent(groq_api_key: str = None) -> HRPolicyAgent:
    """
    Get or create global agent instance.
    Used with Streamlit caching.
    
    Args:
        groq_api_key: Groq API key
    
    Returns:
        HRPolicyAgent: Agent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HRPolicyAgent(groq_api_key)
    return _agent_instance


# Example usage
if __name__ == "__main__":
    import os
    
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    
    # Initialize agent
    agent = HRPolicyAgent(api_key)
    
    # Test query
    print("Testing HR Policy Agent...")
    result = agent.ask("What is the leave policy?", thread_id="test_1")
    
    print(f"\nQuestion: {result['question']}")
    print(f"Route: {result['route']}")
    print(f"Faithfulness: {result['faithfulness']:.2f}")
    print(f"Answer: {result['answer']}")
