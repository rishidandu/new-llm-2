#!/usr/bin/env python3
"""
Test script to verify Qdrant Cloud connection and basic functionality
"""

import sys
import os
import logging
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.qdrant_vector_store import QdrantVectorStore
from src.utils.data_processor import Document

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test basic connection to Qdrant Cloud"""
    logger.info("🔌 Testing Qdrant Cloud connection...")
    
    try:
        # Create test collection
        test_store = QdrantVectorStore(
            collection_name="test_connection"
        )
        
        logger.info("✅ Successfully connected to Qdrant Cloud!")
        
        # Get initial stats
        stats = test_store.get_stats()
        logger.info(f"Collection stats: {stats}")
        
        return test_store
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant Cloud: {e}")
        return None

def test_basic_operations(store: QdrantVectorStore):
    """Test basic CRUD operations"""
    logger.info("🧪 Testing basic operations...")
    
    try:
        # Create test documents
        test_docs = [
            Document(
                id="test_doc_1",
                content="This is a test document about artificial intelligence and machine learning.",
                metadata={"topic": "AI"},
                source="test"
            ),
            Document(
                id="test_doc_2", 
                content="Arizona State University offers excellent computer science programs.",
                metadata={"topic": "Education"},
                source="test"
            )
        ]
        
        # Create dummy embeddings (1536 dimensions for OpenAI text-embedding-3-small)
        embeddings = [
            [0.1] * 1536,  # Simple dummy embedding
            [0.2] * 1536   # Another dummy embedding
        ]
        
        # Test adding documents
        logger.info("Adding test documents...")
        store.add_documents(test_docs, embeddings)
        
        # Test getting stats
        stats = store.get_stats()
        logger.info(f"After adding documents: {stats}")
        
        # Test search functionality
        logger.info("Testing search...")
        query_embedding = [0.15] * 1536  # Query embedding between the two test embeddings
        
        results = store.search(query_embedding, top_k=2)
        logger.info(f"Search returned {len(results)} results")
        
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: Score={result['score']:.4f}, Content='{result['content'][:50]}...'")
        
        logger.info("✅ Basic operations test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic operations test failed: {e}")
        return False

def cleanup_test_collection(store: QdrantVectorStore):
    """Clean up test collection"""
    logger.info("🧹 Cleaning up test collection...")
    
    try:
        store.delete_collection()
        logger.info("✅ Test collection cleaned up successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clean up test collection: {e}")

def verify_environment():
    """Verify required environment variables"""
    logger.info("🔍 Verifying environment variables...")
    
    required_vars = ['QDRANT_URL', 'QDRANT_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask API key for logging
            if 'API_KEY' in var:
                masked_value = value[:8] + '*' * (len(value) - 8)
                logger.info(f"✅ {var}: {masked_value}")
            else:
                logger.info(f"✅ {var}: {value}")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("\nPlease add them to your .env file:")
        logger.error("QDRANT_URL=https://your-cluster.qdrant.tech")
        logger.error("QDRANT_API_KEY=your-api-key")
        logger.error("\nTo get these credentials:")
        logger.error("1. Sign up at https://cloud.qdrant.io/")
        logger.error("2. Create a new cluster")
        logger.error("3. Get the URL and API key from the cluster details")
        return False
    
    return True

def main():
    """Main test function"""
    logger.info("🚀 Starting Qdrant Cloud connection test...")
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Test connection
    store = test_connection()
    if not store:
        sys.exit(1)
    
    # Test basic operations
    if test_basic_operations(store):
        logger.info("🎉 All tests passed! Qdrant Cloud is ready to use.")
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        cleanup_test_collection(store)
        sys.exit(1)
    
    # Clean up
    cleanup_test_collection(store)
    
    logger.info("\n🎯 Next steps:")
    logger.info("1. Run the migration script: python scripts/migrate_to_qdrant.py")
    logger.info("2. Update your RAG system configuration to use Qdrant")
    logger.info("3. Test your RAG system with some queries")

if __name__ == "__main__":
    main() 