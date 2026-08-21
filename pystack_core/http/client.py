"""
HTTP Client Implementation with retry, timeout, and metrics
"""

import asyncio
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
import httpx

from pystack_core.http.interfaces import (
    HttpClientInterface, HTTPRequest, HTTPResponse, HTTPMethod
)


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_retries: int = 3
    backoff_factor: float = 2.0
    retry_on_status_codes: List[int] = field(default_factory=lambda: [500, 502, 503, 504])
    retry_on_exceptions: List[type] = field(default_factory=lambda: [httpx.TimeoutException, httpx.ConnectError])


class HttpClient(HttpClientInterface):
    """Production-ready HTTP client with retry, timeout, and metrics"""
    
    def __init__(
        self,
        timeout: float = 30.0,
        retry_policy: Optional[RetryPolicy] = None,
        enable_metrics: bool = True,
        enable_tracing: bool = False
    ):
        self._timeout = timeout
        self._retry_policy = retry_policy or RetryPolicy()
        self._enable_metrics = enable_metrics
        self._enable_tracing = enable_tracing
        
        # HTTP client configuration
        self._client = httpx.AsyncClient(timeout=timeout)
        
        # Metrics
        self._metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "requests_by_status": {},
            "total_latency": 0.0
        }
        
        # Middleware chain
        self._middleware: List[Callable] = []
        
        # Authentication
        self._auth = None
        self._bearer_token = None
    
    async def request(self, request: HTTPRequest) -> HTTPResponse:
        """Execute HTTP request with retry logic"""
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self._retry_policy.max_retries + 1):
            try:
                # Apply middleware
                for middleware in self._middleware:
                    request = await self._apply_middleware(middleware, request)
                
                # Execute request
                response = await self._execute_request(request)
                
                # Check if we should retry
                if attempt < self._retry_policy.max_retries:
                    if self._should_retry(response):
                        await asyncio.sleep(self._retry_policy.backoff_factor ** attempt)
                        continue
                
                # Update metrics
                self._update_metrics(response, time.time() - start_time)
                
                return response
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry on exception
                if attempt < self._retry_policy.max_retries and self._should_retry_on_exception(e):
                    await asyncio.sleep(self._retry_policy.backoff_factor ** attempt)
                    continue
                
                # Update error metrics
                self._metrics["requests_error"] += 1
                self._metrics["requests_total"] += 1
                
                raise HTTPError(f"HTTP request failed after {attempt + 1} attempts: {str(e)}") from e
    
    async def _execute_request(self, request: HTTPRequest) -> HTTPResponse:
        """Execute the actual HTTP request"""
        method = request.method.value
        headers = request.headers or {}
        params = request.params
        json_data = request.json_data
        data = request.data
        timeout = request.timeout or self._timeout
        auth = request.auth or self._auth
        
        # Add bearer token if present
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        
        response = await self._client.request(
            method=method,
            url=request.url,
            headers=headers,
            params=params,
            json=json_data,
            content=data,
            timeout=timeout,
            auth=auth
        )
        
        return HTTPResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            text=response.text,
            json_data=self._parse_json(response),
            elapsed=response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0.0,
            success=200 <= response.status_code < 300
        )
    
    def _parse_json(self, response) -> Optional[Dict[str, Any]]:
        """Parse JSON response if content-type indicates JSON"""
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except:
                return None
        return None
    
    def _should_retry(self, response: HTTPResponse) -> bool:
        """Check if response should trigger retry"""
        return response.status_code in self._retry_policy.retry_on_status_codes
    
    def _should_retry_on_exception(self, exception: Exception) -> bool:
        """Check if exception should trigger retry"""
        return any(isinstance(exception, exc_type) for exc_type in self._retry_policy.retry_on_exceptions)
    
    async def _apply_middleware(self, middleware: Callable, request: HTTPRequest) -> HTTPRequest:
        """Apply middleware to request"""
        if asyncio.iscoroutinefunction(middleware):
            return await middleware(request)
        else:
            return middleware(request)
    
    def _update_metrics(self, response: HTTPResponse, latency: float):
        """Update request metrics"""
        self._metrics["requests_total"] += 1
        self._metrics["total_latency"] += latency
        
        if response.success:
            self._metrics["requests_success"] += 1
        else:
            self._metrics["requests_error"] += 1
        
        status_key = str(response.status_code)
        self._metrics["requests_by_status"][status_key] = self._metrics["requests_by_status"].get(status_key, 0) + 1
    
    async def get(self, url: str, **kwargs) -> HTTPResponse:
        """Execute GET request"""
        request = HTTPRequest(method=HTTPMethod.GET, url=url, **kwargs)
        return await self.request(request)
    
    async def post(self, url: str, **kwargs) -> HTTPResponse:
        """Execute POST request"""
        request = HTTPRequest(method=HTTPMethod.POST, url=url, **kwargs)
        return await self.request(request)
    
    async def put(self, url: str, **kwargs) -> HTTPResponse:
        """Execute PUT request"""
        request = HTTPRequest(method=HTTPMethod.PUT, url=url, **kwargs)
        return await self.request(request)
    
    async def delete(self, url: str, **kwargs) -> HTTPResponse:
        """Execute DELETE request"""
        request = HTTPRequest(method=HTTPMethod.DELETE, url=url, **kwargs)
        return await self.request(request)
    
    async def patch(self, url: str, **kwargs) -> HTTPResponse:
        """Execute PATCH request"""
        request = HTTPRequest(method=HTTPMethod.PATCH, url=url, **kwargs)
        return await self.request(request)
    
    def add_auth(self, auth_type: str, **config):
        """Add authentication method"""
        if auth_type == "basic":
            username = config.get("username")
            password = config.get("password")
            self._auth = (username, password)
        elif auth_type == "bearer":
            token = config.get("token")
            # Store bearer token as a custom header
            self._bearer_token = token
    
    def add_middleware(self, middleware: Callable):
        """Add request/response middleware"""
        self._middleware.append(middleware)
    
    def set_timeout(self, timeout: float):
        """Set default timeout"""
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
    
    def set_retry_policy(self, max_retries: int, backoff_factor: float):
        """Configure retry policy"""
        self._retry_policy = RetryPolicy(max_retries=max_retries, backoff_factor=backoff_factor)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self._metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self._metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "requests_by_status": {},
            "total_latency": 0.0
        }
    
    async def close(self):
        """Close HTTP client"""
        await self._client.aclose()


class HTTPError(Exception):
    """HTTP client error"""
    pass


# Circuit breaker implementation
class CircuitBreaker:
    """Circuit breaker for HTTP requests"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self._state == "open":
            if self._should_attempt_reset():
                self._state = "half-open"
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self._recovery_timeout
    
    def _on_success(self):
        """Handle successful request"""
        self._failure_count = 0
        if self._state == "half-open":
            self._state = "closed"
    
    def _on_failure(self):
        """Handle failed request"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self._failure_threshold:
            self._state = "open"


class CircuitBreakerError(Exception):
    """Circuit breaker error"""
    pass
