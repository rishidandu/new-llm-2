import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import os

from src.utils.data_processor import Document
from config.settings import Config

class VectorStore:
    """Handles ChromaDB vector store operations"""
    
    def __init__(self, collection_name: str, db_path: str):
        self.collection_name = collection_name
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)  # Initialize logger first
        
        # Use embedded client (single-process mode)
        self.client = chromadb.PersistentClient(path=db_path)
            
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Loaded existing collection: {self.collection_name}")
            return collection
        except Exception as e:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "ASU knowledge base for RAG"}
            )
            self.logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def _clean_metadata_for_chromadb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to be compatible with ChromaDB"""
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                # Convert None to empty string
                cleaned[key] = ""
            elif isinstance(value, (int, float, str, bool)):
                # These types are supported by ChromaDB
                cleaned[key] = value
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned
    
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]):
        """Add documents to vector store"""
        if not documents or not embeddings:
            self.logger.warning("No documents or embeddings provided")
            return
        
        # Prepare data for ChromaDB with cleaned metadata
        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [self._clean_metadata_for_chromadb(doc.metadata) for doc in documents]
        
        # Add in batches
        batch_size = Config.BATCH_SIZE
        successful_adds = 0
        
        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_contents = contents[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_contents,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                successful_adds += len(batch_ids)
                self.logger.info(f"Added batch {i//batch_size + 1} to vector store ({len(batch_ids)} documents)")
            except Exception as e:
                self.logger.error(f"Error adding batch {i//batch_size + 1} to vector store: {e}")
                # Try adding documents one by one to identify problematic ones
                for j, (doc_id, content, embedding, metadata) in enumerate(zip(batch_ids, batch_contents, batch_embeddings, batch_metadatas)):
                    try:
                        self.collection.add(
                            ids=[doc_id],
                            documents=[content],
                            embeddings=[embedding],
                            metadatas=[metadata]
                        )
                        successful_adds += 1
                    except Exception as single_error:
                        self.logger.error(f"Failed to add document {doc_id}: {single_error}")
        
        self.logger.info(f"Successfully added {successful_adds} out of {len(documents)} documents to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'score': 1 - distance,  # Convert distance to similarity score
                        'rank': i + 1
                    })
            
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {
                'total_documents': 0,
                'collection_name': self.collection_name
            } 