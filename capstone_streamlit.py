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
from dotenv import load_dotenv
from agent import HRPolicyAgent

# Load .env file for local development (Streamlit Cloud uses st.secrets)
load_dotenv()


# Page configuration
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #2E7D8B;
        --secondary: #1E5A68;
        --accent: #3DB8D1;
        --success: #27AE60;
        --warning: #F39C12;
        --danger: #E74C3C;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2E7D8B 0%, #1E5A68 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(46, 125, 139, 0.2);
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    .main-header p {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat messages styling */
    .chat-user-msg {
        background: linear-gradient(135deg, #3DB8D1 0%, #2E7D8B 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        border-left: 4px solid #1E5A68;
        box-shadow: 0 2px 8px rgba(46, 125, 139, 0.15);
    }
    
    .chat-assistant-msg {
        background: white;
        color: #1a1a1a;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 0.8rem 0;
        border-left: 4px solid #27AE60;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E0E7FF;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(46, 125, 139, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #7a7a7a;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        color: #2E7D8B;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2E7D8B 0%, #1E5A68 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(46, 125, 139, 0.25);
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(46, 125, 139, 0.35);
        transform: translateY(-2px);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border: 2px solid #E0E7FF;
        border-radius: 10px;
        padding: 0.8rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E7D8B;
        box-shadow: 0 0 0 3px rgba(46, 125, 139, 0.1);
    }
    
    /* Source cards */
    .source-card {
        background: #F0F7F9;
        border-left: 4px solid #3DB8D1;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }
    
    .source-topic {
        color: #2E7D8B;
        font-weight: 600;
    }
    
    .source-rank {
        color: #7a7a7a;
        font-size: 0.85rem;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: #F8F9FA;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #2E7D8B;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.85rem;
        padding: 2rem 1rem;
        border-top: 1px solid #E0E7FF;
        margin-top: 2rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .status-success {
        background: #D4EDDA;
        color: #155724;
    }
    
    .status-warning {
        background: #FFF3CD;
        color: #856404;
    }
    
    .status-error {
        background: #F8D7DA;
        color: #721C24;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .metric-value {
            font-size: 1.4rem;
        }
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
    st.markdown('''
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="font-size: 1.8rem; color: #2E7D8B; margin: 0;">💼 HR Assistant</h1>
            <p style="color: #7a7a7a; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Powered by LangGraph & LLM</p>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Key Features")
    st.markdown("""
    - 📚 RAG-powered retrieval
    - 🧠 Conversation memory
    - 🔧 Smart tool usage
    - ✅ Quality evaluation
    - 🚫 Hallucination control
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Capabilities section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📋 Policy Categories")
    st.markdown("""
    ✓ Leave & Vacation
    ✓ Salary & Payments
    ✓ Work Hours
    ✓ Attendance
    ✓ Benefits
    ✓ WFH Policy
    ✓ Holidays
    ✓ Resignation
    ✓ Dress Code
    ✓ ID & Access
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()
    
    with col2:
        st.checkbox("📊 Details", key="show_metrics", label_visibility="collapsed")
    
    st.markdown("---")
    
    # Session info
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ℹ️ Session Info")
    st.caption(f"**ID:** `{st.session_state.thread_id[:8]}...`")
    st.caption(f"**Messages:** {len(st.session_state.messages)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tech stack
    st.markdown("""
    <div style="text-align: center; color: #7a7a7a; font-size: 0.85rem; padding: 1rem 0;">
    <strong>Built with</strong><br/>
    LangGraph • ChromaDB • LangChain<br/>
    Groq API • Streamlit
    </div>
    """, unsafe_allow_html=True)


# Main content
st.markdown('''
    <div class="main-header">
        <h1>💼 HR Policy Assistant</h1>
        <p>Your AI-powered guide to company policies</p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("""
**Welcome!** Ask any question about company HR policies. The assistant will search through verified policy documents 
and provide accurate answers with sources.
""")

# Display stats
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Messages</div><div class="metric-value">{len(st.session_state.messages)//2}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Session Active</div><div class="metric-value">✓</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Model</div><div class="metric-value">Llama 3.3</div></div>', unsafe_allow_html=True)

st.markdown("---")

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
                    st.markdown("**📊 Response Metrics:**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        route_badge = f'<span class="status-badge status-success">{result.get("route", "N/A").upper()}</span>'
                        st.markdown(f'Route: {route_badge}', unsafe_allow_html=True)
                    
                    with col2:
                        faith = result.get('faithfulness', 0)
                        faith_color = "success" if faith >= 0.7 else "warning" if faith >= 0.5 else "error"
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Faithfulness</div><div class="metric-value">{faith:.2f}</div></div>', unsafe_allow_html=True)
                    
                    with col3:
                        sources_count = len(result.get("sources", []))
                        st.markdown(f'<div class="metric-card"><div class="metric-label">Sources</div><div class="metric-value">{sources_count}</div></div>', unsafe_allow_html=True)
                    
                    with col4:
                        if result.get("employee_name"):
                            st.markdown(f'<div class="metric-card"><div class="metric-label">Employee</div><div class="metric-value">{result.get("employee_name")}</div></div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="metric-card"><div class="metric-label">Employee</div><div class="metric-value">-</div></div>', unsafe_allow_html=True)
                    
                    # Show sources if available
                    if result.get("sources"):
                        st.markdown("**📚 Retrieved Policies:**")
                        for i, source in enumerate(result.get("sources", []), 1):
                            st.markdown(f'''
                                <div class="source-card">
                                    <span class="source-topic">📄 {source.get('topic', 'Unknown')}</span>
                                    <br/><span class="source-rank">Relevance Rank: #{source.get('rank', 0)}</span>
                                </div>
                            ''', unsafe_allow_html=True)
        
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
st.markdown("""
<div class="footer">
    <p><strong>HR Policy Assistant</strong> v1.0</p>
    <p>Powered by <strong>LangGraph</strong> • <strong>Groq API</strong> • <strong>ChromaDB</strong></p>
    <p style="font-size: 0.75rem; color: #bbb; margin-top: 1rem;">© 2025 • Built with AI & ❤️</p>
</div>
""", unsafe_allow_html=True)
