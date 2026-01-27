"""
Simple test script to verify caching functionality
"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from core.cache import cache


async def test_cache():
    print("Testing cache functionality...\n")

    # Test 1: Basic set/get
    print("Test 1: Basic set/get")
    await cache.set("test_key", "test_value", ttl=60)
    result = await cache.get("test_key")
    assert result == "test_value", "Basic get/set failed"
    print("✓ Basic get/set works")

    # Test 2: Cache miss
    print("\nTest 2: Cache miss")
    result = await cache.get("nonexistent_key")
    assert result is None, "Cache miss should return None"
    print("✓ Cache miss works")

    # Test 3: get_or_compute
    print("\nTest 3: get_or_compute")
    compute_count = 0

    async def expensive_compute():
        nonlocal compute_count
        compute_count += 1
        return "computed_value"

    # First call should compute
    result1 = await cache.get_or_compute("compute_key", expensive_compute, ttl=60)
    assert result1 == "computed_value"
    assert compute_count == 1
    print(f"✓ First call computed (count={compute_count})")

    # Second call should use cache
    result2 = await cache.get_or_compute("compute_key", expensive_compute, ttl=60)
    assert result2 == "computed_value"
    assert compute_count == 1  # Should not have incremented
    print(f"✓ Second call used cache (count={compute_count})")

    # Test 4: Cache stats
    print("\nTest 4: Cache stats")
    stats = cache.get_stats()
    print(f"Cache size: {stats['size']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Cache misses: {stats['cache_misses']}")
    print(f"Hit rate: {stats['hit_rate']}")
    print("✓ Cache stats work")

    # Test 5: Clear cache
    print("\nTest 5: Clear cache")
    await cache.clear()
    result = await cache.get("test_key")
    assert result is None, "Cache should be empty after clear"
    print("✓ Cache clear works")

    print("\n✅ All cache tests passed!")


if __name__ == "__main__":
    asyncio.run(test_cache())
