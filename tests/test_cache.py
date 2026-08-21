"""
Tests for Cache module
"""

import pytest
import asyncio
from pystack_core.cache.cache import (
    MemoryCache, RedisCache, DiskCache, CacheManager
)
from pystack_core.cache.interfaces import (
    CacheInterface, CacheBackend, CacheStats
)


class TestMemoryCache:
    """Test memory cache implementation"""
    
    @pytest.mark.asyncio
    async def test_memory_cache_initialization(self):
        """Test memory cache initialization"""
        cache = MemoryCache(max_size=100, default_ttl=3600)
        assert cache._max_size == 100
        assert cache._default_ttl == 3600
    
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test set and get operations"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """Test getting nonexistent key"""
        cache = MemoryCache()
        value = await cache.get("nonexistent")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_delete(self):
        """Test delete operation"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        await cache.delete("key1")
        value = await cache.get("key1")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clear operation"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_exists(self):
        """Test exists operation"""
        cache = MemoryCache()
        assert await cache.exists("key1") is False
        await cache.set("key1", "value1")
        assert await cache.exists("key1") is True
    
    @pytest.mark.asyncio
    async def test_get_many(self):
        """Test get many operation"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        
        result = await cache.get_many(["key1", "key2", "key4"])
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert "key4" not in result
    
    @pytest.mark.asyncio
    async def test_set_many(self):
        """Test set many operation"""
        cache = MemoryCache()
        mapping = {"key1": "value1", "key2": "value2"}
        await cache.set_many(mapping)
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
    
    @pytest.mark.asyncio
    async def test_increment(self):
        """Test increment operation"""
        cache = MemoryCache()
        result = await cache.increment("counter", 5)
        assert result == 5
        result = await cache.increment("counter", 3)
        assert result == 8
    
    @pytest.mark.asyncio
    async def test_decrement(self):
        """Test decrement operation"""
        cache = MemoryCache()
        result = await cache.decrement("counter", 5)
        assert result == -5
        result = await cache.decrement("counter", 2)
        assert result == -7
    
    @pytest.mark.asyncio
    async def test_ttl_expiry(self):
        """Test TTL expiry with very short timeout"""
        cache = MemoryCache(default_ttl=0.1)
        await cache.set("key1", "value1", ttl=0.1)
        await asyncio.sleep(0.2)
        value = await cache.get("key1")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """Test LRU eviction"""
        cache = MemoryCache(max_size=2)
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")  # Should evict key1
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"
    
    @pytest.mark.asyncio
    async def test_stats(self):
        """Test statistics"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        await cache.get("key1")
        await cache.get("key2")  # miss
        
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.sets == 1
        assert stats.hit_rate == 0.5
    
    @pytest.mark.asyncio
    async def test_stats_reset(self):
        """Test statistics reset"""
        cache = MemoryCache()
        await cache.set("key1", "value1")
        cache.reset_stats()
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0


class TestCacheManager:
    """Test cache manager"""
    
    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self):
        """Test cache manager initialization"""
        manager = CacheManager()
        assert manager._default_backend == CacheBackend.MEMORY
    
    @pytest.mark.asyncio
    async def test_get_backend(self):
        """Test getting backend"""
        manager = CacheManager()
        backend = manager.get_backend(CacheBackend.MEMORY)
        assert isinstance(backend, MemoryCache)
    
    @pytest.mark.asyncio
    async def test_manager_operations(self):
        """Test cache manager operations"""
        manager = CacheManager()
        await manager.set("key1", "value1")
        value = await manager.get("key1")
        assert value == "value1"
        await manager.delete("key1")
        assert await manager.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_register_backend(self):
        """Test registering custom backend"""
        manager = CacheManager()
        custom_cache = MemoryCache(max_size=500)
        manager.register_backend(CacheBackend.MEMORY, custom_cache)
        backend = manager.get_backend(CacheBackend.MEMORY)
        assert backend._max_size == 500


class TestCacheInterfaces:
    """Test cache interfaces"""
    
    def test_cache_backend_enum(self):
        """Test cache backend enum"""
        assert CacheBackend.MEMORY.value == "memory"
        assert CacheBackend.REDIS.value == "redis"
        assert CacheBackend.DISK.value == "disk"
    
    def test_cache_stats_dataclass(self):
        """Test cache stats dataclass"""
        stats = CacheStats(hits=10, misses=5)
        assert stats.hit_rate == 0.6666666666666666
        assert stats.hits == 10
        assert stats.misses == 5


class TestDiskCache:
    """Test disk cache implementation"""
    
    @pytest.mark.asyncio
    async def test_disk_cache_initialization(self):
        """Test disk cache initialization"""
        cache = DiskCache(cache_dir=".test_cache")
        assert cache._cache_dir == ".test_cache"
    
    @pytest.mark.asyncio
    async def test_disk_cache_operations(self):
        """Test disk cache operations"""
        cache = DiskCache(cache_dir=".test_cache")
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"
        await cache.delete("key1")
        value = await cache.get("key1")
        assert value is None
        await cache.clear()
    
    @pytest.mark.asyncio
    async def test_disk_cache_cleanup(self):
        """Test disk cache cleanup"""
        import os
        cache = DiskCache(cache_dir=".test_cache")
        await cache.clear()
        if os.path.exists(".test_cache"):
            os.rmdir(".test_cache")
