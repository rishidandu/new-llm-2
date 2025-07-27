import os
import json
import os
from typing import List, Dict, Any, Generator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Represents a processed document for RAG"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str

class DataProcessor:
    """Processes raw data from different sources into RAG-ready format"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [Document(
                id=f"{metadata.get('id', 'unknown')}_chunk_0",
                content=text,
                metadata=metadata,
                source=metadata.get('source', 'unknown')
            )]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Document(
                    id=f"{metadata.get('id', 'unknown')}_chunk_{chunk_id}",
                    content=chunk_text,
                    metadata={**metadata, 'chunk_id': chunk_id},
                    source=metadata.get('source', 'unknown')
                ))
                chunk_id += 1
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_asu_data(self, file_path: str) -> Generator[Document, None, None]:
        """Process ASU web scraped data"""
        logger.info(f"Processing ASU data from {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"ASU data file not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                try:
                    data = json.loads(line.strip())
                    
                    # Create metadata
                    metadata = {
                        'id': data.get('id'),
                        'url': data.get('url'),
                        'title': data.get('title'),
                        'source': 'asu_web',
                        'ingested_at': data.get('ingested_at'),
                        'line_number': line_num
                    }
                    
                    # Chunk the text
                    chunks = self.chunk_text(data.get('text', ''), metadata)
                    for chunk in chunks:
                        yield chunk
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing line {line_num}: {e}")
                    continue
    
    def process_reddit_data(self, file_path: str) -> Generator[Document, None, None]:
        """Process Reddit scraped data"""
        logger.info(f"Processing Reddit data from {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"Reddit data file not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                try:
                    data = json.loads(line.strip())
                    
                    # Create metadata
                    metadata = {
                        'id': data.get('id'),
                        'url': data.get('url'),
                        'title': data.get('title'),
                        'source': 'reddit',
                        'ingested_at': data.get('ingested_at'),
                        'line_number': line_num,
                        **data.get('metadata', {})
                    }
                    
                    # Chunk the text
                    chunks = self.chunk_text(data.get('text', ''), metadata)
                    for chunk in chunks:
                        yield chunk
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing line {line_num}: {e}")
                    continue
    
    def process_all_sources(self, config) -> Generator[Document, None, None]:
        """Process all available data sources"""
        # Process ASU data
        asu_files = self._get_latest_files(config.ASU_RAW_DIR)
        for file_path in asu_files:
            yield from self.process_asu_data(file_path)
        
        # Process Reddit data
        reddit_files = self._get_latest_files(config.REDDIT_RAW_DIR)
        for file_path in reddit_files:
            yield from self.process_reddit_data(file_path)
    
    def _get_latest_files(self, directory: str) -> List[str]:
        """Get the most recent data files from a directory"""
        if not os.path.exists(directory):
            return []
        
        files = []
        for filename in os.listdir(directory):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(directory, filename)
                files.append(file_path)
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return files 
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return files 