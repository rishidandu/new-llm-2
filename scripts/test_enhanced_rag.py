#!/usr/bin/env python3
"""
Test script for the enhanced RAG system with intelligent query handling.
This demonstrates the new features like clarification questions, follow-up suggestions,
action items, and related topics.
"""

import sys
import os
import json
import requests
from typing import Dict, Any

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_enhanced_queries():
    """Test various queries to demonstrate enhanced functionality"""
    
    base_url = "http://localhost:3000"
    
    # Test queries that should trigger different enhancements
    test_queries = [
        "What are good campus jobs?",
        "Tell me about courses",
        "How do I find a professor?",
        "What's the best way to get help with classes?",
        "I need advice about internships",
        "What should I know about campus life?",
        "How do I apply for financial aid?",
        "What are some easy classes to take?"
    ]
    
    print("🧠 Testing Enhanced RAG System with Intelligent Query Handling")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/query",
                headers={"Content-Type": "application/json"},
                json={"question": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display confidence score
                confidence = result.get('confidence_score', 0)
                confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                print(f"{confidence_emoji} Confidence: {confidence:.1%}")
                
                # Display main answer
                print(f"🤖 Answer: {result.get('answer', 'No answer provided')[:200]}...")
                
                # Display clarification questions
                clarifications = result.get('clarification_questions', [])
                if clarifications:
                    print(f"🤔 Clarification Questions ({len(clarifications)}):")
                    for j, clarification in enumerate(clarifications, 1):
                        print(f"   {j}. {clarification['question']}")
                        print(f"      Options: {', '.join(clarification['options'][:3])}...")
                
                # Display follow-up questions
                follow_ups = result.get('follow_up_questions', [])
                if follow_ups:
                    print(f"💭 Follow-up Questions ({len(follow_ups)}):")
                    for j, question in enumerate(follow_ups[:2], 1):
                        print(f"   {j}. {question}")
                
                # Display action items
                actions = result.get('action_items', [])
                if actions:
                    print(f"✅ Action Items ({len(actions)}):")
                    for j, action in enumerate(actions[:3], 1):
                        print(f"   {j}. {action}")
                
                # Display related topics
                topics = result.get('related_topics', [])
                if topics:
                    print(f"🔗 Related Topics ({len(topics)}):")
                    for j, topic in enumerate(topics[:3], 1):
                        print(f"   {j}. {topic}")
                
                # Display source count
                sources = result.get('sources', [])
                print(f"📚 Sources: {len(sources)} found")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()  # Empty line for readability

def test_specific_scenarios():
    """Test specific scenarios that should trigger different enhancements"""
    
    base_url = "http://localhost:3000"
    
    print("\n🎯 Testing Specific Enhancement Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Vague Job Query",
            "query": "I want a good job",
            "expected_features": ["clarification_questions", "follow_up_questions", "action_items"]
        },
        {
            "name": "Course Information Query",
            "query": "Tell me about computer science classes",
            "expected_features": ["related_topics", "action_items", "follow_up_questions"]
        },
        {
            "name": "Professor Query",
            "query": "Who is the best professor?",
            "expected_features": ["clarification_questions", "related_topics"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 Scenario: {scenario['name']}")
        print(f"Query: {scenario['query']}")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                headers={"Content-Type": "application/json"},
                json={"question": scenario['query']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check which features were triggered
                triggered_features = []
                for feature in scenario['expected_features']:
                    if result.get(feature) and len(result[feature]) > 0:
                        triggered_features.append(feature)
                
                print(f"✅ Triggered Features: {', '.join(triggered_features)}")
                
                # Show a sample of the enhancement
                if 'clarification_questions' in triggered_features:
                    clar = result['clarification_questions'][0]
                    print(f"   Clarification: {clar['question']}")
                
                if 'action_items' in triggered_features:
                    action = result['action_items'][0]
                    print(f"   Action: {action}")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function to run all tests"""
    print("🚀 Starting Enhanced RAG System Tests")
    print("Make sure the server is running on http://localhost:3000")
    print()
    
    try:
        # Test basic connectivity
        response = requests.get("http://localhost:3000/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responsive")
        else:
            print("❌ Server responded with error")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:3000")
        return
    
    # Run tests
    test_enhanced_queries()
    test_specific_scenarios()
    
    print("\n🎉 Enhanced RAG System Testing Complete!")
    print("\nKey Features Demonstrated:")
    print("• 🤔 Intelligent clarification questions")
    print("• 💭 Relevant follow-up suggestions")
    print("• ✅ Actionable next steps")
    print("• 🔗 Related topics for exploration")
    print("• 📊 Confidence scoring")
    print("• 🎯 Context-aware responses")

if __name__ == "__main__":
    main() 