"""
Performance benchmarks for pystack-core v0.1.0
"""

import pytest
import asyncio
import time
from datetime import datetime

from py_core import App, AppConfig
from py_core.config import Config
from py_core.logging import Logger, LogLevel


class TestLoggingPerformance:
    """Performance tests for logging system"""
    
    @pytest.mark.asyncio
    async def test_sync_logging_throughput(self):
        """Test synchronous logging throughput (target: 10,000+ logs/sec)"""
        logger = Logger(name="perf-test", level=LogLevel.INFO)
        
        # Benchmark sync logging
        start_time = time.time()
        for i in range(10000):
            logger.info(f"Performance test message {i}")
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = 10000 / duration
        
        print(f"Sync logging throughput: {throughput:.2f} logs/sec")
        print(f"Duration: {duration:.3f} seconds for 10,000 logs")
        
        # Should be able to handle at least 10,000 logs/sec
        assert throughput >= 10000, f"Logging throughput {throughput:.2f} logs/sec below target of 10,000 logs/sec"
    
    @pytest.mark.asyncio
    async def test_async_logging_throughput(self):
        """Test async logging throughput (target: 10,000+ logs/sec)"""
        logger = Logger(name="perf-test", level=LogLevel.INFO)
        logger.enable_async_logging(queue_size=20000)
        await logger.start_async()
        
        try:
            # Benchmark async logging
            start_time = time.time()
            for i in range(10000):
                await logger.ainfo(f"Async performance test message {i}")
            end_time = time.time()
            
            duration = end_time - start_time
            throughput = 10000 / duration
            
            print(f"Async logging throughput: {throughput:.2f} logs/sec")
            print(f"Duration: {duration:.3f} seconds for 10,000 logs")
            
            # Should be able to handle at least 10,000 logs/sec
            assert throughput >= 10000, f"Async logging throughput {throughput:.2f} logs/sec below target of 10,000 logs/sec"
        finally:
            await logger.stop_async()
    
    @pytest.mark.asyncio
    async def test_logging_with_context_overhead(self):
        """Test logging overhead with context injection"""
        logger = Logger(name="perf-test", level=LogLevel.INFO)
        logger.add_global_context(app_name="perf-test", version="1.0.0")
        
        # Benchmark logging with context
        start_time = time.time()
        for i in range(10000):
            logger.info(f"Message with context {i}", user_id=f"user{i}", request_id=f"req{i}")
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = 10000 / duration
        
        print(f"Logging with context throughput: {throughput:.2f} logs/sec")
        print(f"Duration: {duration:.3f} seconds for 10,000 logs with context")
        
        # Should still handle 10,000+ logs/sec even with context
        assert throughput >= 10000, f"Logging with context throughput {throughput:.2f} logs/sec below target"
    
    @pytest.mark.asyncio
    async def test_configuration_loading_performance(self):
        """Test configuration loading performance"""
        config = Config(AppConfig())
        
        # Benchmark config loading
        start_time = time.time()
        for i in range(1000):
            config._load_defaults()
            config._load_from_environment()
        end_time = time.time()
        
        duration = end_time - start_time
        operations_per_sec = 1000 / duration
        
        print(f"Config loading performance: {operations_per_sec:.2f} operations/sec")
        print(f"Duration: {duration:.3f} seconds for 1,000 config loads")
        
        # Should be able to load config 1000+ times per second
        assert operations_per_sec >= 1000, f"Config loading performance {operations_per_sec:.2f} ops/sec below target"


class TestContainerPerformance:
    """Performance tests for dependency injection container"""
    
    @pytest.mark.asyncio
    async def test_container_resolution_performance(self):
        """Test dependency resolution performance"""
        from py_core.container import Container
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        container = Container()
        container.register(TestService, TestService, singleton=True)
        
        # Benchmark dependency resolution
        start_time = time.time()
        for i in range(10000):
            service = container.resolve(TestService)
        end_time = time.time()
        
        duration = end_time - start_time
        resolutions_per_sec = 10000 / duration
        
        print(f"Container resolution performance: {resolutions_per_sec:.2f} resolutions/sec")
        print(f"Duration: {duration:.3f} seconds for 10,000 resolutions")
        
        # Should be able to resolve 10,000+ dependencies per second
        assert resolutions_per_sec >= 10000, f"Container resolution {resolutions_per_sec:.2f} res/sec below target"
    
    @pytest.mark.asyncio
    async def test_container_transient_resolution_performance(self):
        """Test transient (non-singleton) resolution performance"""
        from py_core.container import Container
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        container = Container()
        container.register(TestService, TestService, singleton=False)
        
        # Benchmark transient resolution
        start_time = time.time()
        for i in range(10000):
            service = container.resolve(TestService)
        end_time = time.time()
        
        duration = end_time - start_time
        resolutions_per_sec = 10000 / duration
        
        print(f"Transient resolution performance: {resolutions_per_sec:.2f} resolutions/sec")
        print(f"Duration: {duration:.3f} seconds for 10,000 transient resolutions")
        
        # Should still handle 10,000+ resolutions per second
        assert resolutions_per_sec >= 10000, f"Transient resolution {resolutions_per_sec:.2f} res/sec below target"


