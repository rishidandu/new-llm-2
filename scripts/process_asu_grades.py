#!/usr/bin/env python3
"""
Script to process ASU grades data and integrate it into the RAG system.
This script will:
1. Process all CSV grade files
2. Process professor data
3. Generate embeddings
4. Add to vector store
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from src.utils.asu_grades_processor import ASUGradesProcessor
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore
from tqdm import tqdm

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('asu_grades_processing.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ASU grades data processing...")
    
    # Load configuration
    config = Config()
    
    # Initialize processors
    grades_processor = ASUGradesProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    embedding_gen = EmbeddingGenerator(config.EMBEDDING_MODEL)
    vector_store = VectorStore(config.COLLECTION_NAME, config.VECTOR_DB_DIR)
    
    # Process all grades data
    logger.info("Processing ASU grades data...")
    documents = list(grades_processor.process_all_grades_data())
    
    if not documents:
        logger.error("No documents generated from grades data")
        return
    
    logger.info(f"Generated {len(documents)} documents from grades data")
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    embeddings = []
    for doc in tqdm(documents, desc="Generating embeddings"):
        embedding = embedding_gen.get_embedding(doc.content)
        if embedding:
            embeddings.append(embedding)
        else:
            logger.warning(f"Failed to generate embedding for document {doc.id}")
    
    if len(embeddings) != len(documents):
        logger.warning(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(documents)} documents")
        # Filter out documents without embeddings
        documents = [doc for i, doc in enumerate(documents) if i < len(embeddings)]
    
    # Add to vector store
    logger.info("Adding documents to vector store...")
    vector_store.add_documents(documents, embeddings)
    
    logger.info(f"Successfully processed and stored {len(documents)} ASU grades documents")
    
    # Print some statistics
    course_docs = [doc for doc in documents if doc.source == 'asu_grades']
    professor_docs = [doc for doc in documents if doc.source == 'asu_grades_professors']
    
    logger.info(f"Course documents: {len(course_docs)}")
    logger.info(f"Professor documents: {len(professor_docs)}")
    
    # Print sample documents
    if course_docs:
        logger.info("Sample course document:")
        logger.info(course_docs[0].content[:500] + "...")
    
    if professor_docs:
        logger.info("Sample professor document:")
        logger.info(professor_docs[0].content[:500] + "...")

if __name__ == "__main__":
    main() 