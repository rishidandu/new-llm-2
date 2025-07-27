import os
import json
import re
from typing import List, Dict, Any, Generator, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RAGDocument:
    """RAG-optimized document with conversation context"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    conversation_context: Optional[str] = None
    quality_score: float = 1.0
    related_documents: List[str] = None

class RAGOptimizedProcessor:
    """Processes data specifically optimized for RAG applications"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.conversation_cache = {}  # Cache for conversation context
        
    def calculate_quality_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate quality score based on Reddit metrics"""
        score = 1.0
        
        # Post score (upvotes)
        if 'score' in metadata:
            score += min(metadata['score'] / 10, 5.0)  # Cap at +5
        
        # Comment count (engagement)
        if 'num_comments' in metadata:
            score += min(metadata['num_comments'] / 5, 3.0)  # Cap at +3
        
        # Author reputation (simple heuristic)
        if metadata.get('author') and metadata['author'] != '[deleted]':
            score += 0.5
        
        # Post type preference
        if metadata.get('post_type') == 'submission':
            score += 1.0  # Submissions get bonus
        
        return min(score, 10.0)  # Cap at 10
    
    def build_conversation_context(self, data: Dict[str, Any], all_posts: Dict[str, Any]) -> str:
        """Build conversation context for better RAG retrieval"""
        if data.get('post_type') != 'comment':
            return None
        
        parent_id = data.get('metadata', {}).get('parent_id')
        if not parent_id:
            return None
        
        # Find parent post
        parent_post = all_posts.get(parent_id)
        if not parent_post:
            return None
        
        # Build context
        context_parts = []
        
        # Add original post title and content
        if parent_post.get('title'):
            context_parts.append(f"Original post: {parent_post['title']}")
        
        if parent_post.get('text'):
            # Truncate if too long
            text = parent_post['text'][:200] + "..." if len(parent_post['text']) > 200 else parent_post['text']
            context_parts.append(f"Content: {text}")
        
        # Add subreddit context
        subreddit = data.get('metadata', {}).get('subreddit', '')
        if subreddit:
            context_parts.append(f"Subreddit: r/{subreddit}")
        
        return " | ".join(context_parts)
    
    def group_related_content(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group related posts and comments together"""
        # Group by submission
        submission_groups = defaultdict(list)
        
        for doc in documents:
            if doc.get('post_type') == 'submission':
                submission_groups[doc['id']].append(doc)
            elif doc.get('post_type') == 'comment':
                parent_id = doc.get('parent_id', '').replace('t3_', '').replace('t1_', '')
                submission_groups[parent_id].append(doc)
        
        # Create conversation threads
        conversation_threads = []
        for submission_id, group in submission_groups.items():
            # Sort by timestamp if available
            group.sort(key=lambda x: x.get('created_utc', 0))
            
            # Create conversation document
            if group:
                submission = next((d for d in group if d.get('post_type') == 'submission'), None)
                if submission:
                    # Combine all content
                    all_content = [submission.get('text', '')]
                    all_comments = [d.get('text', '') for d in group if d.get('post_type') == 'comment']
                    
                    conversation_text = f"POST: {submission.get('title', '')}\n{submission.get('text', '')}\n\n"
                    if all_comments:
                        conversation_text += "COMMENTS:\n" + "\n".join(all_comments)
                    
                    conversation_threads.append({
                        'id': f"conversation_{submission_id}",
                        'title': submission.get('title', ''),
                        'text': conversation_text,
                        'metadata': {
                            **submission.get('metadata', {}),
                            'conversation_length': len(group),
                            'comment_count': len(all_comments),
                            'conversation_id': submission_id
                        },
                        'post_type': 'conversation'
                    })
        
        return conversation_threads
    
    def chunk_text_semantic(self, text: str, metadata: Dict[str, Any]) -> List[RAGDocument]:
        """Chunk text with semantic boundaries for RAG"""
        if len(text) <= self.chunk_size:
            return [RAGDocument(
                id=f"{metadata.get('id', 'unknown')}_chunk_0",
                content=text,
                metadata=metadata,
                source=metadata.get('source', 'unknown'),
                quality_score=self.calculate_quality_score(metadata)
            )]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at semantic boundaries
            if end < len(text):
                # Look for paragraph breaks first
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] == '\n' and text[i-1] == '\n':
                        end = i
                        break
                
                # Then look for sentence endings
                if end == start + self.chunk_size:
                    for i in range(end, max(start + self.chunk_size - 100, start), -1):
                        if text[i] in '.!?':
                            end = i + 1
                            break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(RAGDocument(
                    id=f"{metadata.get('id', 'unknown')}_chunk_{chunk_id}",
                    content=chunk_text,
                    metadata={**metadata, 'chunk_id': chunk_id},
                    source=metadata.get('source', 'unknown'),
                    quality_score=self.calculate_quality_score(metadata)
                ))
                chunk_id += 1
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_reddit_data_rag_optimized(self, file_path: str) -> Generator[RAGDocument, None, None]:
        """Process Reddit data optimized for RAG applications"""
        logger.info(f"Processing Reddit data for RAG from {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"Reddit data file not found: {file_path}")
            return
        
        # First pass: collect all posts for context building
        all_posts = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    all_posts[data.get('id')] = data
                except json.JSONDecodeError:
                    continue
        
        # Second pass: process with context
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                try:
                    data = json.loads(line.strip())
                    
                    # Create enhanced metadata
                    metadata = {
                        'id': data.get('id'),
                        'url': data.get('url'),
                        'title': data.get('title'),
                        'source': 'reddit',
                        'ingested_at': data.get('ingested_at'),
                        'line_number': line_num,
                        **data.get('metadata', {})
                    }
                    
                    # Build conversation context
                    conversation_context = self.build_conversation_context(data, all_posts)
                    
                    # Create enhanced content
                    content = data.get('text', '')
                    if conversation_context:
                        content = f"Context: {conversation_context}\n\nContent: {content}"
                    
                    # Chunk with semantic boundaries
                    chunks = self.chunk_text_semantic(content, metadata)
                    for chunk in chunks:
                        chunk.conversation_context = conversation_context
                        yield chunk
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing line {line_num}: {e}")
                    continue
    
    def process_conversation_threads(self, file_path: str) -> Generator[RAGDocument, None, None]:
        """Process data as conversation threads for better RAG retrieval"""
        logger.info(f"Processing conversation threads from {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"Data file not found: {file_path}")
            return
        
        # Load all documents
        documents = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    documents.append(data)
                except json.JSONDecodeError:
                    continue
        
        # Group into conversation threads
        conversation_threads = self.group_related_content(documents)
        
        # Process each conversation thread
        for thread in conversation_threads:
            metadata = {
                'id': thread['id'],
                'url': thread.get('url', ''),
                'title': thread['title'],
                'source': 'reddit_conversation',
                'ingested_at': thread.get('ingested_at', ''),
                **thread.get('metadata', {})
            }
            
            # Chunk the conversation
            chunks = self.chunk_text_semantic(thread['text'], metadata)
            for chunk in chunks:
                yield chunk 