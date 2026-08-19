"""
Production-ready tests for pystack-core App class
"""

import pytest
import asyncio
from py_core.app import App, AppConfig
from py_core.config import Config
from py_core.container import Container
from py_core.middleware import MiddlewarePipeline


class TestAppInitialization:
    """Test application initialization"""
    
    def test_app_initialization(self):
        """Test basic app initialization"""
        app = App()
        assert app.config is not None
        assert app._container is not None
        assert app._middleware is not None
        assert app._started is False
    
    def test_app_with_custom_config(self):
        """Test app initialization with custom config"""
        config = AppConfig(name="custom-app", environment="production", debug=True)
        app = App(config=config)
        assert app.config._app_config.name == "custom-app"
        assert app.config._app_config.environment == "production"
        assert app.config._app_config.debug is True
    
    def test_app_config_properties(self):
        """Test app config properties"""
        config = AppConfig(
            name="test-app",
            environment="staging",
            debug=True,
            log_level="DEBUG",
            enable_metrics=True
        )
        app = App(config=config)
        
        assert app._app_config.name == "test-app"
        assert app._app_config.environment == "staging"
        assert app._app_config.debug is True
        assert app._app_config.log_level == "DEBUG"
        assert app._app_config.enable_metrics is True


class TestAppLifecycle:
    """Test application lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_app_start_stop(self):
        """Test app start and stop lifecycle"""
        app = App()
        assert app._started is False
        
        await app.start()
        assert app._started is True
        assert app.config._loaded is True
        
        await app.stop()
        assert app._started is False
    
    @pytest.mark.asyncio
    async def test_app_double_start(self):
        """Test that double start doesn't cause issues"""
        app = App()
        await app.start()
        await app.start()  # Should not raise error
        assert app._started is True
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_app_stop_without_start(self):
        """Test stopping app without starting"""
        app = App()
        await app.stop()  # Should not raise error
        assert app._started is False
    
    @pytest.mark.asyncio
    async def test_lifespan_context_manager(self):
        """Test lifespan context manager"""
        app = App()
        
        async with app.lifespan():
            assert app._started is True
        
        assert app._started is False


class TestHooks:
    """Test startup and shutdown hooks"""
    
    @pytest.mark.asyncio
    async def test_startup_hook(self):
        """Test startup hook execution"""
        app = App()
        hook_executed = False
        
        def startup_hook(app_instance):
            nonlocal hook_executed
            hook_executed = True
        
        app.add_startup_hook(startup_hook)
        await app.start()
        
        assert hook_executed is True
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_async_startup_hook(self):
        """Test async startup hook execution"""
        app = App()
        hook_executed = False
        
        async def async_startup_hook(app_instance):
            nonlocal hook_executed
            hook_executed = True
            await asyncio.sleep(0.01)
        
        app.add_startup_hook(async_startup_hook)
        await app.start()
        
        assert hook_executed is True
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_shutdown_hook(self):
        """Test shutdown hook execution"""
        app = App()
        hook_executed = False
        
        def shutdown_hook(app_instance):
            nonlocal hook_executed
            hook_executed = True
        
        app.add_shutdown_hook(shutdown_hook)
        await app.start()
        await app.stop()
        
        assert hook_executed is True
    
    @pytest.mark.asyncio
    async def test_hooks_execution_order(self):
        """Test that hooks execute in correct order"""
        app = App()
        execution_order = []
        
        app.add_startup_hook(lambda a: execution_order.append("startup1"))
        app.add_startup_hook(lambda a: execution_order.append("startup2"))
        app.add_shutdown_hook(lambda a: execution_order.append("shutdown1"))
        app.add_shutdown_hook(lambda a: execution_order.append("shutdown2"))
        
        await app.start()
        await app.stop()
        
        assert execution_order == ["startup1", "startup2", "shutdown2", "shutdown1"]


