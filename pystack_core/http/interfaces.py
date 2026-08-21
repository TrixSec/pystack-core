"""
HTTP Client Interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class HTTPRequest:
    """HTTP request data"""
    method: HTTPMethod
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[float] = None
    auth: Optional[tuple] = None


@dataclass
class HTTPResponse:
    """HTTP response data"""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]] = None
    elapsed: float = 0.0
    success: bool = False


class HttpClientInterface(ABC):
    """Interface for HTTP client implementations"""
    
    @abstractmethod
    async def request(self, request: HTTPRequest) -> HTTPResponse:
        """Execute HTTP request"""
        pass
    
    @abstractmethod
    async def get(self, url: str, **kwargs) -> HTTPResponse:
        """Execute GET request"""
        pass
    
    @abstractmethod
    async def post(self, url: str, **kwargs) -> HTTPResponse:
        """Execute POST request"""
        pass
    
    @abstractmethod
    async def put(self, url: str, **kwargs) -> HTTPResponse:
        """Execute PUT request"""
        pass
    
    @abstractmethod
    async def delete(self, url: str, **kwargs) -> HTTPResponse:
        """Execute DELETE request"""
        pass
    
    @abstractmethod
    async def patch(self, url: str, **kwargs) -> HTTPResponse:
        """Execute PATCH request"""
        pass
    
    @abstractmethod
    def add_auth(self, auth_type: str, **config):
        """Add authentication method"""
        pass
    
    @abstractmethod
    def add_middleware(self, middleware: Callable):
        """Add request/response middleware"""
        pass
    
    @abstractmethod
    def set_timeout(self, timeout: float):
        """Set default timeout"""
        pass
    
    @abstractmethod
    def set_retry_policy(self, max_retries: int, backoff_factor: float):
        """Configure retry policy"""
        pass


class CacheInterface(ABC):
    """Interface for cache implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
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
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def get_many(self, keys: list) -> Dict[str, Any]:
        """Get multiple values"""
        pass
    
    @abstractmethod
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None):
        """Set multiple values"""
        pass


class DatabaseInterface(ABC):
    """Interface for database implementations"""
    
    @abstractmethod
    async def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[tuple] = None):
        """Execute SQL query"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> list:
        """Fetch all rows"""
        pass
    
    @abstractmethod
    async def begin_transaction(self):
        """Begin transaction"""
        pass
    
    @abstractmethod
    async def commit_transaction(self):
        """Commit transaction"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self):
        """Rollback transaction"""
        pass
