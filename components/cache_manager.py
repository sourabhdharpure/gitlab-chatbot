"""
Cache Manager - Handles semantic and response caching
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

class SemanticCache:
    """Semantic cache for storing and retrieving responses based on semantic similarity."""
    
    def __init__(self, cache_file: str = "data/semantic_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.max_size = 1000
        self.similarity_threshold = 0.85  # Increased for better matches
    
    def _load_cache(self) -> Dict:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _get_query_hash(self, query: str) -> str:
        """Generate hash for query with normalization for better cache hits."""
        # Normalize query for better cache hits
        normalized = query.lower().strip()
        
        # Remove common variations that don't affect meaning
        import re
        normalized = re.sub(r'\b(what|how|tell me|explain|can you|please)\b', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)  # Remove extra spaces
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Tuple[str, List, Dict]]:
        """Get cached response for query."""
        query_hash = self._get_query_hash(query)
        if query_hash in self.cache:
            cached_data = self.cache[query_hash]
            # Check if cache is still valid (24 hours)
            if datetime.now().timestamp() - cached_data.get('timestamp', 0) < 86400:
                return cached_data.get('response'), cached_data.get('sources', []), cached_data.get('metadata', {})
        return None
    
    def store(self, query: str, response: str, sources: List, metadata: Dict):
        """Store response in cache."""
        query_hash = self._get_query_hash(query)
        self.cache[query_hash] = {
            'response': response,
            'sources': sources,
            'metadata': metadata,
            'timestamp': datetime.now().timestamp()
        }
        
        # Limit cache size
        if len(self.cache) > self.max_size:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1].get('timestamp', 0))
            for key, _ in sorted_items[:len(sorted_items) - self.max_size]:
                del self.cache[key]
        
        self._save_cache()

class ResponseCache:
    """Simple response cache for exact matches."""
    
    def __init__(self, cache_file: str = "data/response_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.max_size = 500
    
    def _load_cache(self) -> Dict:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading response cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving response cache: {e}")
    
    def get(self, query: str) -> Optional[Tuple[str, List, Dict]]:
        """Get cached response for exact query match."""
        query_lower = query.lower().strip()
        if query_lower in self.cache:
            cached_data = self.cache[query_lower]
            # Check if cache is still valid (12 hours)
            if datetime.now().timestamp() - cached_data.get('timestamp', 0) < 43200:
                return cached_data.get('response'), cached_data.get('sources', []), cached_data.get('metadata', {})
        return None
    
    def store(self, query: str, response: str, sources: List, metadata: Dict):
        """Store response in cache."""
        query_lower = query.lower().strip()
        self.cache[query_lower] = {
            'response': response,
            'sources': sources,
            'metadata': metadata,
            'timestamp': datetime.now().timestamp()
        }
        
        # Limit cache size
        if len(self.cache) > self.max_size:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1].get('timestamp', 0))
            for key, _ in sorted_items[:len(sorted_items) - self.max_size]:
                del self.cache[key]
        
        self._save_cache()

class CacheManager:
    """Manages all caching operations."""
    
    def __init__(self):
        self.semantic_cache = SemanticCache()
        self.response_cache = ResponseCache()
    
    def get_cached_response(self, query: str) -> Optional[Tuple[str, List, Dict, str]]:
        """Get cached response from either cache."""
        # Try exact match first
        cached = self.response_cache.get(query)
        if cached:
            return cached[0], cached[1], cached[2], "exact"
        
        # Try semantic match with similarity threshold
        cached = self.semantic_cache.get(query)
        if cached:
            return cached[0], cached[1], cached[2], "semantic"
        
        # Try to find similar queries in semantic cache
        similar_cached = self._find_similar_query(query)
        if similar_cached:
            return similar_cached[0], similar_cached[1], similar_cached[2], "semantic_similar"
        
        return None
    
    def _find_similar_query(self, query: str, threshold: float = 0.8) -> Optional[Tuple[str, List, Dict]]:
        """Find similar queries in the semantic cache."""
        query_lower = query.lower().strip()
        
        # Simple similarity check based on common words
        for cached_query, cached_data in self.semantic_cache.cache.items():
            if self._calculate_similarity(query_lower, cached_query.lower()) >= threshold:
                return cached_data.get('response'), cached_data.get('sources', []), cached_data.get('metadata', {})
        
        return None
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries."""
        # Remove common words for better matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall', 'we', 'you', 'i', 'me', 'my', 'our', 'us'}
        
        # Normalize queries - remove punctuation and extra spaces
        import re
        query1 = re.sub(r'[^\w\s]', ' ', query1.lower().strip())
        query2 = re.sub(r'[^\w\s]', ' ', query2.lower().strip())
        
        # Check for exact substring match first
        if query1 in query2 or query2 in query1:
            return 0.9
        
        words1 = set(query1.split()) - stop_words
        words2 = set(query2.split()) - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_sim = intersection / union if union > 0 else 0.0
        
        # Boost similarity for GitLab-specific terms
        gitlab_terms = {'gitlab', 'pr', 'mr', 'merge', 'request', 'pull', 'comment', 'review', 'code', 'pipeline', 'ci', 'cd', 'deploy', 'issue', 'bug', 'feature'}
        
        gitlab_intersection = len((words1 & gitlab_terms) & (words2 & gitlab_terms))
        if gitlab_intersection > 0:
            jaccard_sim += 0.2  # Boost for GitLab terms
        
        return min(jaccard_sim, 1.0)
    
    def store_response(self, query: str, response: str, sources: List, metadata: Dict):
        """Store response in both caches."""
        self.response_cache.store(query, response, sources, metadata)
        self.semantic_cache.store(query, response, sources, metadata)
