import streamlit as st
import requests
import json
import pandas as pd
from typing import List, Dict, Any
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'documents' not in st.session_state:
        st.session_state.documents = []

def create_session(username: str, email: str = None) -> bool:
    """Create a new user session"""
    try:
        response = requests.post(f"{API_BASE_URL}/sessions", json={
            "username": username,
            "email": email
        })
        if response.status_code == 200:
            data = response.json()
            st.session_state.user_id = data['user_id']
            st.session_state.session_id = data['session_id']
            return True
        return False
    except Exception as e:
        st.error(f"Error creating session: {e}")
        return False

def upload_document(file, title: str = None) -> bool:
    """Upload a document to the system"""
    try:
        files = {"file": file}
        data = {"title": title} if title else {}
        if st.session_state.user_id:
            data["user_id"] = st.session_state.user_id
        
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, data=data)
        if response.status_code == 200:
            st.success("Document uploaded successfully!")
            return True
        else:
            st.error(f"Error uploading document: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error uploading document: {e}")
        return False

def search_query(query: str, search_type: str = "hybrid", max_results: int = 10) -> Dict[str, Any]:
    """Perform a search query"""
    try:
        data = {
            "query": query,
            "search_type": search_type,
            "max_results": max_results,
            "include_sources": True
        }
        if st.session_state.user_id:
            data["user_id"] = st.session_state.user_id
        
        response = requests.post(f"{API_BASE_URL}/search", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error performing search: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error performing search: {e}")
        return None

def get_documents() -> List[Dict[str, Any]]:
    """Get list of uploaded documents"""
    try:
        params = {}
        if st.session_state.user_id:
            params["user_id"] = st.session_state.user_id
        
        response = requests.get(f"{API_BASE_URL}/documents", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching documents: {e}")
        return []

def get_search_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get search history"""
    try:
        if not st.session_state.user_id:
            return []
        
        response = requests.get(f"{API_BASE_URL}/search-history", params={
            "user_id": st.session_state.user_id,
            "limit": limit
        })
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching search history: {e}")
        return []

def submit_feedback(search_history_id: int, scores: Dict[str, float], feedback: str = None):
    """Submit feedback for a search response"""
    try:
        data = {
            "search_history_id": search_history_id,
            "relevance_score": scores["relevance"],
            "accuracy_score": scores["accuracy"],
            "completeness_score": scores["completeness"],
            "coherence_score": scores["coherence"],
            "feedback": feedback
        }
        
        response = requests.post(f"{API_BASE_URL}/feedback", json=data)
        if response.status_code == 200:
            st.success("Feedback submitted successfully!")
            return True
        else:
            st.error(f"Error submitting feedback: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")
        return False

def display_search_results(results: Dict[str, Any]):
    """Display search results in a nice format"""
    if not results:
        st.warning("No results found.")
        return
    
    # Display main response
    st.subheader("📝 Research Response")
    st.markdown(results['response'])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Response Time", f"{results['response_time']:.2f}s")
    with col2:
        st.metric("Total Results", results['total_results'])
    with col3:
        st.metric("Search Type", results['search_type'])
    with col4:
        st.metric("Sources", len(results['sources']))
    
    # Display sources
    st.subheader("📚 Sources")
    for i, source in enumerate(results['sources'], 1):
        with st.expander(f"Source {i}: {source.get('title', 'Untitled')}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(source['content'])
                if source.get('url'):
                    st.write(f"URL: {source['url']}")
            with col2:
                st.write(f"**Type:** {source['source_type']}")
                st.write(f"**Relevance:** {source['relevance_score']:.2f}")
                if source.get('credibility_score'):
                    st.write(f"**Credibility:** {source['credibility_score']:.2f}")

def create_analytics_dashboard():
    """Create analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")
    
    # Get search history
    history = get_search_history(100)
    if not history:
        st.info("No search history available for analytics.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(history)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Search trends over time
    st.write("**Search Trends Over Time**")
    daily_searches = df.groupby(df['created_at'].dt.date).size().reset_index()
    daily_searches.columns = ['Date', 'Searches']
    
    fig = px.line(daily_searches, x='Date', y='Searches', title='Daily Search Volume')
    st.plotly_chart(fig)
    
    # Search type distribution
    st.write("**Search Type Distribution**")
    search_type_counts = df['search_type'].value_counts()
    fig = px.pie(values=search_type_counts.values, names=search_type_counts.index, title='Search Type Distribution')
    st.plotly_chart(fig)
    
    # Response time analysis
    st.write("**Response Time Analysis**")
    fig = px.histogram(df, x='response_time', title='Response Time Distribution', nbins=20)
    st.plotly_chart(fig)
    
    # Average response time by search type
    avg_response_time = df.groupby('search_type')['response_time'].mean().reset_index()
    fig = px.bar(avg_response_time, x='search_type', y='response_time', title='Average Response Time by Search Type')
    st.plotly_chart(fig)

def main():
    st.set_page_config(
        page_title="Research Assistant",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    st.sidebar.title("🔬 Research Assistant")
    
    # User session
    if not st.session_state.user_id:
        st.sidebar.subheader("👤 User Session")
        username = st.sidebar.text_input("Username", key="username_input")
        email = st.sidebar.text_input("Email (optional)", key="email_input")
        
        if st.sidebar.button("Start Session"):
            if username:
                if create_session(username, email):
                    st.sidebar.success("Session created!")
                    st.rerun()
            else:
                st.sidebar.error("Please enter a username")
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.user_id}")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.session_state.session_id = None
            st.rerun()
    
    # Main content
    st.title("🔬 Advanced Research Assistant")
    st.markdown("""
    This research assistant combines document analysis, web search, and AI-powered synthesis to provide comprehensive research insights.
    
    **Features:**
    - 📄 PDF document upload and processing
    - 🌐 Real-time web search integration
    - 🔍 Hybrid search (document + web)
    - 📊 Source verification and credibility scoring
    - 🤖 AI-powered response synthesis
    """)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search", "📄 Documents", "📊 Analytics", "📚 History", "⚙️ Settings"])
    
    with tab1:
        st.header("🔍 Research Search")
        
        # Search form
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_area("Enter your research query:", height=100, placeholder="e.g., What are the latest developments in quantum computing?")
        with col2:
            search_type = st.selectbox("Search Type", ["hybrid", "document", "web"], help="Hybrid combines document and web search")
            max_results = st.slider("Max Results", 5, 20, 10)
        
        if st.button("🔍 Search", type="primary"):
            if query.strip():
                with st.spinner("Searching..."):
                    results = search_query(query, search_type, max_results)
                    if results:
                        st.session_state.search_history.append({
                            'query': query,
                            'results': results,
                            'timestamp': datetime.now()
                        })
                        display_search_results(results)
                        
                        # Feedback section
                        st.subheader("💬 Feedback")
                        st.write("How would you rate this response?")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            relevance = st.slider("Relevance", 1, 5, 3, key="relevance")
                        with col2:
                            accuracy = st.slider("Accuracy", 1, 5, 3, key="accuracy")
                        with col3:
                            completeness = st.slider("Completeness", 1, 5, 3, key="completeness")
                        with col4:
                            coherence = st.slider("Coherence", 1, 5, 3, key="coherence")
                        
                        feedback_text = st.text_area("Additional feedback (optional):", key="feedback_text")
                        
                        if st.button("Submit Feedback"):
                            scores = {
                                "relevance": relevance,
                                "accuracy": accuracy,
                                "completeness": completeness,
                                "coherence": coherence
                            }
                            # Note: This would need the search_history_id from the actual response
                            st.info("Feedback submission would be implemented with actual search history ID")
            else:
                st.warning("Please enter a query")
    
    with tab2:
        st.header("📄 Document Management")
        
        # Upload section
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
        title = st.text_input("Document Title (optional)")
        
        if uploaded_file and st.button("Upload"):
            if upload_document(uploaded_file, title):
                st.rerun()
        
        # Document list
        st.subheader("📚 Uploaded Documents")
        documents = get_documents()
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc['title']} ({doc['filename']})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Size:** {doc['file_size']} bytes")
                        st.write(f"**Type:** {doc['file_type']}")
                    with col2:
                        st.write(f"**Status:** {'✅ Processed' if doc['is_processed'] else '⏳ Processing'}")
                    with col3:
                        if st.button(f"Delete", key=f"delete_{doc['id']}"):
                            st.info("Delete functionality would be implemented here")
        else:
            st.info("No documents uploaded yet.")
    
    with tab3:
        create_analytics_dashboard()
    
    with tab4:
        st.header("📚 Search History")
        history = get_search_history(50)
        if history:
            for item in history:
                with st.expander(f"🔍 {item['query'][:50]}... ({item['created_at']})"):
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Search Type:** {item['search_type']}")
                    st.write(f"**Response Time:** {item['response_time']:.2f}s")
                    if item.get('user_rating'):
                        st.write(f"**User Rating:** {item['user_rating']}/5")
        else:
            st.info("No search history available.")
    
    with tab5:
        st.header("⚙️ Settings")
        st.write("**API Configuration**")
        st.code(f"API Base URL: {API_BASE_URL}")
        
        st.write("**System Status**")
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                health = response.json()
                st.success("✅ API is healthy")
                st.json(health)
            else:
                st.error("❌ API is not responding")
        except Exception as e:
            st.error(f"❌ Cannot connect to API: {e}")

if __name__ == "__main__":
    main() 