import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Intelligent Customer Support System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .ticket-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .priority-high { border-left: 4px solid #ff4444; }
    .priority-medium { border-left: 4px solid #ffaa00; }
    .priority-low { border-left: 4px solid #44aa44; }
    .priority-urgent { border-left: 4px solid #cc0000; }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request to backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def get_dashboard_data() -> Dict:
    """Get dashboard data from API"""
    return make_api_request("/dashboard/")

def get_tickets(status_filter: str = None) -> List[Dict]:
    """Get tickets from API"""
    endpoint = "/tickets/"
    if status_filter:
        endpoint += f"?status_filter={status_filter}"
    return make_api_request(endpoint) or []

def create_ticket(ticket_data: Dict) -> Dict:
    """Create a new ticket"""
    return make_api_request("/tickets/", method="POST", data=ticket_data)

def update_ticket(ticket_id: int, update_data: Dict) -> Dict:
    """Update a ticket"""
    return make_api_request(f"/tickets/{ticket_id}", method="PUT", data=update_data)

def resolve_ticket(ticket_id: int, resolution: str) -> Dict:
    """Resolve a ticket"""
    return make_api_request(f"/tickets/{ticket_id}/resolve", method="POST", data={"resolution": resolution})

def escalate_ticket(ticket_id: int, reason: str) -> Dict:
    """Escalate a ticket"""
    return make_api_request(f"/tickets/{ticket_id}/escalate", method="POST", data={"escalation_reason": reason})

def analyze_ticket(subject: str, description: str) -> Dict:
    """Analyze ticket content"""
    return make_api_request("/analyze-ticket/", method="POST", data={"subject": subject, "description": description})

def generate_response(subject: str, description: str, category: str) -> Dict:
    """Generate response for ticket"""
    return make_api_request("/generate-response/", method="POST", data={
        "subject": subject, 
        "description": description, 
        "category": category
    })

# Main application
def main():
    st.markdown('<h1 class="main-header">🎫 Intelligent Customer Support System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Submit Ticket", "Ticket Management", "Customer Portal", "Analytics", "Knowledge Base"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Submit Ticket":
        show_ticket_submission()
    elif page == "Ticket Management":
        show_ticket_management()
    elif page == "Customer Portal":
        show_customer_portal()
    elif page == "Analytics":
        show_analytics()
    elif page == "Knowledge Base":
        show_knowledge_base()

def show_dashboard():
    """Show the main dashboard"""
    st.header("📊 Support Dashboard")
    
    # Get dashboard data
    dashboard_data = get_dashboard_data()
    if not dashboard_data:
        st.error("Unable to load dashboard data")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tickets",
            dashboard_data["statistics"]["total_tickets"],
            delta=None
        )
    
    with col2:
        st.metric(
            "Open Tickets",
            dashboard_data["statistics"]["open_tickets"],
            delta=None
        )
    
    with col3:
        st.metric(
            "Avg Response Time",
            f"{dashboard_data['average_response_time_hours']}h",
            delta=None
        )
    
    with col4:
        resolved_count = dashboard_data["status_distribution"].get("resolved", 0)
        total_count = dashboard_data["statistics"]["total_tickets"]
        resolution_rate = (resolved_count / total_count * 100) if total_count > 0 else 0
        st.metric(
            "Resolution Rate",
            f"{resolution_rate:.1f}%",
            delta=None
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tickets by Category")
        category_data = dashboard_data["statistics"]["category_distribution"]
        if category_data:
            fig = px.pie(
                values=list(category_data.values()),
                names=list(category_data.keys()),
                title="Ticket Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tickets by Priority")
        priority_data = dashboard_data["statistics"]["priority_distribution"]
        if priority_data:
            fig = px.bar(
                x=list(priority_data.keys()),
                y=list(priority_data.values()),
                title="Tickets by Priority Level",
                color=list(priority_data.values()),
                color_continuous_scale="RdYlGn_r"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent tickets
    st.subheader("🕒 Recent Tickets")
    recent_tickets = dashboard_data.get("recent_tickets", [])
    
    if recent_tickets:
        for ticket in recent_tickets:
            priority_class = f"priority-{ticket['priority']}"
            st.markdown(f"""
            <div class="ticket-card {priority_class}">
                <h4>#{ticket['id']} - {ticket['subject']}</h4>
                <p><strong>Status:</strong> {ticket['status'].replace('_', ' ').title()}</p>
                <p><strong>Priority:</strong> {ticket['priority'].title()}</p>
                <p><strong>Category:</strong> {ticket['category'].replace('_', ' ').title() if ticket['category'] else 'Not categorized'}</p>
                <p><strong>Customer:</strong> {ticket['customer_email']}</p>
                <p><strong>Created:</strong> {ticket['created_at'][:10]}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent tickets to display")

def show_ticket_submission():
    """Show ticket submission form"""
    st.header("📝 Submit Support Ticket")
    
    with st.form("ticket_submission"):
        st.subheader("Customer Information")
        customer_name = st.text_input("Your Name (Optional)")
        customer_email = st.text_input("Email Address *", placeholder="your.email@example.com")
        
        st.subheader("Ticket Details")
        subject = st.text_input("Subject *", placeholder="Brief description of your issue")
        description = st.text_area(
            "Description *", 
            placeholder="Please provide detailed information about your issue...",
            height=200
        )
        
        # Real-time analysis
        if subject and description:
            st.subheader("🔍 AI Analysis Preview")
            analysis = analyze_ticket(subject, description)
            if analysis:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**Category:** {analysis['category'].replace('_', ' ').title()}")
                with col2:
                    st.warning(f"**Priority:** {analysis['priority'].title()}")
                with col3:
                    sentiment_color = {
                        "positive": "🟢",
                        "neutral": "🟡", 
                        "negative": "🔴"
                    }
                    st.info(f"**Sentiment:** {sentiment_color.get(analysis['sentiment'], '🟡')} {analysis['sentiment'].title()}")
                
                st.info(f"**Tags:** {', '.join(analysis['tags'])}")
        
        submitted = st.form_submit_button("Submit Ticket")
        
        if submitted:
            if not customer_email or not subject or not description:
                st.error("Please fill in all required fields")
                return
            
            # Create ticket
            ticket_data = {
                "subject": subject,
                "description": description,
                "customer_email": customer_email,
                "customer_name": customer_name if customer_name else None
            }
            
            result = create_ticket(ticket_data)
            if result:
                st.success("✅ Ticket submitted successfully!")
                st.balloons()
                
                # Show auto-response
                if result.get("auto_response"):
                    st.subheader("🤖 Auto-Generated Response")
                    st.info(result["auto_response"])
                    
                    if result.get("confidence_score"):
                        confidence = result["confidence_score"]
                        if confidence < 0.7:
                            st.warning(f"⚠️ Low confidence response ({confidence:.2%}). This ticket may need human review.")
                        else:
                            st.success(f"✅ High confidence response ({confidence:.2%})")
                
                # Show similar tickets
                if result.get("similar_tickets"):
                    st.subheader("📋 Similar Past Tickets")
                    for similar in result["similar_tickets"][:3]:
                        st.markdown(f"""
                        - **#{similar['ticket_id']}**: {similar['subject']}
                          - Similarity: {similar['similarity_score']:.2%}
                          - Resolution: {similar.get('resolution', 'No resolution recorded')}
                        """)

def show_ticket_management():
    """Show ticket management interface for agents"""
    st.header("🎫 Ticket Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "open", "in_progress", "resolved", "closed", "escalated"]
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "low", "medium", "high", "urgent"]
        )
    with col3:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "shipping_issue", "payment_problem", "product_return", "technical_support", 
             "account_issue", "general_inquiry", "refund_request", "damaged_product"]
        )
    
    # Get tickets
    tickets = get_tickets()
    if not tickets:
        st.info("No tickets found")
        return
    
    # Apply filters
    if status_filter != "All":
        tickets = [t for t in tickets if t["status"] == status_filter]
    if priority_filter != "All":
        tickets = [t for t in tickets if t["priority"] == priority_filter]
    if category_filter != "All":
        tickets = [t for t in tickets if t["category"] == category_filter]
    
    # Display tickets
    for ticket in tickets:
        priority_class = f"priority-{ticket['priority']}"
        
        with st.expander(f"#{ticket['id']} - {ticket['subject']} ({ticket['status'].title()})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Customer:** {ticket['customer_email']} {f"({ticket['customer_name']})" if ticket['customer_name'] else ""}
                
                **Description:** {ticket['description']}
                
                **Category:** {ticket['category'].replace('_', ' ').title() if ticket['category'] else 'Not categorized'}
                **Priority:** {ticket['priority'].title()}
                **Sentiment:** {ticket['sentiment'].title() if ticket['sentiment'] else 'Unknown'}
                **Tags:** {', '.join(ticket['tags']) if ticket['tags'] else 'None'}
                """)
                
                if ticket.get("auto_response"):
                    st.markdown(f"**Auto-Response:** {ticket['auto_response']}")
                
                if ticket.get("confidence_score"):
                    confidence = ticket["confidence_score"]
                    if confidence < 0.7:
                        st.warning(f"⚠️ Low confidence: {confidence:.2%}")
                    else:
                        st.success(f"✅ High confidence: {confidence:.2%}")
            
            with col2:
                st.markdown(f"**Created:** {ticket['created_at'][:10]}")
                st.markdown(f"**Updated:** {ticket['updated_at'][:10]}")
                
                # Action buttons
                if ticket["status"] == "open":
                    if st.button(f"Start Work", key=f"start_{ticket['id']}"):
                        update_ticket(ticket["id"], {"status": "in_progress"})
                        st.rerun()
                    
                    if st.button(f"Escalate", key=f"escalate_{ticket['id']}"):
                        reason = st.text_input("Escalation reason", key=f"reason_{ticket['id']}")
                        if reason:
                            escalate_ticket(ticket["id"], reason)
                            st.rerun()
                
                elif ticket["status"] == "in_progress":
                    resolution = st.text_area("Resolution", key=f"resolution_{ticket['id']}")
                    if st.button(f"Resolve", key=f"resolve_{ticket['id']}"):
                        if resolution:
                            resolve_ticket(ticket["id"], resolution)
                            st.rerun()
                        else:
                            st.error("Please provide a resolution")

def show_customer_portal():
    """Show customer portal for viewing their tickets"""
    st.header("👤 Customer Portal")
    
    customer_email = st.text_input("Enter your email to view your tickets")
    
    if customer_email:
        tickets = make_api_request(f"/customers/{customer_email}/tickets")
        
        if tickets:
            st.subheader(f"Your Tickets ({len(tickets)})")
            
            for ticket in tickets:
                priority_class = f"priority-{ticket['priority']}"
                st.markdown(f"""
                <div class="ticket-card {priority_class}">
                    <h4>#{ticket['id']} - {ticket['subject']}</h4>
                    <p><strong>Status:</strong> {ticket['status'].replace('_', ' ').title()}</p>
                    <p><strong>Priority:</strong> {ticket['priority'].title()}</p>
                    <p><strong>Description:</strong> {ticket['description']}</p>
                    <p><strong>Created:</strong> {ticket['created_at'][:10]}</p>
                    {f"<p><strong>Resolution:</strong> {ticket['resolution']}</p>" if ticket.get('resolution') else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tickets found for this email address")

def show_analytics():
    """Show detailed analytics"""
    st.header("📈 Analytics")
    
    # Get statistics
    stats = make_api_request("/statistics/")
    if not stats:
        st.error("Unable to load statistics")
        return
    
    # Time series analysis (simplified)
    st.subheader("Ticket Trends")
    
    # Create sample time series data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    ticket_counts = [stats["total_tickets"] // 365 + np.random.randint(-2, 3) for _ in range(len(dates))]
    
    df = pd.DataFrame({
        'Date': dates,
        'Tickets': ticket_counts
    })
    
    fig = px.line(df, x='Date', y='Tickets', title='Daily Ticket Volume')
    st.plotly_chart(fig, use_container_width=True)
    
    # Category analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Category Performance")
        category_data = stats["category_distribution"]
        if category_data:
            fig = px.bar(
                x=list(category_data.keys()),
                y=list(category_data.values()),
                title="Tickets by Category",
                color=list(category_data.values()),
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Priority Distribution")
        priority_data = stats["priority_distribution"]
        if priority_data:
            fig = px.pie(
                values=list(priority_data.values()),
                names=list(priority_data.keys()),
                title="Tickets by Priority"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_knowledge_base():
    """Show knowledge base management"""
    st.header("📚 Knowledge Base")
    
    # Add new knowledge entry
    with st.expander("Add New Knowledge Entry"):
        with st.form("knowledge_entry"):
            title = st.text_input("Title")
            content = st.text_area("Content")
            category = st.selectbox("Category", ["returns", "shipping", "payment", "damaged", "account", "technical"])
            tags = st.text_input("Tags (comma-separated)")
            
            if st.form_submit_button("Add Entry"):
                if title and content:
                    entry_data = {
                        "title": title,
                        "content": content,
                        "category": category,
                        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
                    }
                    
                    result = make_api_request("/knowledge-base/", method="POST", data=entry_data)
                    if result:
                        st.success("Knowledge base entry added successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in title and content")
    
    # View knowledge base
    st.subheader("Current Knowledge Base")
    knowledge_entries = make_api_request("/knowledge-base/")
    
    if knowledge_entries:
        for entry in knowledge_entries:
            with st.expander(f"{entry['title']} ({entry['category']})"):
                st.markdown(f"**Content:** {entry['content']}")
                st.markdown(f"**Tags:** {', '.join(entry['tags'])}")
                st.markdown(f"**Created:** {entry['created_at'][:10]}")
    else:
        st.info("No knowledge base entries found")

if __name__ == "__main__":
    main() 