"""
HTTP Client Example - demonstrating retry, timeout, and metrics
"""

import asyncio
from pystack_core import HttpClient, HTTPMethod, RetryPolicy, CircuitBreaker

async def basic_http_example():
    """Basic HTTP client usage"""
    print("=== Basic HTTP Client Example ===")
    
    client = HttpClient(timeout=30.0)
    
    try:
        # Simple GET request
        response = await client.get("https://httpbin.org/get")
        print(f"Status: {response.status_code}")
        print(f"Success: {response.success}")
        
        # POST request with JSON data
        response = await client.post(
            "https://httpbin.org/post",
            json_data={"name": "John", "age": 30}
        )
        print(f"POST Status: {response.status_code}")
        
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        await client.close()

async def retry_policy_example():
    """HTTP client with custom retry policy"""
    print("\n=== Retry Policy Example ===")
    
    retry_policy = RetryPolicy(
        max_retries=5,
        backoff_factor=2.0,
        retry_on_status_codes=[500, 502, 503, 504]
    )
    
    client = HttpClient(timeout=10.0, retry_policy=retry_policy)
    
    try:
        response = await client.get("https://httpbin.org/get")
        print(f"Request completed with retry policy")
        print(f"Metrics: {client.get_metrics()}")
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        await client.close()

async def authentication_example():
    """HTTP client with authentication"""
    print("\n=== Authentication Example ===")
    
    client = HttpClient(timeout=30.0)
    
    # Basic authentication
    client.add_auth("basic", username="user", password="pass")
    print("Basic auth configured")
    
    # Bearer token authentication
    client.add_auth("bearer", token="your-api-token")
    print("Bearer token configured")
    
    await client.close()

async def circuit_breaker_example():
    """Circuit breaker for fault tolerance"""
    print("\n=== Circuit Breaker Example ===")
    
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
    
    async def failing_request():
        raise Exception("Service unavailable")
    
    async def successful_request():
        return {"status": "ok"}
    
    # Test circuit breaker
    for i in range(4):
        try:
            result = await breaker.call(successful_request if i == 3 else failing_request)
            print(f"Request {i+1}: Success")
        except Exception as e:
            print(f"Request {i+1}: Failed - {e}")
    
    print(f"Circuit breaker state: {breaker._state}")

async def metrics_example():
    """HTTP client metrics collection"""
    print("\n=== Metrics Example ===")
    
    client = HttpClient(timeout=30.0, enable_metrics=True)
    
    try:
        # Make some requests
        for i in range(3):
            try:
                await client.get("https://httpbin.org/get")
            except:
                pass
        
        # Get metrics
        metrics = client.get_metrics()
        print(f"Total requests: {metrics['requests_total']}")
        print(f"Successful: {metrics['requests_success']}")
        print(f"Errors: {metrics['requests_error']}")
        print(f"Total latency: {metrics['total_latency']:.3f}s")
        print(f"Requests by status: {metrics['requests_by_status']}")
        
    finally:
        await client.close()

async def main():
    """Run all examples"""
    await basic_http_example()
    await retry_policy_example()
    await authentication_example()
    await circuit_breaker_example()
    await metrics_example()

if __name__ == "__main__":
    asyncio.run(main())
