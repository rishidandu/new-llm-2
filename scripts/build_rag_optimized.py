#!/usr/bin/env python3
"""
Build RAG System with Optimized Data Processing
Uses conversation context and quality scoring for better retrieval
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.rag_optimized_processor import RAGOptimizedProcessor
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore
from config.settings import Config
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Build RAG system with optimized processing"""
    config = Config()
    
    print("🚀 Building RAG system with optimized processing...")
    start_time = time.time()
    
    # Initialize components
    processor = RAGOptimizedProcessor(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    
    embedding_generator = EmbeddingGenerator()
    vector_store = VectorStore(config)
    
    # Get latest data files
    reddit_files = processor._get_latest_files(config.REDDIT_RAW_DIR)
    asu_files = processor._get_latest_files(config.ASU_RAW_DIR)
    
    print(f"📁 Found {len(reddit_files)} Reddit files and {len(asu_files)} ASU files")
    
    total_documents = 0
    
    # Process Reddit data with conversation context
    for file_path in reddit_files:
        print(f"🔄 Processing Reddit file: {os.path.basename(file_path)}")
        
        # Option 1: Process with conversation context
        documents = list(processor.process_reddit_data_rag_optimized(file_path))
        
        # Option 2: Process as conversation threads (alternative)
        # documents = list(processor.process_conversation_threads(file_path))
        
        print(f"   📄 Generated {len(documents)} RAG-optimized documents")
        
        # Add to vector store with quality scoring
        for doc in documents:
            # Generate embedding
            embedding = embedding_generator.get_embedding(doc.content)
            
            # Add with quality score in metadata
            enhanced_metadata = {
                **doc.metadata,
                'quality_score': doc.quality_score,
                'conversation_context': doc.conversation_context
            }
            
            vector_store.add_document(
                content=doc.content,
                metadata=enhanced_metadata,
                embedding=embedding
            )
        
        total_documents += len(documents)
    
    # Process ASU data (standard processing)
    for file_path in asu_files:
        print(f"🔄 Processing ASU file: {os.path.basename(file_path)}")
        
        # Use standard processing for ASU data
        from src.utils.data_processor import DataProcessor
        standard_processor = DataProcessor(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        documents = list(standard_processor.process_asu_data(file_path))
        print(f"   📄 Generated {len(documents)} documents")
        
        for doc in documents:
            embedding = embedding_generator.get_embedding(doc.content)
            vector_store.add_document(
                content=doc.content,
                metadata=doc.metadata,
                embedding=embedding
            )
        
        total_documents += len(documents)
    
    # Save vector store
    vector_store.save()
    
    elapsed_time = time.time() - start_time
    print(f"✅ RAG system built successfully!")
    print(f"📊 Total documents processed: {total_documents}")
    print(f"⏱️ Total time: {elapsed_time:.2f} seconds")
    print(f"🚀 Documents per second: {total_documents/elapsed_time:.1f}")

if __name__ == "__main__":
    main() 