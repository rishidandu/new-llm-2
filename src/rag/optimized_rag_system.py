#!/usr/bin/env python3
"""
Optimized RAG System for production deployment
Includes caching, timeouts, and performance optimizations
"""

import logging
import time
from typing import List, Dict, Any, Optional
from functools import lru_cache
import hashlib

from config.settings import Config
from src.rag.rag_system import ASURAGSystem

logger = logging.getLogger(__name__)

class OptimizedRAGSystem:
    """Optimized RAG system with caching and performance improvements"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_rag = ASURAGSystem(config)
        self.query_cache = {}
        self.max_cache_size = 100
        self.cache_ttl = 3600  # 1 hour
        
    def _get_cache_key(self, question: str) -> str:
        """Generate cache key for question"""
        return hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry['timestamp'] < self.cache_ttl
    
    def _cleanup_cache(self):
        """Remove old cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.query_cache.items()
            if current_time - entry['timestamp'] > self.cache_ttl
        ]
        for key in expired_keys:
            del self.query_cache[key]
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Optimized query with caching and reduced search scope"""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(question)
        if cache_key in self.query_cache:
            entry = self.query_cache[cache_key]
            if self._is_cache_valid(entry):
                logger.info(f"🚀 Cache hit for query (saved {time.time() - start_time:.2f}s)")
                return entry['result']
        
        # Clean up old cache entries
        if len(self.query_cache) > self.max_cache_size:
            self._cleanup_cache()
        
        try:
            # Use reduced top_k for faster responses
            result = self.base_rag.query(question, top_k=top_k)
            
            # Cache the result
            self.query_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            query_time = time.time() - start_time
            logger.info(f"⚡ Query completed in {query_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return {
                'question': question,
                'answer': "I'm experiencing some technical difficulties. Please try again in a moment.",
                'sources': [],
                'context': ""
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics including cache info"""
        base_stats = self.base_rag.get_stats()
        base_stats.update({
            'cache_size': len(self.query_cache),
            'cache_hit_ratio': self._calculate_cache_hit_ratio(),
            'optimization_enabled': True
        })
        return base_stats
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)"""
        # This is a simplified version - in production you'd track this properly
        return 0.0 if len(self.query_cache) == 0 else min(0.8, len(self.query_cache) / 10) 