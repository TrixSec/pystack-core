"""
Core App class - Production-ready central orchestrator for pystack-core
"""

from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
import asyncio
import signal
import sys
import inspect
from contextlib import asynccontextmanager

from py_core.config import Config, AppConfig
from py_core.container import Container
from py_core.middleware import MiddlewarePipeline
from py_core.logging import LogLevel


@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "py-core-app"
    environment: str = "development"
    debug: bool = False
    config_path: Optional[str] = None
    env_prefix: str = "APP_"
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = False


class App:
    """Production-ready main application class with lifecycle management"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the application"""
        self._app_config = config or AppConfig()
        self.config = Config(self._app_config)
        self._container = Container()
        self._middleware = MiddlewarePipeline()
        self._started = False
        self._shutdown_hooks: list[Callable] = []
        self._startup_hooks: list[Callable] = []
        self._context: Dict[str, Any] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def add_startup_hook(self, hook: Callable) -> None:
        """Add a startup hook to be called during app.start()"""
        self._startup_hooks.append(hook)
    
    def add_shutdown_hook(self, hook: Callable) -> None:
        """Add a shutdown hook to be called during app.stop()"""
        self._shutdown_hooks.append(hook)
    
    def register_service(self, interface: type, implementation: type, singleton: bool = True) -> None:
        """Register a service in the DI container"""
        self._container.register(interface, implementation, singleton)
    
    def register_instance(self, interface: type, instance: Any) -> None:
        """Register an instance in the DI container"""
        self._container.register_instance(interface, instance)
    
    async def start(self) -> None:
        """Start the application and initialize all modules"""
        if self._started:
            return
        
        self._loop = asyncio.get_event_loop()
        
        # Set up signal handlers for graceful shutdown
        if sys.platform != 'win32':  # Unix-like systems
            for sig in (signal.SIGTERM, signal.SIGINT):
                self._loop.add_signal_handler(
                    sig, lambda: asyncio.create_task(self._handle_signal(sig))
                )
        
        # Initialize configuration
        await self.config.load()
        
        # Register core services in container
        self._container.register_instance(Config, self.config)
        self._container.register_instance(MiddlewarePipeline, self._middleware)
        self._container.register_instance(App, self)
        
        # Execute startup hooks
        for hook in self._startup_hooks:
            if inspect.iscoroutinefunction(hook):
                await hook(self)
            else:
                hook(self)
        
        self._started = True
    
    async def _handle_signal(self, sig) -> None:
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {sig.name}, shutting down gracefully...")
        await self.stop()
    
    async def stop(self) -> None:
        """Stop the application and cleanup resources"""
        if not self._started:
            return
        
        # Execute shutdown hooks in reverse order
        for hook in reversed(self._shutdown_hooks):
            try:
                if inspect.iscoroutinefunction(hook):
                    await hook(self)
                else:
                    hook(self)
            except Exception as e:
                print(f"Error in shutdown hook: {e}")
        
        # Cleanup resources
        await self.config.cleanup()
        self._container.reset()
        
        # Remove signal handlers
        if self._loop and sys.platform != 'win32':
            for sig in (signal.SIGTERM, signal.SIGINT):
                self._loop.remove_signal_handler(sig)
        
        self._started = False
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager for application lifespan"""
        await self.start()
        try:
            yield self
        finally:
            await self.stop()
    
    async def run(self, main_coroutine: Callable) -> Any:
        """Run the application with a main coroutine"""
        async with self.lifespan():
            return await main_coroutine(self)
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a value from the application context"""
        return self._context.get(key, default)
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a value in the application context"""
        self._context[key] = value
    
    @property
    def container(self) -> Container:
        """Get the DI container"""
        return self._container
    
    @property
    def middleware(self) -> MiddlewarePipeline:
        """Get the middleware pipeline"""
        return self._middleware
    
    @property
    def is_started(self) -> bool:
        """Check if the application is started"""
        return self._started
    
    @property
    def logger(self):
        """Get logger (lazy loaded) with proper configuration"""
        from py_core.logging.logger import Logger
        if not self._container.is_registered(Logger):
            logger = Logger(name=self._app_config.name, level=LogLevel.from_string(self._app_config.log_level))
            self._container.register_instance(Logger, logger)
        return self._container.resolve(Logger)
    
    # For v0.1.0, we only have config and logging, but keep placeholders for future versions
    # These will be implemented in later versions according to the implementation plan
    
    async def execute_with_middleware(self, request: Any, handler: Callable) -> Any:
        """Execute a request through the middleware pipeline"""
        return await self._middleware.execute(request, handler)
