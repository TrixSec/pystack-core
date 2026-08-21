"""
Cache Interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class CacheBackend(Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class CacheInterface(ABC):
    """Interface for cache implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def clear(self):
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        pass
    
    @abstractmethod
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values in cache"""
        pass
    
    @abstractmethod
    async def delete_many(self, keys: List[str]):
        """Delete multiple values from cache"""
        pass
    
    @abstractmethod
    async def increment(self, key: str, delta: int = 1) -> int:
        """Increment value by delta"""
        pass
    
    @abstractmethod
    async def decrement(self, key: str, delta: int = 1) -> int:
        """Decrement value by delta"""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        pass
    
    @abstractmethod
    def reset_stats(self):
        """Reset cache statistics"""
        pass
