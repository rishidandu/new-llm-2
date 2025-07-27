import logging
from typing import List, Dict, Any
from tqdm import tqdm

from config.settings import Config
from src.utils.data_processor import DataProcessor
from src.utils.asu_grades_processor import ASUGradesProcessor
from src.rag.embeddings import EmbeddingGenerator
from src.rag.llm import LLMGenerator
from src.rag.vector_store_factory import create_vector_store
from src.rag.reranker import Reranker

class ASURAGSystem:
    """Main RAG system orchestrator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_processor = DataProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        self.grades_processor = ASUGradesProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        self.embedding_gen = EmbeddingGenerator(config.EMBEDDING_MODEL)
        self.llm_gen = LLMGenerator(config.LLM_MODEL)
        self.vector_store = create_vector_store(config.COLLECTION_NAME)
        self.reranker = Reranker()  # Initialize reranker
    
    def ingest_data(self, data_sources: List[str]):
        """Ingest data from specified sources"""
        self.logger.info(f"Ingesting data from sources: {data_sources}")
        
        all_documents = []
        
        for source in data_sources:
            if source == "asu_web":
                # Find latest ASU web data file
                import glob
                asu_files = glob.glob(f"{self.config.ASU_RAW_DIR}/*.jsonl")
                if asu_files:
                    latest_file = max(asu_files, key=lambda x: x.split('/')[-1])
                    docs = list(self.data_processor.process_asu_data(latest_file))  # Convert generator to list
                    all_documents.extend(docs)
                    self.logger.info(f"Processed {len(docs)} ASU web documents")
                else:
                    self.logger.warning("No ASU web data files found")
            
            elif source == "reddit":
                # Find latest Reddit data file
                import glob
                reddit_files = glob.glob(f"{self.config.REDDIT_RAW_DIR}/*.jsonl")
                if reddit_files:
                    latest_file = max(reddit_files, key=lambda x: x.split('/')[-1])
                    docs = list(self.data_processor.process_reddit_data(latest_file))  # Convert generator to list
                    all_documents.extend(docs)
                    self.logger.info(f"Processed {len(docs)} Reddit documents")
                else:
                    self.logger.warning("No Reddit data files found")
            
            elif source == "asu_grades":
                # Process ASU grades data
                docs = list(self.grades_processor.process_all_grades_data())  # Convert generator to list
                all_documents.extend(docs)
                self.logger.info(f"Processed {len(docs)} ASU grades documents")
        
        if not all_documents:
            self.logger.error("No documents to process")
            return
        
        # Generate embeddings
        self.logger.info("Generating embeddings...")
        embeddings = []
        for doc in tqdm(all_documents, desc="Generating embeddings"):
            embedding = self.embedding_gen.get_embedding(doc.content)
            embeddings.append(embedding)
        
        # Add to vector store
        self.logger.info("Adding documents to vector store...")
        self.vector_store.add_documents(all_documents, embeddings)
        
        self.logger.info(f"Successfully ingested {len(all_documents)} documents")
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Complete RAG pipeline: retrieve + rerank + generate"""
        # Get query embedding
        query_embedding = self.embedding_gen.get_embedding(question)
        
        if not query_embedding:
            return {
                'question': question,
                'answer': "Error: Could not generate query embedding",
                'sources': [],
                'context': ""
            }
        
        # Search for relevant documents (retrieve more for reranking)
        initial_results = self.vector_store.search(query_embedding, top_k=top_k * 2)
        
        if not initial_results:
            return {
                'question': question,
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': [],
                'context': ""
            }
        
        # Rerank the documents
        results = self.reranker.rerank(question, initial_results, top_k=top_k)
        
        # Prepare detailed context with metadata
        context_parts = []
        for i, result in enumerate(results):
            metadata = result['metadata']
            source_info = f"Source {i+1} ({metadata.get('source', 'unknown')}):"
            if metadata.get('title'):
                source_info += f" {metadata.get('title')}"
            if metadata.get('url'):
                source_info += f" [URL: {metadata.get('url')}]"
            context_parts.append(f"{source_info}\n{result['content']}")
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        answer = self.llm_gen.generate_answer(question, context)
        
        # Prepare sources
        sources = []
        for result in results:
            sources.append({
                'title': result['metadata'].get('title', 'No Title'),
                'url': result['metadata'].get('url', ''),
                'score': result['score'],
                'source': result['metadata'].get('source', 'unknown'),
                'content_preview': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            })
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'context': context
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        vector_stats = self.vector_store.get_stats()
        reranker_info = self.reranker.get_model_info()
        
        return {
            'vector_store': vector_stats,
            'embedding_model': self.config.EMBEDDING_MODEL,
            'llm_model': self.config.LLM_MODEL,
            'reranker_model': reranker_info['model_name'],
            'chunk_size': self.config.CHUNK_SIZE,
            'chunk_overlap': self.config.CHUNK_OVERLAP
        } 