#!/usr/bin/env python3
"""
Test script to verify ASU grades data processing without embeddings.
This will test the data processing pipeline and show sample documents.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asu_grades_processor import ASUGradesProcessor

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main test function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Testing ASU grades data processing...")
    
    # Initialize processor
    grades_processor = ASUGradesProcessor()
    
    # Process all grades data
    logger.info("Processing ASU grades data...")
    documents = list(grades_processor.process_all_grades_data())
    
    if not documents:
        logger.error("No documents generated from grades data")
        return
    
    logger.info(f"Generated {len(documents)} documents from grades data")
    
    # Separate course and professor documents
    course_docs = [doc for doc in documents if doc.source == 'asu_grades']
    professor_docs = [doc for doc in documents if doc.source == 'asu_grades_professors']
    
    logger.info(f"Course documents: {len(course_docs)}")
    logger.info(f"Professor documents: {len(professor_docs)}")
    
    # Show sample course documents
    print("\n" + "="*80)
    print("SAMPLE COURSE DOCUMENTS")
    print("="*80)
    
    for i, doc in enumerate(course_docs[:3], 1):
        print(f"\n{i}. Course Document:")
        print("-" * 60)
        print(f"ID: {doc.id}")
        print(f"Source: {doc.source}")
        print(f"Content:\n{doc.content}")
        print(f"Metadata keys: {list(doc.metadata.keys())}")
        print()
    
    # Show sample professor documents
    print("\n" + "="*80)
    print("SAMPLE PROFESSOR DOCUMENTS")
    print("="*80)
    
    for i, doc in enumerate(professor_docs[:3], 1):
        print(f"\n{i}. Professor Document:")
        print("-" * 60)
        print(f"ID: {doc.id}")
        print(f"Source: {doc.source}")
        print(f"Content:\n{doc.content}")
        print(f"Metadata keys: {list(doc.metadata.keys())}")
        print()
    
    # Show statistics
    print("\n" + "="*80)
    print("DATA STATISTICS")
    print("="*80)
    
    # Course statistics
    if course_docs:
        subjects = set(doc.metadata.get('subject', '') for doc in course_docs)
        semesters = set(doc.metadata.get('semester', '') for doc in course_docs)
        years = set(doc.metadata.get('year', '') for doc in course_docs)
        
        print(f"Unique subjects: {len(subjects)}")
        print(f"Sample subjects: {list(subjects)[:10]}")
        print(f"Semesters: {sorted(semesters)}")
        print(f"Years: {sorted(years)}")
        
        # Show some grade statistics
        avg_grades = [doc.metadata.get('average_grade', 0) for doc in course_docs if doc.metadata.get('average_grade') != 'N/A']
        if avg_grades:
            print(f"Average grade range: {min(avg_grades):.2f} - {max(avg_grades):.2f}")
        
        pass_rates = [doc.metadata.get('pass_rate', 0) for doc in course_docs]
        if pass_rates:
            print(f"Pass rate range: {min(pass_rates):.1f}% - {max(pass_rates):.1f}%")
    
    # Professor statistics
    if professor_docs:
        departments = set(doc.metadata.get('department', '') for doc in professor_docs if doc.metadata.get('department'))
        print(f"Unique departments: {len(departments)}")
        print(f"Sample departments: {list(departments)[:10]}")
        
        ratings = [doc.metadata.get('quality_rating', 0) for doc in professor_docs if doc.metadata.get('quality_rating')]
        if ratings:
            print(f"Professor rating range: {min(ratings):.1f} - {max(ratings):.1f}")
    
    logger.info("Data processing test completed successfully!")

if __name__ == "__main__":
    main() 