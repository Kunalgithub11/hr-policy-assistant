"""
Streamlit UI for HR Policy Assistant
Chat interface with memory persistence and sidebar information
"""

# Suppress transformers warnings about vision models not needed for text-only app
import warnings
warnings.filterwarnings("ignore", message=".*torchvision.*")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

import streamlit as st
import os
import uuid
from datetime import datetime
from agent import HRPolicyAgent


# Page configuration
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .main-header {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "agent" not in st.session_state:
    # Try to get API key from Streamlit secrets (cloud) or environment (local)
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.error("⚠️ Groq API key not found. Please add GROQ_API_KEY to Streamlit Secrets.")
        st.stop()
    
    try:
        st.session_state.agent = HRPolicyAgent(api_key)
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.stop()

if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False


# Sidebar
with st.sidebar:
    st.markdown("## 💼 HR Policy Assistant")
    st.markdown("---")
    
    st.markdown("""
    ### About This Assistant
    
    This AI-powered HR assistant helps employees understand company policies by:
    
    - 📚 **Retrieving** from verified HR documents
    - 🧠 **Remembering** conversation context
    - 🔧 **Using tools** for calculations and dates
    - ✅ **Evaluating** answer quality
    - 🚫 **Avoiding hallucinations**
    
    ### Capabilities
    
    ✓ Leave & Vacation Policies
    ✓ Salary & Payment Information
    ✓ Working Hours & Flexibility
    ✓ Attendance Rules
    ✓ Benefits & Insurance
    ✓ Work From Home Policy
    ✓ Holiday Calendar
    ✓ Resignation Process
    ✓ Dress Code Standards
    ✓ ID Card & Access Rules
    
    ### How It Works
    
    1. Ask your HR policy question
    2. Agent retrieves relevant policies
    3. Answer is generated from company documents
    4. Quality is automatically evaluated
    """)
    
    st.markdown("---")
    
    # New Conversation Button
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
    
    # Show/Hide Metrics
    st.checkbox("📊 Show Metrics", key="show_metrics")
    
    # Thread ID display
    st.markdown("---")
    st.markdown("### Session Info")
    st.code(st.session_state.thread_id, language="text")
    st.caption("Thread ID for memory persistence")
    
    st.markdown("---")
    st.markdown("""
    **Built with:**
    - LangGraph
    - ChromaDB
    - LangChain
    - Streamlit
    """)


# Main content
st.markdown('<div class="main-header">💼 HR Policy Assistant</div>', unsafe_allow_html=True)

st.markdown("""
Ask any question about company HR policies. The assistant will search through verified policy documents 
and provide accurate answers. Questions and responses are stored in conversation memory.
""")

# Chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show metrics for assistant messages if enabled
            if message["role"] == "assistant" and st.session_state.show_metrics and "metadata" in message:
                metrics = message["metadata"]
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Route", metrics.get("route", "N/A"))
                with col2:
                    st.metric("Faithfulness", f"{metrics.get('faithfulness', 0):.2f}")
                with col3:
                    st.metric("Sources", len(metrics.get("sources", [])))


# Input area
st.markdown("---")

# User input
user_input = st.chat_input("Ask about HR policies...", key="user_input")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Process with agent
    with st.spinner("🔄 Processing..."):
        try:
            result = st.session_state.agent.ask(user_input, st.session_state.thread_id)
            
            # Prepare metrics
            metrics = {
                "route": result.get("route", "N/A"),
                "faithfulness": result.get("faithfulness", 0.0),
                "sources": result.get("sources", []),
                "tool_result": result.get("tool_result", ""),
                "employee_name": result.get("employee_name", "")
            }
            
            # Add assistant message
            assistant_message = {
                "role": "assistant",
                "content": result.get("answer", "I couldn't generate a response. Please try again."),
                "metadata": metrics
            }
            
            st.session_state.messages.append(assistant_message)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.write(result.get("answer", "I couldn't generate a response."))
                
                # Show metrics
                if st.session_state.show_metrics:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Route", result.get("route", "N/A"))
                    with col2:
                        st.metric("Faithfulness", f"{result.get('faithfulness', 0):.2f}")
                    with col3:
                        st.metric("Sources", len(result.get("sources", [])))
                    with col4:
                        if result.get("employee_name"):
                            st.metric("Employee", result.get("employee_name"))
                    
                    # Show sources if available
                    if result.get("sources"):
                        st.markdown("**Sources:**")
                        for source in result.get("sources", []):
                            st.write(f"- {source.get('topic', 'Unknown')} (Rank #{source.get('rank', 0)})")
        
        except Exception as e:
            import traceback
            error_msg = str(e)
            tb = traceback.format_exc()
            
            # Log full error for debugging
            print("=" * 80)
            print("AGENT ERROR:")
            print(error_msg)
            print(tb)
            print("=" * 80)
            
            st.error(f"❌ Error: {error_msg}")
            st.code(tb)  # Show full traceback
            st.session_state.messages.pop()  # Remove user message on error


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8rem;">
    HR Policy Assistant v1.0 | Built with LangGraph & Streamlit | © 2025
</div>
""", unsafe_allow_html=True)
