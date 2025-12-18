"""
Caching system for QuoteWise AI application.
Provides in-memory caching for frequently accessed data.
"""

import time
import json
from typing import Any, Optional, Dict, Union
from functools import wraps
from .logger import get_logger

logger = get_logger("cache")


class MemoryCache:
    """In-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cache entry with TTL."""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        logger.debug(f"Cache set: {key}", ttl=ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache entry if not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry['expires_at']:
            del self.cache[key]
            logger.debug(f"Cache expired: {key}")
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        active_entries = sum(
            1 for entry in self.cache.values()
            if current_time <= entry['expires_at']
        )
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': len(self.cache) - active_entries
        }


# Global cache instance
cache = MemoryCache()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def cache_inventory_data(ttl: int = 1800):  # 30 minutes
    """Cache inventory data with specific TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"inventory_data:{hash(str(args) + str(kwargs))}"
            
            result = cache.get(cache_key)
            if result is not None:
                logger.debug("Inventory data cache hit")
                return result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug("Inventory data cached")
            
            return result
        return wrapper
    return decorator


def cache_pricing_calculations(ttl: int = 900):  # 15 minutes
    """Cache pricing calculations with specific TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"pricing_calc:{hash(str(args) + str(kwargs))}"
            
            result = cache.get(cache_key)
            if result is not None:
                logger.debug("Pricing calculation cache hit")
                return result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug("Pricing calculation cached")
            
            return result
        return wrapper
    return decorator

