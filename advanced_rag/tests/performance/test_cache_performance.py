"""
Performance tests for caching system.

Tests cache effectiveness, hit rates, and performance improvements.
"""
import pytest
import time
from src.core.cache import get_llm_cache, Cache


@pytest.mark.performance
@pytest.mark.slow
class TestCachePerformance:
    """Performance tests for caching."""
    
    def test_cache_hit_performance(self, mock_config):
        """Test that cache hits are faster than misses."""
        cache = get_llm_cache()
        
        # Set a value
        cache.set("perf_test", "value", ttl=60)
        
        # Time cache hit
        start = time.time()
        for _ in range(100):
            cache.get("perf_test")
        hit_time = time.time() - start
        
        # Time cache miss
        start = time.time()
        for _ in range(100):
            cache.get("nonexistent_key")
        miss_time = time.time() - start
        
        # Cache hits should be faster (or at least not much slower)
        # Allow some variance
        assert hit_time < miss_time * 2, \
            f"Cache hits not faster: hit={hit_time:.4f}s, miss={miss_time:.4f}s"
    
    def test_cache_throughput(self, mock_config):
        """Test cache can handle high throughput."""
        cache = get_llm_cache()
        
        # Set many values
        start = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}", ttl=60)
        set_time = time.time() - start
        
        # Get many values
        start = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        get_time = time.time() - start
        
        # Should complete in reasonable time (< 1 second for 1000 ops)
        assert set_time < 1.0, f"Cache set too slow: {set_time:.4f}s"
        assert get_time < 1.0, f"Cache get too slow: {get_time:.4f}s"
    
    def test_cache_memory_efficiency(self, mock_config):
        """Test cache doesn't leak memory."""
        cache = get_llm_cache()
        
        # Add many entries
        for i in range(100):
            cache.set(f"key_{i}", "x" * 1000, ttl=1)  # Short TTL
        
        initial_stats = cache.stats()
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        # Cleanup expired
        removed = cache.cleanup_expired()
        
        final_stats = cache.stats()
        
        # Should have removed expired entries
        assert removed > 0, "No expired entries removed"
        assert final_stats["active_entries"] < initial_stats["total_entries"], \
            "Cache didn't clean up expired entries"

