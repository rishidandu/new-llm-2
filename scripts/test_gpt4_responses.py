#!/usr/bin/env python3
"""Test script to demonstrate GPT-4 detailed responses"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import Dict, Any

def test_gpt4_query(question: str) -> Dict[str, Any]:
    """Test a query with the new GPT-4 configuration"""
    try:
        response = requests.post(
            'http://localhost:3000/query',
            json={'question': question},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    """Test various queries to demonstrate GPT-4 improvements"""
    
    test_questions = [
        "What are the best campus jobs for students at ASU?",
        "How do I get involved in research opportunities at ASU?",
        "What are the most popular dining options on campus?",
        "How difficult is the computer science program at ASU?",
        "What resources are available for international students?"
    ]
    
    print("🧪 Testing GPT-4 Enhanced Responses\n")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 40)
        
        result = test_gpt4_query(question)
        
        if result:
            answer = result.get('answer', 'No answer received')
            sources = result.get('sources', [])
            
            # Print the answer (truncated for readability)
            print(f"Answer: {answer[:300]}...")
            print(f"Sources found: {len(sources)}")
            
            if sources:
                print("Top source:", sources[0].get('title', 'No title'))
        else:
            print("❌ Failed to get response")
        
        print()

if __name__ == "__main__":
    main() 