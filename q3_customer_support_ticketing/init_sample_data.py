import requests
import json
from datetime import datetime, timedelta
import random

# Configuration
API_BASE_URL = "http://localhost:8000"

def create_sample_ticket(ticket_data):
    """Create a sample ticket"""
    try:
        response = requests.post(f"{API_BASE_URL}/tickets/", json=ticket_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating ticket: {e}")
        return None

def create_sample_customer(customer_data):
    """Create a sample customer"""
    try:
        response = requests.post(f"{API_BASE_URL}/customers/", json=customer_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating customer: {e}")
        return None

def init_sample_data():
    """Initialize the system with sample data"""
    
    print("🚀 Initializing Customer Support System with Sample Data...")
    
    # Sample customers
    customers = [
        {
            "email": "john.doe@example.com",
            "name": "John Doe",
            "phone": "+1-555-0101",
            "address": "123 Main St, Anytown, USA"
        },
        {
            "email": "jane.smith@example.com", 
            "name": "Jane Smith",
            "phone": "+1-555-0102",
            "address": "456 Oak Ave, Somewhere, USA"
        },
        {
            "email": "bob.wilson@example.com",
            "name": "Bob Wilson",
            "phone": "+1-555-0103",
            "address": "789 Pine Rd, Elsewhere, USA"
        },
        {
            "email": "alice.brown@example.com",
            "name": "Alice Brown",
            "phone": "+1-555-0104",
            "address": "321 Elm St, Nowhere, USA"
        },
        {
            "email": "charlie.davis@example.com",
            "name": "Charlie Davis",
            "phone": "+1-555-0105",
            "address": "654 Maple Dr, Anywhere, USA"
        }
    ]
    
    # Create customers
    print("📝 Creating sample customers...")
    for customer in customers:
        result = create_sample_customer(customer)
        if result:
            print(f"✅ Created customer: {customer['name']}")
        else:
            print(f"❌ Failed to create customer: {customer['name']}")
    
    # Sample historical tickets
    sample_tickets = [
        {
            "subject": "Order hasn't arrived",
            "description": "I placed an order on March 15th and it still hasn't arrived. The tracking shows it was delivered but I never received it. Order number: ORD-2024-001",
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe"
        },
        {
            "subject": "Want to return this product",
            "description": "I received the wrong size and would like to return it for a refund. The product is in original condition with all packaging. Order number: ORD-2024-002",
            "customer_email": "jane.smith@example.com",
            "customer_name": "Jane Smith"
        },
        {
            "subject": "Payment failed but money deducted",
            "description": "I tried to place an order but the payment failed. However, I can see that $89.99 was deducted from my account. Transaction ID: TXN-2024-001",
            "customer_email": "bob.wilson@example.com",
            "customer_name": "Bob Wilson"
        },
        {
            "subject": "Product damaged during delivery",
            "description": "The package arrived with visible damage and the product inside is broken. I took photos as requested. Order number: ORD-2024-003",
            "customer_email": "alice.brown@example.com",
            "customer_name": "Alice Brown"
        },
        {
            "subject": "Can't log into my account",
            "description": "I'm trying to log into my account but keep getting an error message. I've tried resetting my password but it's not working. Email: charlie.davis@example.com",
            "customer_email": "charlie.davis@example.com",
            "customer_name": "Charlie Davis"
        },
        {
            "subject": "Website not loading properly",
            "description": "The website is very slow and some pages don't load at all. I'm using Chrome browser on Windows 10. This has been happening for the past 2 days.",
            "customer_email": "john.doe@example.com",
            "customer_name": "John Doe"
        },
        {
            "subject": "Need refund for cancelled order",
            "description": "I cancelled my order within the cancellation window but haven't received my refund yet. It's been 5 business days. Order number: ORD-2024-004",
            "customer_email": "jane.smith@example.com",
            "customer_name": "Jane Smith"
        },
        {
            "subject": "Shipping address change request",
            "description": "I need to change the shipping address for my order. I moved to a new apartment. Order number: ORD-2024-005",
            "customer_email": "bob.wilson@example.com",
            "customer_name": "Bob Wilson"
        },
        {
            "subject": "Product quality issue",
            "description": "The product I received doesn't match the description on the website. The quality is much lower than advertised. Order number: ORD-2024-006",
            "customer_email": "alice.brown@example.com",
            "customer_name": "Alice Brown"
        },
        {
            "subject": "Account security concern",
            "description": "I received an email about suspicious activity on my account. I want to make sure my account is secure and change my password.",
            "customer_email": "charlie.davis@example.com",
            "customer_name": "Charlie Davis"
        }
    ]
    
    # Create tickets
    print("🎫 Creating sample tickets...")
    for i, ticket in enumerate(sample_tickets):
        result = create_sample_ticket(ticket)
        if result:
            print(f"✅ Created ticket #{result['id']}: {ticket['subject']}")
            
            # Randomly resolve some tickets
            if i < 7:  # Resolve first 7 tickets
                resolution_texts = [
                    "Issue resolved by providing tracking information and arranging redelivery.",
                    "Return processed successfully. Refund issued within 3 business days.",
                    "Payment issue investigated and refund processed. Apologies for the inconvenience.",
                    "Replacement product shipped with expedited delivery. Original packaging returned.",
                    "Account access restored after password reset. Security measures reviewed.",
                    "Website performance issues resolved. Technical team implemented fixes.",
                    "Refund processed for cancelled order. Confirmation email sent."
                ]
                
                # Simulate resolution
                import time
                time.sleep(1)  # Small delay to avoid rate limiting
                
                try:
                    resolution_response = requests.post(
                        f"{API_BASE_URL}/tickets/{result['id']}/resolve",
                        json={"resolution": resolution_texts[i]}
                    )
                    if resolution_response.status_code == 200:
                        print(f"   ✅ Ticket #{result['id']} resolved")
                except:
                    pass
        else:
            print(f"❌ Failed to create ticket: {ticket['subject']}")
    
    print("\n🎉 Sample data initialization completed!")
    print("\n📊 System Statistics:")
    
    # Get statistics
    try:
        stats_response = requests.get(f"{API_BASE_URL}/statistics/")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   Total Tickets: {stats['total_tickets']}")
            print(f"   Open Tickets: {stats['open_tickets']}")
            print(f"   Categories: {len(stats['category_distribution'])}")
            print(f"   Priorities: {len(stats['priority_distribution'])}")
    except:
        print("   Unable to retrieve statistics")
    
    print("\n🚀 You can now:")
    print("   1. Start the Streamlit app: streamlit run streamlit_app.py")
    print("   2. Access the API at: http://localhost:8000")
    print("   3. View API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    init_sample_data() 