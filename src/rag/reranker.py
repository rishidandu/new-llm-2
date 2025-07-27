import logging
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import numpy as np

class Reranker:
    """Reranks retrieved documents based on query relevance"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the reranker with a cross-encoder model.
        
        Args:
            model_name: Name of the cross-encoder model to use
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        
        try:
            self.model = CrossEncoder(model_name)
            self.logger.info(f"Loaded reranker model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load reranker model: {e}")
            raise
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank documents based on their relevance to the query.
        
        Args:
            query: The user's question
            documents: List of document dictionaries with 'content' and 'metadata' keys
            top_k: Number of top documents to return
            
        Returns:
            List of reranked documents with updated scores and ranks
        """
        if not documents:
            return []
        
        try:
            # Prepare query-document pairs for the cross-encoder
            pairs = [[query, doc['content']] for doc in documents]
            
            # Get relevance scores from the cross-encoder
            scores = self.model.predict(pairs)
            
            # Create list of documents with their scores
            scored_docs = []
            for i, (doc, score) in enumerate(zip(documents, scores)):
                scored_docs.append({
                    **doc,
                    'rerank_score': float(score),
                    'original_rank': doc.get('rank', i + 1)
                })
            
            # Sort by rerank score (higher is better)
            reranked_docs = sorted(scored_docs, key=lambda x: x['rerank_score'], reverse=True)
            
            # Update ranks and return top_k
            for i, doc in enumerate(reranked_docs[:top_k]):
                doc['rank'] = i + 1
                doc['score'] = doc['rerank_score']  # Use rerank score as primary score
            
            self.logger.info(f"Reranked {len(documents)} documents, returning top {len(reranked_docs[:top_k])}")
            return reranked_docs[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error during reranking: {e}")
            # Return original documents if reranking fails
            return documents[:top_k]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranker model"""
        return {
            'model_name': self.model_name,
            'type': 'cross-encoder',
            'description': 'MS MARCO trained cross-encoder for document reranking'
        } 