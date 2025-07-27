#!/usr/bin/env python3
"""
Test script to verify ASU grades data integration with RAG system.
This script will:
1. Load the RAG system with grades data
2. Test various queries about grades and professors
3. Display results
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from src.rag.rag_system import ASURAGSystem

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_grades_queries(rag_system):
    """Test various queries related to grades and professors"""
    
    test_queries = [
        # Course-specific queries
        "What is the average grade for MAT 210?",
        "How many students took ACCT 2301 in Fall 2024?",
        "What is the pass rate for CS 110?",
        
        # Professor queries
        "Who teaches ACCT 2301?",
        "What is the rating for Professor Huang?",
        "Which professors have the highest ratings?",
        
        # Grade distribution queries
        "What is the grade distribution for MAT 210?",
        "Which courses have the highest pass rates?",
        "What are the most difficult courses based on grades?",
        
        # Semester queries
        "How do grades compare between Fall 2023 and Fall 2024?",
        "What courses were offered in Spring 2024?",
        
        # General queries
        "What information do you have about ASU course grades?",
        "Can you tell me about professor ratings and course difficulty?",
    ]
    
    print("\n" + "="*80)
    print("TESTING ASU GRADES RAG SYSTEM")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 60)
        
        try:
            result = rag_system.query(query, top_k=3)
            
            print(f"Answer: {result['answer']}")
            
            if result['sources']:
                print(f"\nSources found: {len(result['sources'])}")
                for j, source in enumerate(result['sources'][:2], 1):  # Show first 2 sources
                    print(f"  Source {j}: {source['content'][:200]}...")
            
            print()
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print()

def main():
    """Main test function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ASU grades RAG system test...")
    
    # Load configuration
    config = Config()
    
    # Initialize RAG system
    rag_system = ASURAGSystem(config)
    
    # Test the system with grades data
    test_grades_queries(rag_system)
    
    logger.info("Test completed!")

if __name__ == "__main__":
    main() 