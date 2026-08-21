"""
Cache Implementation with multiple backends
"""

import asyncio
import time
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib

from pystack_core.cache.interfaces import CacheInterface, CacheBackend, CacheStats


class MemoryCache(CacheInterface):
    """In-memory cache implementation with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple] = OrderedDict()
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if expiry and time.time() > expiry:
                del self._cache[key]
                self._stats.misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        async with self._lock:
            ttl = ttl or self._default_ttl
            expiry = time.time() + ttl if ttl else None
            
            # Evict if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)
            self._stats.sets += 1
            self._stats.size = len(self._cache)
    
    async def delete(self, key: str):
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.deletes += 1
                self._stats.size = len(self._cache)
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._stats.size = 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        async with self._lock:
            if key not in self._cache:
                return False
            
            _, expiry = self._cache[key]
            if expiry and time.time() > expiry:
                del self._cache[key]
                return False
            
            return True
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values in cache"""
        for key, value in mapping.items():
            await self.set(key, value, ttl)
    
    async def delete_many(self, keys: List[str]):
        """Delete multiple values from cache"""
        for key in keys:
            await self.delete(key)
    
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment value by delta"""
        async with self._lock:
            current = await self.get(key)
            if current is None:
                current = 0
            new_value = current + delta
            await self.set(key, new_value)
            return new_value
    
    async def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement value by delta"""
        async with self._lock:
            current = await self.get(key)
            if current is None:
                current = 0
            new_value = current - delta
            await self.set(key, new_value)
            return new_value
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._stats
    
    def reset_stats(self):
        """Reset cache statistics"""
        self._stats = CacheStats()


class RedisCache(CacheInterface):
    """Redis cache implementation (placeholder for actual Redis integration)"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._client = None
        self._stats = CacheStats()
        self._connected = False
    
    async def _connect(self):
        """Connect to Redis (placeholder)"""
        # In production, use aioredis or redis-py
        # For now, use memory cache as fallback
        if not self._connected:
            self._memory_cache = MemoryCache()
            self._connected = True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        await self._connect()
        return await self._memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        await self._connect()
        await self._memory_cache.set(key, value, ttl)
        self._stats.sets += 1
    
    async def delete(self, key: str):
        """Delete value from cache"""
        await self._connect()
        await self._memory_cache.delete(key)
        self._stats.deletes += 1
    
    async def clear(self):
        """Clear all cache entries"""
        await self._connect()
        await self._memory_cache.clear()
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        await self._connect()
        return await self._memory_cache.exists(key)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        await self._connect()
        return await self._memory_cache.get_many(keys)
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values in cache"""
        await self._connect()
        await self._memory_cache.set_many(mapping, ttl)
    
    async def delete_many(self, keys: List[str]):
        """Delete multiple values from cache"""
        await self._connect()
        await self._memory_cache.delete_many(keys)
    
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment value by delta"""
        await self._connect()
        return await self._memory_cache.increment(key, delta)
    
    async def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement value by delta"""
        await self._connect()
        return await self._memory_cache.decrement(key, delta)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._stats
    
    def reset_stats(self):
        """Reset cache statistics"""
        self._stats = CacheStats()


class DiskCache(CacheInterface):
    """Disk cache implementation using file storage"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 3600):
        self._cache_dir = cache_dir
        self._default_ttl = default_ttl
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
        import os
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self._cache_dir}/{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            file_path = self._get_file_path(key)
            
            if not await self._file_exists(file_path):
                self._stats.misses += 1
                return None
            
            try:
                import aiofiles
                async with aiofiles.open(file_path, 'r') as f:
                    data = await f.read()
                    cache_data = json.loads(data)
                
                # Check expiry
                if cache_data.get('expiry') and time.time() > cache_data['expiry']:
                    await self._delete_file(file_path)
                    self._stats.misses += 1
                    return None
                
                self._stats.hits += 1
                return cache_data['value']
            except:
                self._stats.misses += 1
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        async with self._lock:
            file_path = self._get_file_path(key)
            ttl = ttl or self._default_ttl
            expiry = time.time() + ttl if ttl else None
            
            cache_data = {
                'value': value,
                'expiry': expiry,
                'key': key
            }
            
            import aiofiles
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(cache_data))
            
            self._stats.sets += 1
    
    async def delete(self, key: str):
        """Delete value from cache"""
        async with self._lock:
            file_path = self._get_file_path(key)
            await self._delete_file(file_path)
            self._stats.deletes += 1
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            import os
            for filename in os.listdir(self._cache_dir):
                if filename.endswith('.cache'):
                    os.remove(f"{self._cache_dir}/{filename}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        file_path = self._get_file_path(key)
        return await self._file_exists(file_path)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values in cache"""
        for key, value in mapping.items():
            await self.set(key, value, ttl)
    
    async def delete_many(self, keys: List[str]):
        """Delete multiple values from cache"""
        for key in keys:
            await self.delete(key)
    
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment value by delta"""
        current = await self.get(key)
        if current is None:
            current = 0
        new_value = current + delta
        await self.set(key, new_value)
        return new_value
    
    async def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement value by delta"""
        current = await self.get(key)
        if current is None:
            current = 0
        new_value = current - delta
        await self.set(key, new_value)
        return new_value
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._stats
    
    def reset_stats(self):
        """Reset cache statistics"""
        self._stats = CacheStats()
    
    async def _file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(file_path)
    
    async def _delete_file(self, file_path: str):
        """Delete file"""
        import os
        if os.path.exists(file_path):
            os.remove(file_path)


class CacheManager:
    """Cache manager for automatic backend selection"""
    
    def __init__(self, default_backend: CacheBackend = CacheBackend.MEMORY):
        self._default_backend = default_backend
        self._backends: Dict[CacheBackend, CacheInterface] = {}
        self.register_backend(CacheBackend.MEMORY, MemoryCache())
    
    def register_backend(self, backend_type: CacheBackend, backend: CacheInterface):
        """Register a cache backend"""
        self._backends[backend_type] = backend
    
    def get_backend(self, backend_type: Optional[CacheBackend] = None) -> CacheInterface:
        """Get cache backend"""
        backend_type = backend_type or self._default_backend
        if backend_type not in self._backends:
            raise ValueError(f"Backend {backend_type} not registered")
        return self._backends[backend_type]
    
    async def get(self, key: str, backend: Optional[CacheBackend] = None) -> Optional[Any]:
        """Get value from cache"""
        cache = self.get_backend(backend)
        return await cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, backend: Optional[CacheBackend] = None):
        """Set value in cache"""
        cache = self.get_backend(backend)
        await cache.set(key, value, ttl)
    
    async def delete(self, key: str, backend: Optional[CacheBackend] = None):
        """Delete value from cache"""
        cache = self.get_backend(backend)
        await cache.delete(key)
    
    async def clear(self, backend: Optional[CacheBackend] = None):
        """Clear cache"""
        cache = self.get_backend(backend)
        await cache.clear()
    
    def get_all_stats(self) -> Dict[CacheBackend, CacheStats]:
        """Get statistics for all backends"""
        return {backend: cache.get_stats() for backend, cache in self._backends.items()}
