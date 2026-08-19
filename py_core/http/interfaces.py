"""
HTTP interfaces - Base interfaces and enums for HTTP module
"""

from typing import Any, Dict, Optional
from enum import Enum


class HttpMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpResponse:
    """HTTP response wrapper"""
    
    def __init__(self, status_code: int, headers: Dict[str, str], content: Any):
        self.status_code = status_code
        self.headers = headers
        self.content = content
    
    @property
    def json(self) -> Any:
        """Parse response as JSON"""
        import json
        return json.loads(self.content)
    
    @property
    def text(self) -> str:
        """Get response as text"""
        return str(self.content)