class TestDependencyInjection:
    """Test dependency injection functionality"""
    
    @pytest.mark.asyncio
    async def test_service_registration(self):
        """Test service registration in container"""
        app = App()
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        app.register_service(TestService, TestService, singleton=True)
        await app.start()
        
        service = app._container.resolve(TestService)
        assert service.value == "test"
        
        # Test singleton behavior
        service2 = app._container.resolve(TestService)
        assert service is service2
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_instance_registration(self):
        """Test instance registration"""
        app = App()
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        instance = TestService()
        app.register_instance(TestService, instance)
        await app.start()
        
        resolved = app._container.resolve(TestService)
        assert resolved is instance
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_core_services_registered(self):
        """Test that core services are registered"""
        app = App()
        await app.start()
        
        assert app._container.is_registered(Config)
        assert app._container.is_registered(MiddlewarePipeline)
        assert app._container.is_registered(App)
        
        await app.stop()


class TestContextManagement:
    """Test application context management"""
    
    @pytest.mark.asyncio
    async def test_context_operations(self):
        """Test setting and getting context values"""
        app = App()
        
        app.set_context("user_id", "12345")
        app.set_context("request_id", "abcde")
        
        assert app.get_context("user_id") == "12345"
        assert app.get_context("request_id") == "abcde"
        assert app.get_context("nonexistent") is None
        assert app.get_context("nonexistent", "default") == "default"
    
    @pytest.mark.asyncio
    async def test_context_with_lifecycle(self):
        """Test context persists through lifecycle"""
        app = App()
        
        app.set_context("test_key", "test_value")
        await app.start()
        
        assert app.get_context("test_key") == "test_value"
        
        await app.stop()
        assert app.get_context("test_key") == "test_value"  # Context persists


class TestMiddleware:
    """Test middleware functionality"""
    
    @pytest.mark.asyncio
    async def test_middleware_pipeline_access(self):
        """Test access to middleware pipeline"""
        app = App()
        await app.start()
        
        assert app.middleware is not None
        assert isinstance(app.middleware, MiddlewarePipeline)
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_execute_with_middleware(self):
        """Test executing request through middleware"""
        app = App()
        await app.start()
        
        async def handler(request):
            return f"processed: {request}"
        
        result = await app.execute_with_middleware("test-request", handler)
        assert result == "processed: test-request"
        
        await app.stop()


class TestLoggerAccess:
    """Test logger access and configuration"""
    
    @pytest.mark.asyncio
    async def test_logger_property(self):
        """Test logger property access"""
        app = App()
        await app.start()
        
        logger = app.logger
        assert logger is not None
        assert logger.name == app._app_config.name
        
        await app.stop()
    
    @pytest.mark.asyncio
    async def test_logger_level_from_config(self):
        """Test that logger level respects config"""
        config = AppConfig(name="test-app", log_level="DEBUG")
        app = App(config=config)
        await app.start()
        
        from py_core.logging import LogLevel
        assert app.logger.level == LogLevel.DEBUG
        
        await app.stop()


class TestRunMethod:
    """Test the run method for main coroutine execution"""
    
    @pytest.mark.asyncio
    async def test_run_with_main_coroutine(self):
        """Test running app with main coroutine"""
        app = App()
        
        async def main_coroutine(app_instance):
            assert app_instance is app
            return "success"
        
        result = await app.run(main_coroutine)
        assert result == "success"
        assert app._started is False  # Should be stopped after run


class TestErrorHandling:
    """Test error handling in app lifecycle"""
    
    @pytest.mark.asyncio
    async def test_shutdown_hook_error_handling(self):
        """Test that errors in shutdown hooks don't prevent other hooks"""
        app = App()
        execution_order = []
        
        def failing_hook(app_instance):
            execution_order.append("failing")
            raise RuntimeError("Test error")
        
        def working_hook(app_instance):
            execution_order.append("working")
        
        app.add_shutdown_hook(failing_hook)
        app.add_shutdown_hook(working_hook)
        
        await app.start()
        await app.stop()  # Should not raise despite error
        
        assert "failing" in execution_order
        assert "working" in execution_order


class TestContainerIntegration:
    """Test container integration with app"""
    
    @pytest.mark.asyncio
    async def test_container_reset_on_stop(self):
        """Test that container is reset on app stop"""
        app = App()
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        app.register_service(TestService, TestService)
        await app.start()
        
        # Resolve service
        service = app._container.resolve(TestService)
        assert service is not None
        
        await app.stop()
        
        # Container should be reset
        assert len(app._container._instances) == 0