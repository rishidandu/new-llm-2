"""
Vector Store Factory - Creates the appropriate vector store based on configuration
"""

import logging
from typing import Union

from config.settings import Config
from src.rag.vector_store import VectorStore
from src.rag.qdrant_vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)

def create_vector_store(collection_name: str = None) -> Union[VectorStore, QdrantVectorStore]:
    """
    Factory function to create the appropriate vector store based on configuration
    
    Args:
        collection_name: Name of the collection (defaults to Config.COLLECTION_NAME)
    
    Returns:
        Vector store instance (ChromaDB or Qdrant)
    """
    if collection_name is None:
        collection_name = Config.COLLECTION_NAME
    
    vector_store_type = Config.VECTOR_STORE_TYPE.lower()
    
    logger.info(f"Creating {vector_store_type} vector store with collection: {collection_name}")
    
    if vector_store_type == "qdrant":
        return QdrantVectorStore(
            collection_name=collection_name,
            qdrant_url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )
    elif vector_store_type == "chromadb":
        return VectorStore(
            collection_name=collection_name,
            db_path=Config.VECTOR_DB_PATH
        )
    else:
        raise ValueError(f"Unsupported vector store type: {vector_store_type}. Supported types: 'chromadb', 'qdrant'")

def get_vector_store_info() -> dict:
    """
    Get information about the currently configured vector store
    
    Returns:
        Dictionary with vector store configuration info
    """
    return {
        "type": Config.VECTOR_STORE_TYPE,
        "collection_name": Config.COLLECTION_NAME,
        "qdrant_url": Config.QDRANT_URL if Config.VECTOR_STORE_TYPE == "qdrant" else None,
        "chromadb_path": Config.VECTOR_DB_PATH if Config.VECTOR_STORE_TYPE == "chromadb" else None
    } 