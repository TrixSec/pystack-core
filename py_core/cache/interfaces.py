"""
Cache interfaces - Base interfaces for cache module
"""

from typing import Any, Optional
from datetime import timedelta
from enum import Enum
from dataclasses import dataclass


class CacheBackend(Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    ttl: Optional[timedelta] = None
    created_at: Optional[float] = None
