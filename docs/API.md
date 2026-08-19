# pystack-core v0.1.0 API Documentation

## Overview

pystack-core v0.1.0 provides a production-ready foundation for Python applications with core runtime, configuration management, and structured logging.

## Core Components

### App

The main application class that orchestrates all modules and manages application lifecycle.

```python
from py_core import App, AppConfig

# Create application with configuration
config = AppConfig(
    name="my-app",
    environment="production",
    debug=False,
    log_level="INFO"
)
app = App(config=config)

# Start the application
await app.start()

# Use the application
app.logger.info("Application running")

# Stop the application
await app.stop()
```

#### Methods

- `__init__(config: Optional[AppConfig] = None)` - Initialize the application
- `async start()` - Start the application and initialize all modules
- `async stop()` - Stop the application and cleanup resources
- `add_startup_hook(hook: Callable)` - Add a startup hook
- `add_shutdown_hook(hook: Callable)` - Add a shutdown hook
- `register_service(interface: type, implementation: type, singleton: bool = True)` - Register a service
- `register_instance(interface: type, instance: Any)` - Register an instance
- `set_context(key: str, value: Any)` - Set application context
- `get_context(key: str, default: Any = None)` - Get application context
- `async run(main_coroutine: Callable)` - Run application with main coroutine
- `async execute_with_middleware(request: Any, handler: Callable)` - Execute through middleware pipeline

#### Properties

- `config` - Configuration object
- `container` - Dependency injection container
- `middleware` - Middleware pipeline
- `logger` - Logger instance
- `is_started` - Whether the application is started

### AppConfig

Application configuration dataclass.

```python
from py_core import AppConfig

config = AppConfig(
    name="my-app",              # Application name
    environment="production",  # Environment (development, staging, production)
    debug=False,                # Debug mode
    config_path=None,           # Path to config file
    env_prefix="APP_",          # Environment variable prefix
    log_level="INFO",           # Logging level
    enable_metrics=True,        # Enable metrics collection
    enable_tracing=False       # Enable tracing
)
```

### Config

Configuration manager with support for multiple sources.

```python
from py_core import Config, AppConfig

config = Config(AppConfig())
await config.load()

# Get configuration values
db_url = config.get("database.url")
debug = config.get("app.debug", False)

# Set configuration values
config.set("cache.enabled", True)

# Validate against Pydantic schema
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    url: str = Field(..., min_length=1)
    pool_size: int = Field(default=10, ge=1, le=100)

db_config = config.validate_section("database", DatabaseConfig)
```

#### Methods

- `async load()` - Load configuration from all sources
- `get(key: str, default: Any = None)` - Get configuration value
- `get_typed(key: str, type_: Type[T]) -> T` - Get typed configuration value
- `set(key: str, value: Any)` - Set configuration value
- `validate(schema: Type[BaseModel]) -> BaseModel` - Validate against Pydantic schema
- `validate_section(section: str, schema: Type[BaseModel]) -> BaseModel` - Validate section
- `get_section(section: str)` - Get configuration section
- `has(key: str)` - Check if key exists
- `get_all()` - Get all configuration
- `reload()` - Reload configuration
- `async cleanup()` - Cleanup resources

### Container

Dependency injection container with lifecycle management.

```python
from py_core import Container

container = Container()

# Register services
class DatabaseService:
    def __init__(self):
        self.connected = False

container.register(DatabaseService, DatabaseService, singleton=True)

# Resolve services
db = container.resolve(DatabaseService)

# Register instances
instance = DatabaseService()
container.register_instance(DatabaseService, instance)

# Register factory functions
def create_db():
    return DatabaseService()

container.register_factory(DatabaseService, create_db, singleton=True)
```

#### Methods

