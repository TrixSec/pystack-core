"""
Cache module - Multi-backend caching with automatic backend selection
"""

from py_core.cache.cache import Cache
from py_core.cache.interfaces import CacheBackend, CacheEntry

__all__ = [
    "Cache",
    "CacheBackend",
    "CacheEntry",
]
