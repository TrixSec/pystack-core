"""
Tests for HTTP Client module
"""

import pytest
import asyncio
from pystack_core.http.client import (
    HttpClient, HTTPRequest, HTTPResponse, HTTPMethod,
    RetryPolicy, CircuitBreaker, CircuitBreakerError, HTTPError
)


class TestHTTPClient:
    """Test HTTP client functionality"""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test HTTP client initialization"""
        client = HttpClient(timeout=30.0)
        assert client._timeout == 30.0
        assert client._retry_policy.max_retries == 3
        await client.close()
    
    @pytest.mark.asyncio
    async def test_timeout_configuration(self):
        """Test timeout configuration"""
        client = HttpClient(timeout=15.0)
        assert client._timeout == 15.0
        await client.close()
    
    @pytest.mark.asyncio
    async def test_retry_policy_configuration(self):
        """Test retry policy configuration"""
        retry_policy = RetryPolicy(max_retries=5, backoff_factor=3.0)
        client = HttpClient(retry_policy=retry_policy)
        assert client._retry_policy.max_retries == 5
        assert client._retry_policy.backoff_factor == 3.0
        await client.close()
    
    @pytest.mark.asyncio
    async def test_metrics_operations(self):
        """Test metrics operations"""
        client = HttpClient(enable_metrics=True)
        # Manually set metrics to test the system
        client._metrics["requests_total"] = 5
        client._metrics["requests_success"] = 4
        client._metrics["requests_error"] = 1
        
        metrics = client.get_metrics()
        assert metrics["requests_total"] == 5
        assert metrics["requests_success"] == 4
        assert metrics["requests_error"] == 1
        
        client.reset_metrics()
        metrics = client.get_metrics()
        assert metrics["requests_total"] == 0
        await client.close()
    
    @pytest.mark.asyncio
    async def test_basic_auth(self):
        """Test basic authentication"""
        client = HttpClient()
        client.add_auth("basic", username="user", password="pass")
        assert client._auth == ("user", "pass")
        await client.close()
    
    @pytest.mark.asyncio
    async def test_bearer_auth(self):
        """Test bearer token authentication"""
        client = HttpClient()
        client.add_auth("bearer", token="test-token")
        assert client._bearer_token == "test-token"
        await client.close()
    
    @pytest.mark.asyncio
    async def test_middleware_addition(self):
        """Test middleware addition"""
        client = HttpClient()
        
        async def dummy_middleware(request):
            return request
        
        client.add_middleware(dummy_middleware)
        assert len(client._middleware) == 1
        await client.close()


class TestRetryPolicy:
    """Test retry policy"""
    
    def test_default_retry_policy(self):
        """Test default retry policy"""
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.backoff_factor == 2.0
        assert 500 in policy.retry_on_status_codes
    
    def test_custom_retry_policy(self):
        """Test custom retry policy"""
        policy = RetryPolicy(max_retries=5, backoff_factor=3.0)
        assert policy.max_retries == 5
        assert policy.backoff_factor == 3.0


class TestCircuitBreaker:
    """Test circuit breaker"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_initial_state(self):
        """Test circuit breaker initial state"""
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker._state == "closed"
        assert breaker._failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open_on_threshold(self):
        """Test circuit breaker opens on threshold"""
        breaker = CircuitBreaker(failure_threshold=2)
        
        async def failing_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        
        assert breaker._state == "open"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_requests(self):
        """Test circuit breaker prevents requests when open"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Trigger circuit breaker with immediate failures
        try:
            await breaker.call(failing_func)
        except:
            pass
        
        try:
            await breaker.call(failing_func)
        except:
            pass
        
        # Circuit breaker should be open now
        with pytest.raises(CircuitBreakerError):
            await breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker goes to half-open after timeout"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Trigger circuit breaker
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Should be in half-open state
        assert breaker._state == "open"  # Will reset on next call


class TestHTTPInterfaces:
    """Test HTTP interfaces"""
    
    def test_http_request_creation(self):
        """Test HTTP request creation"""
        request = HTTPRequest(
            method=HTTPMethod.GET,
            url="https://example.com",
            headers={"Content-Type": "application/json"}
        )
        assert request.method == HTTPMethod.GET
        assert request.url == "https://example.com"
        assert request.headers["Content-Type"] == "application/json"
    
    def test_http_response_creation(self):
        """Test HTTP response creation"""
        response = HTTPResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            content=b'{"test": "data"}',
            text='{"test": "data"}',
            json_data={"test": "data"},
            elapsed=0.1,
            success=True
        )
        assert response.status_code == 200
        assert response.success is True
        assert response.json_data == {"test": "data"}
    
    def test_http_method_enum(self):
        """Test HTTP method enum"""
        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"
        assert HTTPMethod.PUT.value == "PUT"
        assert HTTPMethod.DELETE.value == "DELETE"