- `register(interface: Type[T], implementation: Type[T], singleton: bool = True)` - Register implementation
- `register_instance(interface: Type[T], instance: T)` - Register instance
- `register_factory(interface: Type[T], factory: Callable[..., T], singleton: bool = True)` - Register factory
- `register_decorator(interface: Type[T], decorator: Callable[[T], T])` - Register decorator
- `resolve(interface: Type[T]) -> T` - Resolve interface to implementation
- `is_registered(interface: Type[T])` - Check if registered
- `reset()` - Reset container
- `inject(func: Callable)` - Dependency injection decorator

### MiddlewarePipeline

Middleware pipeline for cross-cutting concerns.

```python
from py_core import MiddlewarePipeline
from py_core.middleware import RequestIDMiddleware, TimingMiddleware

pipeline = MiddlewarePipeline()
pipeline.add_middleware(RequestIDMiddleware())
pipeline.add_middleware(TimingMiddleware())

async def handler(request):
    return f"processed: {request}"

result = await pipeline.execute("test-request", handler)
```

#### Methods

- `add_middleware(middleware: MiddlewareInterface, order: Optional[int] = None)` - Add middleware
- `remove_middleware(middleware_class: type)` - Remove middleware
- `async execute(request: Any, handler: Callable)` - Execute pipeline
- `get_performance_stats()` - Get performance statistics
- `reset_performance_stats()` - Reset statistics

### Logger

Structured logger with automatic context injection.

```python
from py_core import Logger, LogLevel

logger = Logger(name="my-app", level=LogLevel.INFO)

# Basic logging
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred", error_code="ERR001")

# Context management
logger.add_global_context(app_version="1.0.0")
logger.info("Log with global context")

# Request-specific context
request_logger = logger.with_context(request_id="req-12345", user_id="user-67890")
request_logger.info("Processing request")

# Request tracking
logger.set_request_id("trace-abc123")
logger.info("Request started")
```

#### Methods

- `add_handler(handler: LogHandler, use_async: bool = False)` - Add log handler
- `set_level(level: LogLevel)` - Set logging level
- `enable_async_logging(queue_size: int = 1000)` - Enable async logging
- `async start_async()` - Start async logging consumer
- `async stop_async()` - Stop async logging consumer
- `set_request_id(request_id: str)` - Set request ID
- `add_global_context(**context)` - Add global context
- `clear_context()` - Clear context
- `with_context(**context)` - Create logger with additional context

#### Logging Methods

**Synchronous:**
- `debug(message, **kwargs)`
- `info(message, **kwargs)`
- `warning(message, **kwargs)`
- `error(message, **kwargs)`
- `critical(message, **kwargs)`

**Asynchronous:**
- `async adebug(message, **kwargs)`
- `async ainfo(message, **kwargs)`
- `async awarning(message, **kwargs)`
- `async aerror(message, **kwargs)`
- `async acritical(message, **kwargs)`

### LogLevel

Log level enumeration with numeric values for filtering.

```python
from py_core import LogLevel

# Levels in order of severity
LogLevel.DEBUG    # 10
LogLevel.INFO     # 20
LogLevel.WARNING  # 30
LogLevel.ERROR    # 40
LogLevel.CRITICAL # 50

# Convert from string
level = LogLevel.from_string("INFO")
```

### Log Handlers

#### ConsoleHandler

Console handler with colored output.

```python
from py_core.logging import ConsoleHandler, LogLevel

handler = ConsoleHandler(level=LogLevel.INFO, use_colors=True)
```

#### FileHandler

Async file handler with rotation support.

```python
from py_core.logging import FileHandler, LogLevel

handler = FileHandler(
    file_path="app.log",
    level=LogLevel.DEBUG,
    max_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    formatter_type="json"
)
```

#### AsyncQueueHandler

Async queue handler for non-blocking logging.

```python
from py_core.logging import AsyncQueueHandler, LogLevel

handler = AsyncQueueHandler(level=LogLevel.INFO, queue_size=1000)
await handler.start()
# ... logging operations
await handler.stop()
```

### Log Formatters

