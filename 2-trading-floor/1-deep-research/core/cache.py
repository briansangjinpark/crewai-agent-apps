from typing import Optional, Any, Callable
import hashlib
import time
from datetime import datetime
import asyncio
from collections import OrderedDict


class CacheEntry:
    """Represents a cached value with metadata"""

    def __init__(self, value: Any, expires_at: float):
        self.value = value
        self.expires_at = expires_at
        self.created_at = datetime.now()
        self.hits = 0


class InMemoryCache:
    """
    LRU cache with TTL support for storing search results and plans.
    Thread-safe using asyncio.Lock.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._cache_hits = 0
        self._cache_misses = 0

    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate cache key from query by normalizing and hashing"""
        normalized = data.lower().strip()
        hash_value = hashlib.md5(normalized.encode()).hexdigest()
        return f"{prefix}:{hash_value}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]

                # Check if expired
                if time.time() >= entry.expires_at:
                    del self.cache[key]
                    self._cache_misses += 1
                    return None

                # Update stats
                entry.hits += 1
                self._cache_hits += 1

                # Move to end (LRU - most recently used)
                self.cache.move_to_end(key)

                return entry.value

            self._cache_misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl

            # Evict oldest item if at capacity and key is new
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Remove least recently used item (first item)
                self.cache.popitem(last=False)

            self.cache[key] = CacheEntry(value, expires_at)
            self.cache.move_to_end(key)

    async def delete(self, key: str):
        """Delete a specific key from cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]

    async def clear(self):
        """Clear entire cache"""
        async with self._lock:
            self.cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        ttl: Optional[int] = None
    ):
        """
        Get from cache or compute and cache the result.
        This is the primary method to use for caching.
        """
        cached = await self.get(key)
        if cached is not None:
            return cached

        result = await compute_fn()
        await self.set(key, result, ttl)
        return result

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "utilization": f"{(len(self.cache) / self.max_size) * 100:.1f}%",
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.1f}%"
        }

    async def cleanup_expired(self):
        """Remove expired entries"""
        async with self._lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if now >= entry.expires_at
            ]
            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)


# Global cache instance
cache = InMemoryCache(max_size=1000, default_ttl=3600)
