#!/usr/bin/env python3
"""
Parallel ASU grades data processing script with batch embeddings.
This script will:
1. Process all CSV grade files
2. Process professor data
3. Generate embeddings in batches (much faster)
4. Add to vector store
"""

import sys
import os
import logging
import asyncio
import aiohttp
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import json

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from src.utils.asu_grades_processor import ASUGradesProcessor
from src.rag.vector_store import VectorStore
from tqdm import tqdm

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('asu_grades_processing_parallel.log'),
            logging.StreamHandler()
        ]
    )

class BatchEmbeddingGenerator:
    """Generate embeddings in batches for faster processing"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", batch_size: int = 100):
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self.base_url = "https://api.openai.com/v1/embeddings"
        
    async def get_embeddings_batch(self, session: aiohttp.ClientSession, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts"""
        if not texts:
            return []
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": texts
        }
        
        try:
            async with session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return [item["embedding"] for item in result["data"]]
                else:
                    error_text = await response.text()
                    logging.error(f"API Error {response.status}: {error_text}")
                    return []
        except Exception as e:
            logging.error(f"Request error: {e}")
            return []
    
    async def get_embeddings_parallel(self, texts: List[str], max_concurrent: int = 5) -> List[List[float]]:
        """Get embeddings for all texts using parallel processing"""
        if not texts:
            return []
        
        # Split texts into batches
        batches = [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch(batch):
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    return await self.get_embeddings_batch(session, batch)
        
        # Process all batches concurrently
        tasks = [process_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_embeddings = []
        for result in results:
            if isinstance(result, list):
                all_embeddings.extend(result)
            else:
                logging.error(f"Batch processing error: {result}")
                # Add empty embeddings for failed batch
                all_embeddings.extend([[] for _ in range(self.batch_size)])
        
        return all_embeddings[:len(texts)]  # Ensure we return exactly the right number

def process_documents_in_batches(documents: List, batch_size: int = 100) -> List[List]:
    """Split documents into batches"""
    return [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]

async def main_async():
    """Main async processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting parallel ASU grades data processing...")
    
    # Load configuration
    config = Config()
    
    # Initialize processor
    grades_processor = ASUGradesProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    
    # Process all grades data
    logger.info("Processing ASU grades data...")
    documents = list(grades_processor.process_all_grades_data())
    
    if not documents:
        logger.error("No documents generated from grades data")
        return
    
    logger.info(f"Generated {len(documents)} documents from grades data")
    
    # Initialize batch embedding generator
    embedding_gen = BatchEmbeddingGenerator(
        api_key=config.OPENAI_API_KEY,
        model=config.EMBEDDING_MODEL,
        batch_size=100
    )
    
    # Generate embeddings in parallel
    logger.info("Generating embeddings in parallel...")
    start_time = time.time()
    
    # Extract text content for embedding
    texts = [doc.content for doc in documents]
    
    # Get embeddings using parallel processing
    embeddings = await embedding_gen.get_embeddings_parallel(texts, max_concurrent=5)
    
    end_time = time.time()
    logger.info(f"Generated {len(embeddings)} embeddings in {end_time - start_time:.2f} seconds")
    
    # Filter out documents without embeddings
    valid_docs = []
    valid_embeddings = []
    
    for doc, embedding in zip(documents, embeddings):
        if embedding:  # Check if embedding was generated successfully
            valid_docs.append(doc)
            valid_embeddings.append(embedding)
        else:
            logger.warning(f"Failed to generate embedding for document {doc.id}")
    
    logger.info(f"Valid documents with embeddings: {len(valid_docs)}")
    
    # Add to vector store
    logger.info("Adding documents to vector store...")
    vector_store = VectorStore(config.COLLECTION_NAME, config.VECTOR_DB_DIR)
    vector_store.add_documents(valid_docs, valid_embeddings)
    
    logger.info(f"Successfully processed and stored {len(valid_docs)} ASU grades documents")
    
    # Print statistics
    course_docs = [doc for doc in valid_docs if doc.source == 'asu_grades']
    professor_docs = [doc for doc in valid_docs if doc.source == 'asu_grades_professors']
    
    logger.info(f"Course documents: {len(course_docs)}")
    logger.info(f"Professor documents: {len(professor_docs)}")
    logger.info(f"Processing time: {end_time - start_time:.2f} seconds")

def main():
    """Main function to run async processing"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 