class TestAppLifecyclePerformance:
    """Performance tests for application lifecycle"""
    
    @pytest.mark.asyncio
    async def test_app_startup_performance(self):
        """Test application startup performance"""
        app = App()
        
        # Benchmark app startup
        start_time = time.time()
        await app.start()
        end_time = time.time()
        
        startup_time = end_time - start_time
        print(f"App startup time: {startup_time:.3f} seconds")
        
        # Should start in less than 1 second
        assert startup_time < 1.0, f"App startup time {startup_time:.3f}s exceeds target of 1.0s"
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_app_shutdown_performance(self):
        """Test application shutdown performance"""
        app = App()
        await app.start()
        
        # Benchmark app shutdown
        start_time = time.time()
        await app.stop()
        end_time = time.time()
        
        shutdown_time = end_time - start_time
        print(f"App shutdown time: {shutdown_time:.3f} seconds")
        
        # Should shutdown in less than 1 second
        assert shutdown_time < 1.0, f"App shutdown time {shutdown_time:.3f}s exceeds target of 1.0s"


class TestMemoryEfficiency:
    """Memory efficiency tests"""
    
    @pytest.mark.asyncio
    async def test_logger_memory_efficiency(self):
        """Test that logger doesn't leak memory"""
        import sys
        import gc
        
        logger = Logger(name="memory-test", level=LogLevel.INFO)
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Log many messages
        for i in range(100):
            logger.info(f"Memory test message {i}")
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_increase = final_objects - initial_objects
        print(f"Object increase after 100 logs: {object_increase}")
        
        # Object increase should be reasonable (less than 1000 new objects for 100 logs)
        # This is a baseline check - logging creates objects which is expected
        assert object_increase < 1000, f"Memory leak detected: {object_increase} new objects after logging"
    
    @pytest.mark.asyncio
    async def test_config_memory_efficiency(self):
        """Test that config doesn't leak memory"""
        import gc
        
        config = Config(AppConfig())
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Load config many times
        for i in range(100):
            config._load_defaults()
            config.reload()
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_increase = final_objects - initial_objects
        print(f"Object increase after 100 config loads: {object_increase}")
        
        # Object increase should be minimal
        assert object_increase < 200, f"Memory leak in config: {object_increase} new objects"


class TestMiddlewarePerformance:
    """Performance tests for middleware pipeline"""
    
    @pytest.mark.asyncio
    async def test_middleware_pipeline_performance(self):
        """Test middleware pipeline performance"""
        from py_core.middleware import MiddlewarePipeline, RequestIDMiddleware, TimingMiddleware
        
        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(RequestIDMiddleware())
        pipeline.add_middleware(TimingMiddleware())
        
        async def handler(request):
            return f"processed: {request}"
        
        # Benchmark middleware execution
        start_time = time.time()
        for i in range(10000):
            await pipeline.execute(f"request-{i}", handler)
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = 10000 / duration
        
        print(f"Middleware pipeline throughput: {throughput:.2f} requests/sec")
        print(f"Duration: {duration:.3f} seconds for 10,000 requests")
        
        # Should handle 10,000+ requests per second
        assert throughput >= 10000, f"Middleware throughput {throughput:.2f} req/sec below target"


class TestOverallPerformance:
    """Overall performance tests for v0.1.0 requirements"""
    
    @pytest.mark.asyncio
    async def test_v0_1_0_performance_requirements(self):
        """Test all v0.1.0 performance requirements"""
        print("\n=== v0.1.0 Performance Requirements Test ===")
        
        # Test 1: Logging performance (10,000+ logs/sec)
        logger = Logger(name="v0.1.0-test", level=LogLevel.INFO)
        start_time = time.time()
        for i in range(10000):
            logger.info(f"Test message {i}")
        logging_duration = time.time() - start_time
        logging_throughput = 10000 / logging_duration
        print(f"[OK] Logging: {logging_throughput:.2f} logs/sec (target: 10,000+)")
        assert logging_throughput >= 10000
        
        # Test 2: Config loading performance
        config = Config(AppConfig())
        start_time = time.time()
        for i in range(1000):
            config._load_defaults()
        config_duration = time.time() - start_time
        config_throughput = 1000 / config_duration
        print(f"[OK] Config loading: {config_throughput:.2f} loads/sec (target: 1,000+)")
        assert config_throughput >= 1000
        
        # Test 3: App startup performance
        app = App()
        start_time = time.time()
        await app.start()
        startup_duration = time.time() - start_time
        print(f"[OK] App startup: {startup_duration:.3f}s (target: <1.0s)")
        assert startup_duration < 1.0
        
        # Test 4: App shutdown performance
        start_time = time.time()
        await app.stop()
        shutdown_duration = time.time() - start_time
        print(f"[OK] App shutdown: {shutdown_duration:.3f}s (target: <1.0s)")
        assert shutdown_duration < 1.0
        
        print("=== All v0.1.0 performance requirements met ===\n")