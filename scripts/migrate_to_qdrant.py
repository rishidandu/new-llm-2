#!/usr/bin/env python3
"""
Migration script to transfer embeddings from ChromaDB to Qdrant Cloud
"""

import sys
import os
import logging
from typing import List, Dict, Any
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.vector_store import VectorStore
from src.rag.qdrant_vector_store import QdrantVectorStore
from src.utils.data_processor import Document
from config.settings import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_environment():
    """Verify required environment variables are set"""
    required_vars = ['QDRANT_URL', 'QDRANT_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set them in your .env file:")
        logger.error("QDRANT_URL=https://your-cluster.qdrant.tech")
        logger.error("QDRANT_API_KEY=your-api-key")
        return False
    
    return True

def get_all_documents_from_chromadb(chroma_store: VectorStore) -> List[Dict[str, Any]]:
    """Extract all documents and their embeddings from ChromaDB"""
    logger.info("Extracting all documents from ChromaDB...")
    
    try:
        # Get all documents from the collection
        collection = chroma_store.collection
        
        # Get total count first
        total_count = collection.count()
        logger.info(f"Found {total_count} documents in ChromaDB")
        
        if total_count == 0:
            logger.warning("No documents found in ChromaDB")
            return []
        
        # Get all documents in batches
        all_results = []
        batch_size = 1000
        
        for offset in tqdm(range(0, total_count, batch_size), desc="Extracting batches"):
            try:
                # Get batch of documents
                batch_result = collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=['documents', 'metadatas', 'embeddings']
                )
                
                # Process batch
                if batch_result['documents']:
                    for i in range(len(batch_result['documents'])):
                        doc_data = {
                            'id': batch_result['ids'][i],
                            'content': batch_result['documents'][i],
                            'metadata': batch_result['metadatas'][i],
                            'embedding': batch_result['embeddings'][i]
                        }
                        all_results.append(doc_data)
                        
            except Exception as e:
                logger.error(f"Error extracting batch at offset {offset}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(all_results)} documents from ChromaDB")
        return all_results
        
    except Exception as e:
        logger.error(f"Error extracting documents from ChromaDB: {e}")
        return []

def migrate_documents_to_qdrant(documents_data: List[Dict[str, Any]], qdrant_store: QdrantVectorStore):
    """Migrate documents to Qdrant"""
    logger.info(f"Migrating {len(documents_data)} documents to Qdrant...")
    
    # Convert to Document objects
    documents = []
    embeddings = []
    
    for doc_data in documents_data:
        # Extract source from metadata if it exists, otherwise use 'unknown'
        source = doc_data['metadata'].get('source', 'unknown')
        
        doc = Document(
            id=doc_data['id'],
            content=doc_data['content'],
            metadata=doc_data['metadata'],
            source=source
        )
        documents.append(doc)
        embeddings.append(doc_data['embedding'])
    
    # Add to Qdrant
    qdrant_store.add_documents(documents, embeddings)
    logger.info("Migration to Qdrant completed!")

def verify_migration(chroma_store: VectorStore, qdrant_store: QdrantVectorStore):
    """Verify the migration was successful"""
    logger.info("Verifying migration...")
    
    # Get stats from both stores
    chroma_stats = chroma_store.get_stats()
    qdrant_stats = qdrant_store.get_stats()
    
    logger.info(f"ChromaDB documents: {chroma_stats['total_documents']}")
    logger.info(f"Qdrant documents: {qdrant_stats['total_documents']}")
    
    if chroma_stats['total_documents'] == qdrant_stats['total_documents']:
        logger.info("✅ Migration verification successful! Document counts match.")
        return True
    else:
        logger.error("❌ Migration verification failed! Document counts don't match.")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting ChromaDB to Qdrant migration...")
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    try:
        # Initialize ChromaDB store
        logger.info("Connecting to ChromaDB...")
        chroma_store = VectorStore(
            collection_name=Config.COLLECTION_NAME,
            db_path=Config.VECTOR_DB_PATH
        )
        
        # Initialize Qdrant store
        logger.info("Connecting to Qdrant Cloud...")
        qdrant_store = QdrantVectorStore(
            collection_name=Config.COLLECTION_NAME
        )
        
        # Check if Qdrant collection already exists and has data
        qdrant_stats = qdrant_store.get_stats()
        if qdrant_stats['total_documents'] > 0:
            logger.warning(f"Qdrant collection already contains {qdrant_stats['total_documents']} documents")
            response = input("Do you want to proceed and overwrite? (y/N): ")
            if response.lower() != 'y':
                logger.info("Migration cancelled by user")
                return
            
            # Delete existing collection
            logger.info("Deleting existing Qdrant collection...")
            qdrant_store.delete_collection()
            
            # Recreate collection
            qdrant_store = QdrantVectorStore(
                collection_name=Config.COLLECTION_NAME
            )
        
        # Extract documents from ChromaDB
        documents_data = get_all_documents_from_chromadb(chroma_store)
        
        if not documents_data:
            logger.error("No documents to migrate")
            return
        
        # Migrate to Qdrant
        migrate_documents_to_qdrant(documents_data, qdrant_store)
        
        # Verify migration
        if verify_migration(chroma_store, qdrant_store):
            logger.info("🎉 Migration completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Update your RAG system to use QdrantVectorStore")
            logger.info("2. Test the system with a few queries")
            logger.info("3. Consider backing up your ChromaDB data before removing it")
        else:
            logger.error("Migration verification failed. Please check the logs.")
            
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        raise

if __name__ == "__main__":
    main() 