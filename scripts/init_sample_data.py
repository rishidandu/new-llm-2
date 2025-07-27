#!/usr/bin/env python3
"""
Initialize sample data for the RAG system
Run this after deployment to populate the vector store with basic data
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from src.rag.rag_system import ASURAGSystem
from src.utils.data_processor import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_documents():
    """Create some sample ASU documents for the system"""
    sample_docs = [
        Document(
            content="Arizona State University (ASU) is a public research university located in the Phoenix metropolitan area. Founded in 1885, ASU is one of the largest universities in the United States by enrollment.",
            metadata={
                'source': 'asu_web',
                'title': 'About Arizona State University',
                'url': 'https://www.asu.edu/about',
                'type': 'general_info'
            }
        ),
        Document(
            content="ASU offers over 400 undergraduate degree programs and more than 450 graduate degree programs across 17 colleges and schools. The university is known for innovation and research excellence.",
            metadata={
                'source': 'asu_web',
                'title': 'ASU Academic Programs',
                'url': 'https://www.asu.edu/academics',
                'type': 'academics'
            }
        ),
        Document(
            content="The Tempe campus is ASU's main campus, home to over 50,000 students. It features state-of-the-art facilities including libraries, research centers, and student recreation areas.",
            metadata={
                'source': 'asu_web',
                'title': 'ASU Tempe Campus',
                'url': 'https://www.asu.edu/tempe',
                'type': 'campus_info'
            }
        ),
        Document(
            content="ASU is consistently ranked among the top universities for innovation. The university emphasizes practical learning, research opportunities, and preparing students for future careers.",
            metadata={
                'source': 'asu_web',
                'title': 'ASU Innovation and Rankings',
                'url': 'https://www.asu.edu/rankings',
                'type': 'rankings'
            }
        ),
        Document(
            content="Student life at ASU includes over 1,000 student organizations, Division I athletics (ASU Sun Devils), and numerous cultural and recreational activities throughout the year.",
            metadata={
                'source': 'asu_web',
                'title': 'ASU Student Life',
                'url': 'https://www.asu.edu/student-life',
                'type': 'student_life'
            }
        )
    ]
    return sample_docs

def initialize_system():
    """Initialize the RAG system with sample data"""
    try:
        logger.info("🚀 Initializing RAG system...")
        config = Config()
        rag_system = ASURAGSystem(config)
        
        logger.info("📝 Creating sample documents...")
        sample_docs = create_sample_documents()
        
        logger.info("🔤 Generating embeddings...")
        embeddings = []
        for doc in sample_docs:
            embedding = rag_system.embedding_gen.get_embedding(doc.content)
            embeddings.append(embedding)
        
        logger.info("💾 Adding documents to vector store...")
        rag_system.vector_store.add_documents(sample_docs, embeddings)
        
        logger.info(f"✅ Successfully initialized system with {len(sample_docs)} sample documents")
        
        # Test the system
        logger.info("🧪 Testing system with sample query...")
        result = rag_system.query("What is Arizona State University?")
        logger.info(f"Test query result: {result['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        return False

def main():
    """Main entry point"""
    logger.info("🎯 Starting sample data initialization...")
    
    if initialize_system():
        logger.info("🎉 Sample data initialization completed successfully!")
        print("\n✅ Your RAG system is ready!")
        print("🔗 You can now query the system via the API endpoints:")
        print("   - POST /query - Ask questions about ASU")
        print("   - GET /stats - View system statistics")
        print("   - GET /health - Health check")
    else:
        logger.error("💥 Sample data initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 