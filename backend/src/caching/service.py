import json
import logging
from typing import Any, Optional
from redis import Redis
from .redis_config import get_redis_cache_connection

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service using database 1 (separate from queues)."""
    
    def __init__(self):
        self.redis_client: Redis = get_redis_cache_connection()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached value or None if not found
        """
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set a value in cache with TTL.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int): Time to live in seconds (default: 1 hour)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key (str): Cache key to delete
            
        Returns:
            bool: True if key was deleted, False otherwise
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern (str): Pattern to match (e.g., "candidate:*")
            
        Returns:
            int: Number of keys deleted
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
            return 0

# Global cache instance
cache_service = CacheService()
