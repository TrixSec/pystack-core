"""
HTTP module - Production-ready HTTP client with retry, timeout, and metrics
"""

from .client import HttpClient, RetryPolicy, CircuitBreaker, CircuitBreakerError, HTTPError
from .interfaces import HttpClientInterface, HTTPRequest, HTTPResponse, HTTPMethod

__all__ = [
    "HttpClient",
    "RetryPolicy",
    "CircuitBreaker",
    "CircuitBreakerError",
    "HTTPError",
    "HttpClientInterface",
    "HTTPRequest",
    "HTTPResponse",
    "HTTPMethod",
]