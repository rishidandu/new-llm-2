import logging
from typing import List
from openai import OpenAI
from config.settings import Config

class EmbeddingGenerator:
    """Handles OpenAI embeddings generation"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error getting embedding: {e}")
            return []
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        
        return embeddings 