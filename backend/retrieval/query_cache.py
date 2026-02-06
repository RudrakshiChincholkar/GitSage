"""
Simple in-memory cache for query results.
Speeds up repeated queries significantly.
"""
from typing import Dict, List, Optional, Tuple
import hashlib
import time


class QueryCache:
    """
    LRU-style cache for query embeddings and results.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Args:
            max_size: Maximum number of cached queries
            ttl_seconds: Time-to-live for cached entries (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[List, float]] = {}  # key -> (results, timestamp)
        self._access_order: List[str] = []

    def _make_key(self, query: str, repo_url: Optional[str], top_k: int) -> str:
        """Generate cache key from query parameters."""
        key_str = f"{query}|{repo_url or ''}|{top_k}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, repo_url: Optional[str], top_k: int) -> Optional[List]:
        """
        Retrieve cached results if available and not expired.
        
        Returns:
            Cached results or None if not found/expired
        """
        key = self._make_key(query, repo_url, top_k)
        
        if key in self._cache:
            results, timestamp = self._cache[key]
            
            # Check if expired
            if time.time() - timestamp > self.ttl_seconds:
                del self._cache[key]
                self._access_order.remove(key)
                return None
            
            # Update access order (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            
            print(f"[QueryCache] ✓ Cache hit for query: {query[:50]}...")
            return results
        
        return None

    def set(self, query: str, repo_url: Optional[str], top_k: int, results: List):
        """Store query results in cache."""
        key = self._make_key(query, repo_url, top_k)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        # Store with timestamp
        self._cache[key] = (results, time.time())
        
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        print(f"[QueryCache] Cached results for: {query[:50]}...")

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._access_order.clear()


# Global cache instance
_query_cache = QueryCache()


def get_query_cache() -> QueryCache:
    """Get the global query cache instance."""
    return _query_cache