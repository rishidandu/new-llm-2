import logging
from typing import List, Dict, Any, Optional
import os
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from src.utils.data_processor import Document
from config.settings import Config

class QdrantVectorStore:
    """Handles Qdrant Cloud vector store operations"""
    
    def __init__(self, collection_name: str, qdrant_url: Optional[str] = None, api_key: Optional[str] = None):
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # Get Qdrant credentials from environment or parameters
        self.qdrant_url = qdrant_url or os.getenv('QDRANT_URL')
        self.api_key = api_key or os.getenv('QDRANT_API_KEY')
        
        if not self.qdrant_url or not self.api_key:
            raise ValueError("Qdrant URL and API key must be provided via environment variables or parameters")
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.api_key,
        )
        
        # Embedding dimension - can be configured
        self.embedding_dim = int(os.getenv('EMBEDDING_DIM', 1536))  # OpenAI text-embedding-3-small default
        
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                self.logger.info(f"Loaded existing collection: {self.collection_name}")
                return self.collection_name
            else:
                # Create new collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Created new collection: {self.collection_name}")
                return self.collection_name
                
        except Exception as e:
            self.logger.error(f"Error creating/accessing collection: {e}")
            raise
    
    def _clean_metadata_for_qdrant(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to be compatible with Qdrant"""
        cleaned = {}
        for key, value in metadata.items():
            if value is None:
                # Convert None to empty string
                cleaned[key] = ""
            elif isinstance(value, (int, float, str, bool)):
                # These types are supported by Qdrant
                cleaned[key] = value
            elif isinstance(value, list):
                # Convert lists to strings (Qdrant supports arrays but this is simpler)
                cleaned[key] = str(value)
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned
    
    def _generate_point_id(self, doc_id: str) -> str:
        """Generate a UUID from the document ID for Qdrant compatibility"""
        # Create a hash from the doc_id and convert to UUID format
        hash_obj = hashlib.md5(doc_id.encode())
        hash_hex = hash_obj.hexdigest()
        # Format as UUID: 8-4-4-4-12
        uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        return uuid_str
    
    def add_documents(self, documents: List[Document], embeddings: List[List[float]]):
        """Add documents to vector store"""
        if not documents or not embeddings:
            self.logger.warning("No documents or embeddings provided")
            return
        
        # Prepare points for Qdrant
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            cleaned_metadata = self._clean_metadata_for_qdrant(doc.metadata)
            # Add content and original ID to metadata for retrieval
            cleaned_metadata['content'] = doc.content
            cleaned_metadata['original_id'] = doc.id
            
            point = PointStruct(
                id=self._generate_point_id(doc.id),
                vector=embedding,
                payload=cleaned_metadata
            )
            points.append(point)
        
        # Add in batches
        batch_size = getattr(Config, 'BATCH_SIZE', 100)
        successful_adds = 0
        
        for i in range(0, len(points), batch_size):
            batch_points = points[i:i + batch_size]
            
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch_points
                )
                successful_adds += len(batch_points)
                self.logger.info(f"Added batch {i//batch_size + 1} to Qdrant ({len(batch_points)} documents)")
            except Exception as e:
                self.logger.error(f"Error adding batch {i//batch_size + 1} to Qdrant: {e}")
                # Try adding points one by one to identify problematic ones
                for point in batch_points:
                    try:
                        self.client.upsert(
                            collection_name=self.collection_name,
                            points=[point]
                        )
                        successful_adds += 1
                    except Exception as single_error:
                        self.logger.error(f"Failed to add document {point.id}: {single_error}")
        
        self.logger.info(f"Successfully added {successful_adds} out of {len(documents)} documents to Qdrant")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False  # We don't need the vectors back
            )
            
            # Format results to match ChromaDB interface
            formatted_results = []
            for i, result in enumerate(search_result):
                # Extract content from payload
                content = result.payload.get('content', '')
                
                # Create metadata dict without content
                metadata = {k: v for k, v in result.payload.items() if k != 'content'}
                
                formatted_results.append({
                    'content': content,
                    'metadata': metadata,
                    'score': result.score,  # Qdrant already provides similarity score
                    'rank': i + 1
                })
            
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Error searching Qdrant: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'total_documents': collection_info.points_count,
                'collection_name': self.collection_name,
                'vector_size': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance.value
            }
        except Exception as e:
            self.logger.error(f"Error getting Qdrant collection stats: {e}")
            return {
                'total_documents': 0,
                'collection_name': self.collection_name
            }
    
    def delete_collection(self):
        """Delete the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Error deleting collection: {e}")
            raise
    
    def collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False 