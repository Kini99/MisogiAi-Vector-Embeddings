#!/usr/bin/env python3
"""
Demo script for the Intelligent Customer Support System
Showcases the RAG pipeline with example tickets and responses
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_ticket_analysis():
    """Demo ticket analysis capabilities"""
    print_header("Ticket Analysis Demo")
    
    # Example tickets for analysis
    demo_tickets = [
        {
            "subject": "My order hasn't arrived",
            "description": "I placed an order on March 15th and it still hasn't arrived. The tracking shows it was delivered but I never received it. Order number: ORD-2024-001"
        },
        {
            "subject": "Want to return this product",
            "description": "I received the wrong size and would like to return it for a refund. The product is in original condition with all packaging. Order number: ORD-2024-002"
        },
        {
            "subject": "Payment failed but money deducted",
            "description": "I tried to place an order but the payment failed. However, I can see that $89.99 was deducted from my account. Transaction ID: TXN-2024-001"
        },
        {
            "subject": "Product damaged during delivery",
            "description": "The package arrived with visible damage and the product inside is broken. I took photos as requested. Order number: ORD-2024-003"
        },
        {
            "subject": "Can't log into my account",
            "description": "I'm trying to log into my account but keep getting an error message. I've tried resetting my password but it's not working. Email: charlie.davis@example.com"
        }
    ]
    
    for i, ticket in enumerate(demo_tickets, 1):
        print_section(f"Ticket {i}: {ticket['subject']}")
        print(f"Description: {ticket['description']}")
        
        # Analyze ticket
        try:
            analysis_response = requests.post(
                f"{API_BASE_URL}/analyze-ticket/",
                json={"subject": ticket['subject'], "description": ticket['description']}
            )
            
            if analysis_response.status_code == 200:
                analysis = analysis_response.json()
                print(f"✅ Category: {analysis['category'].replace('_', ' ').title()}")
                print(f"✅ Priority: {analysis['priority'].title()}")
                print(f"✅ Sentiment: {analysis['sentiment'].title()}")
                print(f"✅ Tags: {', '.join(analysis['tags'])}")
                print(f"✅ Confidence: {analysis['confidence_score']:.2%}")
                print(f"✅ Escalation Needed: {'Yes' if analysis['escalation_needed'] else 'No'}")
            else:
                print("❌ Analysis failed")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        
        print()

def demo_response_generation():
    """Demo response generation capabilities"""
    print_header("Response Generation Demo")
    
    # Example ticket for response generation
    ticket = {
        "subject": "Payment failed but money deducted",
        "description": "I tried to place an order but the payment failed. However, I can see that $89.99 was deducted from my account. Transaction ID: TXN-2024-001"
    }
    
    print_section("Example Ticket")
    print(f"Subject: {ticket['subject']}")
    print(f"Description: {ticket['description']}")
    
    # Generate response
    try:
        response_data = requests.post(
            f"{API_BASE_URL}/generate-response/",
            json={
                "subject": ticket['subject'],
                "description": ticket['description'],
                "category": "payment_problem"
            }
        )
        
        if response_data.status_code == 200:
            response = response_data.json()
            print_section("Generated Response")
            print(f"Response: {response['response_text']}")
            print(f"Confidence: {response['confidence_score']:.2%}")
            print(f"Escalation Suggested: {'Yes' if response['suggested_escalation'] else 'No'}")
            
            if response['similar_tickets']:
                print_section("Similar Historical Tickets")
                for i, similar in enumerate(response['similar_tickets'][:3], 1):
                    print(f"{i}. Ticket #{similar['ticket_id']}: {similar['subject']}")
                    print(f"   Similarity: {similar['similarity_score']:.2%}")
                    if similar.get('resolution'):
                        print(f"   Resolution: {similar['resolution']}")
                    print()
            
            if response['knowledge_base_references']:
                print_section("Knowledge Base References")
                for ref in response['knowledge_base_references']:
                    print(f"• {ref}")
                    
        else:
            print("❌ Response generation failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def demo_similarity_search():
    """Demo similarity search capabilities"""
    print_header("Similarity Search Demo")
    
    # Example queries
    queries = [
        "My order is late and I need it urgently",
        "The product I received is broken",
        "I want to cancel my order and get a refund"
    ]
    
    for i, query in enumerate(queries, 1):
        print_section(f"Query {i}: {query}")
        
        try:
            similar_response = requests.get(
                f"{API_BASE_URL}/similar-tickets/",
                params={"subject": query, "description": query, "limit": 3}
            )
            
            if similar_response.status_code == 200:
                similar_tickets = similar_response.json()
                if similar_tickets:
                    for j, ticket in enumerate(similar_tickets, 1):
                        print(f"{j}. Ticket #{ticket['ticket_id']}: {ticket['subject']}")
                        print(f"   Similarity: {ticket['similarity_score']:.2%}")
                        print(f"   Category: {ticket.get('category', 'Unknown')}")
                        if ticket.get('resolution'):
                            print(f"   Resolution: {ticket['resolution']}")
                        print()
                else:
                    print("No similar tickets found")
            else:
                print("❌ Similarity search failed")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")

def demo_system_statistics():
    """Demo system statistics and analytics"""
    print_header("System Statistics Demo")
    
    try:
        # Get dashboard data
        dashboard_response = requests.get(f"{API_BASE_URL}/dashboard/")
        
        if dashboard_response.status_code == 200:
            dashboard = dashboard_response.json()
            
            print_section("Key Metrics")
            stats = dashboard['statistics']
            print(f"📊 Total Tickets: {stats['total_tickets']}")
            print(f"📊 Open Tickets: {stats['open_tickets']}")
            print(f"📊 Average Response Time: {dashboard['average_response_time_hours']} hours")
            
            # Calculate resolution rate
            resolved = dashboard['status_distribution'].get('resolved', 0)
            total = stats['total_tickets']
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            print(f"📊 Resolution Rate: {resolution_rate:.1f}%")
            
            print_section("Category Distribution")
            for category, count in stats['category_distribution'].items():
                print(f"• {category.replace('_', ' ').title()}: {count}")
            
            print_section("Priority Distribution")
            for priority, count in stats['priority_distribution'].items():
                print(f"• {priority.title()}: {count}")
            
            print_section("Status Distribution")
            for status, count in dashboard['status_distribution'].items():
                print(f"• {status.replace('_', ' ').title()}: {count}")
                
        else:
            print("❌ Failed to retrieve dashboard data")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def demo_ticket_lifecycle():
    """Demo complete ticket lifecycle"""
    print_header("Ticket Lifecycle Demo")
    
    # Create a new ticket
    print_section("1. Creating New Ticket")
    new_ticket = {
        "subject": "Demo ticket for testing",
        "description": "This is a demo ticket to test the system capabilities. I have a question about my recent order.",
        "customer_email": "demo@example.com",
        "customer_name": "Demo User"
    }
    
    try:
        create_response = requests.post(f"{API_BASE_URL}/tickets/", json=new_ticket)
        
        if create_response.status_code == 201:
            ticket = create_response.json()
            ticket_id = ticket['id']
            print(f"✅ Ticket created with ID: {ticket_id}")
            print(f"✅ Auto-categorized as: {ticket['category'].replace('_', ' ').title()}")
            print(f"✅ Priority assigned: {ticket['priority'].title()}")
            print(f"✅ Confidence score: {ticket['confidence_score']:.2%}")
            
            if ticket.get('auto_response'):
                print(f"✅ Auto-response generated: {ticket['auto_response'][:100]}...")
            
            # Update ticket status
            print_section("2. Updating Ticket Status")
            update_data = {"status": "in_progress"}
            update_response = requests.put(f"{API_BASE_URL}/tickets/{ticket_id}", json=update_data)
            
            if update_response.status_code == 200:
                print("✅ Ticket status updated to 'in_progress'")
            
            # Resolve ticket
            print_section("3. Resolving Ticket")
            resolution = "Demo ticket resolved successfully. Customer inquiry addressed."
            resolve_response = requests.post(
                f"{API_BASE_URL}/tickets/{ticket_id}/resolve",
                json={"resolution": resolution}
            )
            
            if resolve_response.status_code == 200:
                print("✅ Ticket resolved successfully")
            
            # Get final ticket status
            final_response = requests.get(f"{API_BASE_URL}/tickets/{ticket_id}")
            if final_response.status_code == 200:
                final_ticket = final_response.json()
                print(f"✅ Final status: {final_ticket['status']}")
                if final_ticket.get('resolution'):
                    print(f"✅ Resolution: {final_ticket['resolution']}")
                    
        else:
            print("❌ Failed to create ticket")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

def check_api_health():
    """Check if the API is running"""
    try:
        health_response = requests.get(f"{API_BASE_URL}/health/")
        if health_response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def main():
    """Main demo function"""
    print("🎫 Intelligent Customer Support System - Demo")
    print("=" * 60)
    
    # Check API health
    print("🔍 Checking API health...")
    if not check_api_health():
        print("❌ API is not running. Please start the API server first:")
        print("   python api.py")
        return
    
    print("✅ API is running and healthy!")
    
    # Run demos
    demo_ticket_analysis()
    demo_response_generation()
    demo_similarity_search()
    demo_system_statistics()
    demo_ticket_lifecycle()
    
    print_header("Demo Complete")
    print("🎉 All demos completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Start the Streamlit frontend: streamlit run streamlit_app.py")
    print("2. Explore the web interface at http://localhost:8501")
    print("3. View API documentation at http://localhost:8000/docs")
    print("4. Try submitting your own tickets and see the AI in action!")

if __name__ == "__main__":
    main() 