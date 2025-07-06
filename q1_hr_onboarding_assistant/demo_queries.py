#!/usr/bin/env python3
"""
Demo script for HR Onboarding Knowledge Assistant
This script demonstrates the system's capabilities with sample queries
"""

import requests
import json
import time
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_query(query: str, expected_category: str = None) -> Dict[str, Any]:
    """Test a single query and return the response"""
    try:
        print(f"\n🤔 Query: {query}")
        print("-" * 60)
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response received")
            print(f"📊 Category: {result['query_category']}")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"📄 Sources: {len(result['sources'])}")
            print(f"⏱️  Retrieved documents: {result['retrieved_documents_count']}")
            
            print(f"\n💬 Answer:")
            print(result['answer'])
            
            if result['sources']:
                print(f"\n📚 Sources:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['document_name']} - {source['section_title']}")
                    print(f"     Preview: {source['text_preview'][:100]}...")
            
            if expected_category and result['query_category'] != expected_category:
                print(f"⚠️  Expected category: {expected_category}, got: {result['query_category']}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start with: python run_api.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def run_demo_queries():
    """Run a series of demo queries to showcase the system"""
    
    print("🏢 HR Onboarding Knowledge Assistant - Demo")
    print("=" * 60)
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ API server is not healthy. Please start the server first.")
            return
        print("✅ API server is running and healthy")
    except:
        print("❌ API server not running. Please start with: python run_api.py")
        return
    
    # Demo queries organized by category
    demo_queries = [
        # Leave Policy Queries
        {
            "query": "How many vacation days do I get as a new employee?",
            "category": "leave_policy",
            "description": "Basic vacation policy question"
        },
        {
            "query": "What's the process for requesting parental leave?",
            "category": "leave_policy", 
            "description": "Parental leave procedure"
        },
        {
            "query": "How do I request sick leave and what documentation do I need?",
            "category": "leave_policy",
            "description": "Sick leave requirements"
        },
        
        # Benefits Queries
        {
            "query": "How do I enroll in health insurance?",
            "category": "benefits",
            "description": "Health insurance enrollment"
        },
        {
            "query": "What dental coverage is available and what does it cover?",
            "category": "benefits",
            "description": "Dental benefits details"
        },
        {
            "query": "Are there vision benefits and how much do they cover?",
            "category": "benefits",
            "description": "Vision benefits information"
        },
        
        # Work Arrangement Queries
        {
            "query": "Can I work remotely and what are the guidelines?",
            "category": "work_arrangement",
            "description": "Remote work policy"
        },
        {
            "query": "What's the hybrid work policy and core hours?",
            "category": "work_arrangement",
            "description": "Hybrid work arrangements"
        },
        {
            "query": "What are the standard office hours and can I have flexible scheduling?",
            "category": "work_arrangement",
            "description": "Office hours and flexibility"
        },
        
        # Conduct Queries
        {
            "query": "What's the dress code policy for the office?",
            "category": "conduct",
            "description": "Dress code requirements"
        },
        {
            "query": "What are the social media guidelines for employees?",
            "category": "conduct",
            "description": "Social media policy"
        },
        {
            "query": "How do I report workplace issues or concerns?",
            "category": "conduct",
            "description": "Reporting procedures"
        },
        
        # Compensation Queries
        {
            "query": "How often are performance reviews conducted?",
            "category": "compensation",
            "description": "Performance review schedule"
        },
        {
            "query": "What's the bonus structure and when are bonuses paid?",
            "category": "compensation",
            "description": "Bonus information"
        },
        {
            "query": "How do I request a salary review outside the annual cycle?",
            "category": "compensation",
            "description": "Salary review process"
        },
        
        # General Queries
        {
            "query": "How do I access the employee portal?",
            "category": "general",
            "description": "Portal access"
        },
        {
            "query": "What's the onboarding process for new employees?",
            "category": "general",
            "description": "Onboarding overview"
        },
        {
            "query": "Who should I contact for HR questions?",
            "category": "general",
            "description": "HR contact information"
        }
    ]
    
    # Run queries by category
    categories = ["leave_policy", "benefits", "work_arrangement", "conduct", "compensation", "general"]
    
    for category in categories:
        print(f"\n{'='*20} {category.upper().replace('_', ' ')} {'='*20}")
        
        category_queries = [q for q in demo_queries if q["category"] == category]
        
        for query_info in category_queries:
            print(f"\n📋 {query_info['description']}")
            result = test_query(query_info["query"], query_info["category"])
            
            if result:
                # Add a small delay between queries
                time.sleep(1)
            else:
                print("⏭️  Skipping remaining queries due to error")
                break

def test_edge_cases():
    """Test edge cases and error handling"""
    print(f"\n{'='*20} EDGE CASES {'='*20}")
    
    edge_queries = [
        {
            "query": "What's the policy on unicorns in the office?",
            "description": "Non-existent policy query"
        },
        {
            "query": "",
            "description": "Empty query"
        },
        {
            "query": "a" * 1000,  # Very long query
            "description": "Very long query"
        },
        {
            "query": "What's the policy on vacation days and health insurance and remote work and dress code?",
            "description": "Multi-topic query"
        }
    ]
    
    for query_info in edge_queries:
        print(f"\n📋 {query_info['description']}")
        test_query(query_info["query"])

def test_suggestions():
    """Test the suggestions endpoint"""
    print(f"\n{'='*20} SUGGESTIONS {'='*20}")
    
    try:
        # Get all suggestions
        response = requests.get(f"{API_BASE_URL}/suggestions")
        if response.status_code == 200:
            suggestions = response.json()
            print(f"✅ Got {len(suggestions['questions'])} general suggestions")
            
            # Get category-specific suggestions
            categories = ["leave_policy", "benefits", "work_arrangement"]
            for category in categories:
                response = requests.get(f"{API_BASE_URL}/suggestions?category={category}")
                if response.status_code == 200:
                    cat_suggestions = response.json()
                    print(f"✅ {category}: {len(cat_suggestions['questions'])} suggestions")
                    
        else:
            print(f"❌ Error getting suggestions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing suggestions: {e}")

def main():
    """Run the complete demo"""
    print("🎬 Starting HR Onboarding Assistant Demo")
    print("Make sure you have uploaded some HR documents first!")
    print("=" * 60)
    
    # Run main demo queries
    run_demo_queries()
    
    # Test edge cases
    test_edge_cases()
    
    # Test suggestions
    test_suggestions()
    
    print(f"\n{'='*20} DEMO COMPLETE {'='*20}")
    print("🎉 Demo completed! The system is working correctly.")
    print("💡 Try uploading your own HR documents and asking custom questions!")

if __name__ == "__main__":
    main() 