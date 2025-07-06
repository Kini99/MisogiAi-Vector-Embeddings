import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.set_page_config(
        page_title="HR Onboarding Assistant",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 5px solid #9c27b0;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .confidence-high { color: #4caf50; }
    .confidence-medium { color: #ff9800; }
    .confidence-low { color: #f44336; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏢 HR Onboarding Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered assistant for new employee onboarding</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Chat Interface", "Document Management", "Analytics", "Settings"]
        )
        
        st.header("Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📊 View Stats"):
            show_stats()
    
    # Main content based on selected page
    if page == "Chat Interface":
        chat_interface()
    elif page == "Document Management":
        document_management()
    elif page == "Analytics":
        analytics_page()
    elif page == "Settings":
        settings_page()

def chat_interface():
    st.header("💬 Chat with HR Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                st.markdown("**Sources:**")
                for source in message["sources"]:
                    with st.expander(f"📄 {source['document_name']} - {source['section_title']}"):
                        st.text(source["text_preview"])
    
    # Chat input
    if prompt := st.chat_input("Ask about HR policies, benefits, or procedures..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = send_query(prompt)
                    if response:
                        # Display answer
                        st.markdown(response["answer"])
                        
                        # Display confidence
                        confidence_color = {
                            "high": "confidence-high",
                            "medium": "confidence-medium", 
                            "low": "confidence-low"
                        }.get(response["confidence"], "confidence-low")
                        
                        st.markdown(f"<span class='{confidence_color}'>**Confidence:** {response['confidence'].title()}</span>", unsafe_allow_html=True)
                        
                        # Display sources
                        if response["sources"]:
                            st.markdown("**Sources:**")
                            for source in response["sources"]:
                                with st.expander(f"📄 {source['document_name']} - {source['section_title']}"):
                                    st.text(source["text_preview"])
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response["answer"],
                            "sources": response["sources"]
                        })
                    else:
                        st.error("Failed to get response from API")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Suggested questions
    st.markdown("---")
    st.subheader("💡 Suggested Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("How many vacation days do I get?"):
            st.session_state.messages.append({"role": "user", "content": "How many vacation days do I get as a new employee?"})
            st.rerun()
        
        if st.button("How do I enroll in health insurance?"):
            st.session_state.messages.append({"role": "user", "content": "How do I enroll in health insurance?"})
            st.rerun()
    
    with col2:
        if st.button("What's the remote work policy?"):
            st.session_state.messages.append({"role": "user", "content": "Can I work remotely and what are the guidelines?"})
            st.rerun()
        
        if st.button("How do I request parental leave?"):
            st.session_state.messages.append({"role": "user", "content": "What's the process for requesting parental leave?"})
            st.rerun()

def document_management():
    st.header("📁 Document Management")
    
    # Upload section
    st.subheader("Upload HR Documents")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx', 'txt'],
        help="Upload HR documents in PDF, DOCX, or TXT format"
    )
    
    if uploaded_file is not None:
        if st.button("Upload and Process"):
            with st.spinner("Processing document..."):
                try:
                    files = {"file": uploaded_file}
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Document uploaded successfully!")
                        st.json(result)
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading document: {str(e)}")
    
    # Document statistics
    st.subheader("Document Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            stats = response.json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Documents", stats["total_documents"])
            
            with col2:
                st.metric("Unique Files", stats["unique_document_files"])
            
            with col3:
                st.metric("Categories", len(stats["category_distribution"]))
            
            # Category distribution
            if stats["category_distribution"]:
                st.subheader("Documents by Category")
                df = pd.DataFrame(list(stats["category_distribution"].items()), 
                                columns=["Category", "Count"])
                st.bar_chart(df.set_index("Category"))
            
            # Document list
            if stats["document_names"]:
                st.subheader("Uploaded Documents")
                for doc_name in stats["document_names"]:
                    st.write(f"📄 {doc_name}")
        
        else:
            st.error("Failed to get document statistics")
    
    except Exception as e:
        st.error(f"Error getting statistics: {str(e)}")

def analytics_page():
    st.header("📊 Analytics Dashboard")
    
    # Query analytics
    st.subheader("Query Analytics")
    
    # Placeholder for analytics - in a real implementation, you'd store query logs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Queries", "0")
    
    with col2:
        st.metric("Most Common Category", "Benefits")
    
    with col3:
        st.metric("Average Response Time", "2.3s")
    
    # Query category distribution
    st.subheader("Query Categories")
    categories = ["Leave Policy", "Benefits", "Conduct", "Compensation", "Work Arrangement", "General"]
    values = [25, 30, 15, 10, 12, 8]
    
    chart_data = pd.DataFrame({
        "Category": categories,
        "Queries": values
    })
    
    st.bar_chart(chart_data.set_index("Category"))

def settings_page():
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    
    # API URL setting
    api_url = st.text_input("API Base URL", value=API_BASE_URL)
    
    # Test connection
    if st.button("Test API Connection"):
        try:
            response = requests.get(f"{api_url}/health")
            if response.status_code == 200:
                st.success("✅ API connection successful!")
                st.json(response.json())
            else:
                st.error("❌ API connection failed")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
    
    st.subheader("System Information")
    st.info("""
    **HR Onboarding Assistant v1.0.0**
    
    - Vector Database: ChromaDB
    - Embedding Model: sentence-transformers/all-MiniLM-L6-v2
    - LLM: OpenAI GPT-3.5-turbo
    - Framework: FastAPI + Streamlit
    """)

def send_query(query: str) -> Dict[str, Any]:
    """Send query to API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def show_stats():
    """Show quick statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            stats = response.json()
            st.sidebar.success(f"📊 {stats['total_documents']} documents loaded")
        else:
            st.sidebar.error("Failed to get stats")
    except:
        st.sidebar.error("API not available")

if __name__ == "__main__":
    main() 