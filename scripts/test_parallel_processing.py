#!/usr/bin/env python3
"""
Test script for parallel ASU grades processing with a small subset.
This will test the parallel processing with just a few documents to ensure it works.
"""

import sys
import os
import logging
import asyncio
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from src.utils.asu_grades_processor import ASUGradesProcessor

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_parallel_embeddings():
    """Test parallel embedding generation with a small subset"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Testing parallel ASU grades processing...")
    
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
    
    # Take only first 10 documents for testing
    test_documents = documents[:10]
    logger.info(f"Testing with {len(test_documents)} documents")
    
    # Import the parallel embedding generator
    from scripts.process_asu_grades_parallel import BatchEmbeddingGenerator
    
    # Initialize batch embedding generator
    embedding_gen = BatchEmbeddingGenerator(
        api_key=config.OPENAI_API_KEY,
        model=config.EMBEDDING_MODEL,
        batch_size=5  # Small batch size for testing
    )
    
    # Generate embeddings in parallel
    logger.info("Testing parallel embedding generation...")
    start_time = time.time()
    
    # Extract text content for embedding
    texts = [doc.content for doc in test_documents]
    
    # Get embeddings using parallel processing
    embeddings = await embedding_gen.get_embeddings_parallel(texts, max_concurrent=2)
    
    end_time = time.time()
    logger.info(f"Generated {len(embeddings)} embeddings in {end_time - start_time:.2f} seconds")
    
    # Check results
    valid_embeddings = [emb for emb in embeddings if emb]
    logger.info(f"Valid embeddings: {len(valid_embeddings)}/{len(embeddings)}")
    
    if valid_embeddings:
        logger.info("✅ Parallel processing test successful!")
        logger.info(f"Average time per document: {(end_time - start_time) / len(test_documents):.2f} seconds")
        
        # Show sample embedding
        sample_embedding = valid_embeddings[0]
        logger.info(f"Sample embedding length: {len(sample_embedding)}")
        logger.info(f"Sample embedding first 5 values: {sample_embedding[:5]}")
    else:
        logger.error("❌ No valid embeddings generated")

def main():
    """Main function"""
    asyncio.run(test_parallel_embeddings())

if __name__ == "__main__":
    main() 