#### ConsoleFormatter

Colored console formatter for human-readable output.

```python
from py_core.logging import ConsoleFormatter

formatter = ConsoleFormatter(show_colors=True, show_timestamp=True)
```

#### JSONFormatter

JSON formatter for structured logging.

```python
from py_core.logging import JSONFormatter

formatter = JSONFormatter(indent=True)
```

#### TextFormatter

Simple text formatter without colors.

```python
from py_core.logging import TextFormatter

formatter = TextFormatter(show_timestamp=True)
```

## Usage Patterns

### Basic Application

```python
import asyncio
from py_core import App, AppConfig

async def main():
    app = App(AppConfig(name="my-app"))
    await app.start()
    
    app.logger.info("Application started")
    
    await app.stop()

asyncio.run(main())
```

### Configuration Management

```python
import asyncio
from py_core import Config, AppConfig

async def main():
    config = Config(AppConfig(config_path="config.yaml"))
    await config.load()
    
    db_url = config.get("database.url")
    debug = config.get("app.debug")
    
    print(f"Database: {db_url}, Debug: {debug}")

asyncio.run(main())
```

### Advanced Logging

```python
import asyncio
from py_core import Logger, LogLevel
from py_core.logging import FileHandler, JSONFormatter

async def main():
    logger = Logger(name="advanced-logging", level=LogLevel.DEBUG)
    
    # Add file handler
    file_handler = FileHandler("app.log", level=LogLevel.DEBUG)
    file_handler.set_formatter(JSONFormatter())
    logger.add_handler(file_handler)
    
    # Enable async logging
    logger.enable_async_logging()
    await logger.start_async()
    
    # Log with context
    logger.add_global_context(app_version="1.0.0")
    await logger.ainfo("Application started")
    
    await logger.stop_async()

asyncio.run(main())
```

### Dependency Injection

```python
import asyncio
from py_core import App, AppConfig

class DatabaseService:
    def __init__(self):
        self.connected = False

async def main():
    app = App(AppConfig(name="di-example"))
    
    # Register service
    app.register_service(DatabaseService, DatabaseService)
    await app.start()
    
    # Resolve service
    db = app._container.resolve(DatabaseService)
    print(f"Database service: {db}")
    
    await app.stop()

asyncio.run(main())
```

## Performance

pystack-core v0.1.0 is designed for high-performance scenarios:

- **Logging**: 10,000+ logs/sec throughput
- **Configuration**: 1,000+ loads/sec
- **App startup**: <1 second
- **App shutdown**: <1 second
- **Dependency resolution**: 10,000+ resolutions/sec

## Error Handling

All components include comprehensive error handling:

- Configuration parsing errors are caught and reported with context
- Logging handlers fail gracefully without crashing the application
- Dependency injection provides clear error messages for circular dependencies
- Application lifecycle hooks have error isolation to prevent cascade failures

## Thread Safety

- Configuration is thread-safe for read operations
- Logger is thread-safe with per-thread context caching
- Container is thread-safe for singleton resolution
- AsyncQueueHandler provides thread-safe async logging

## Best Practices

1. **Always use async/await** for I/O operations
2. **Use context injection** for request-specific data
3. **Validate configuration** with Pydantic schemas
4. **Use async logging** for high-throughput scenarios
5. **Clean up resources** with proper shutdown hooks
6. **Use dependency injection** for testability
7. **Set appropriate log levels** for production vs development

## Migration from Existing Solutions

### From python-dotenv

```python
# Before
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

# After
from py_core import Config, AppConfig
config = Config(AppConfig(env_prefix=""))
await config.load()
API_KEY = config.get("api_key")
```

### From custom logging

```python
# Before
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Message")

# After
from py_core import Logger, LogLevel
logger = Logger(name="my-app", level=LogLevel.INFO)
logger.info("Message")
```

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/TrixSec/py_core
- Telegram: https://t.me/Trixsec
