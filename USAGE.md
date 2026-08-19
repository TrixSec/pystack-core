# Usage Guide

This guide provides detailed usage examples and patterns for pystack-core v0.1.0.

## Table of Contents

- [Getting Started](#getting-started)
- [Application Lifecycle](#application-lifecycle)
- [Configuration Management](#configuration-management)
- [Logging](#logging)
- [Dependency Injection](#dependency-injection)
- [Middleware](#middleware)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Getting Started

### Installation

```bash
pip install pystack-core
```

### Basic Application

```python
import asyncio
from py_core import App, AppConfig

async def main():
    # Create application with configuration
    config = AppConfig(
        name="my-app",
        environment="production",
        log_level="INFO"
    )
    app = App(config=config)
    
    # Start the application
    await app.start()
    
    # Your application logic here
    app.logger.info("Application started")
    
    # Stop the application
    await app.stop()

asyncio.run(main())
```

## Application Lifecycle

### Startup and Shutdown Hooks

```python
from py_core import App, AppConfig

def on_startup(app):
    app.logger.info("Initializing resources...")
    # Initialize database connections, cache, etc.

async def async_on_startup(app):
    app.logger.info("Async initialization...")
    # Initialize async resources

def on_shutdown(app):
    app.logger.info("Cleaning up resources...")
    # Cleanup resources

async def main():
    app = App(AppConfig(name="my-app"))
    
    # Add hooks
    app.add_startup_hook(on_startup)
    app.add_startup_hook(async_on_startup)
    app.add_shutdown_hook(on_shutdown)
    
    await app.start()
    await app.stop()
```

### Context Manager

```python
from py_core import App, AppConfig

async def main():
    app = App(AppConfig(name="my-app"))
    
    async with app:
        # Application is started
        app.logger.info("Running")
    
    # Application is stopped automatically
```

## Configuration Management

### Environment Variables

```python
import os
from py_core import Config, AppConfig

async def main():
    # Set environment variables
    os.environ["APP_DATABASE_URL"] = "postgresql://localhost/mydb"
    os.environ["APP_DEBUG"] = "true"
    
    config = Config(AppConfig(env_prefix="APP_"))
    await config.load()
    
    # Access configuration
    db_url = config.get("database.url")
    debug = config.get("debug")
    
    print(f"Database: {db_url}, Debug: {debug}")
```

### File-Based Configuration

```python
from py_core import Config, AppConfig

async def main():
    # Load from YAML file
    config = Config(AppConfig(config_path="config.yaml"))
    await config.load()
    
    # Access nested values
    api_key = config.get("api.key")
    timeout = config.get("api.timeout", default=30)
```

### YAML Configuration File

```yaml
# config.yaml
database:
  url: "postgresql://localhost/mydb"
  pool_size: 20
  timeout: 30

api:
  key: "your-api-key"
  timeout: 60
  retries: 3

cache:
  enabled: true
  ttl: 3600
```

### Pydantic Validation

```python
from pydantic import BaseModel, Field
from py_core import Config, AppConfig

class DatabaseConfig(BaseModel):
    url: str = Field(..., min_length=1)
    pool_size: int = Field(default=10, ge=1, le=100)
    timeout: int = Field(default=30, ge=1)

async def main():
    config = Config(AppConfig(config_path="config.yaml"))
    await config.load()
    
    # Validate configuration
    db_config = config.validate_section("database", DatabaseConfig)
    print(f"Validated config: {db_config}")
```

### Type Conversion

Configuration automatically converts string values to appropriate types:

```python
# Environment variable
APP_ENABLED=true          # -> bool(True)
APP_PORT=8080            # -> int(8080)
APP_TIMEOUT=30.5         # -> float(30.5)
APP_ALLOWED_IPS=["1.1.1.1", "2.2.2.2"]  # -> list
```

## Logging

### Basic Logging

```python
from py_core import Logger, LogLevel

logger = Logger(name="my-app", level=LogLevel.INFO)

logger.debug("Debug message")      # Not shown (below INFO)
logger.info("Info message")       # Shown
logger.warning("Warning message") # Shown
logger.error("Error message")     # Shown
logger.critical("Critical message") # Shown
```

### Context Injection

```python
from py_core import Logger, LogLevel

logger = Logger(name="my-app", level=LogLevel.INFO)

# Add global context
logger.add_global_context(app_version="1.0.0", environment="production")

# Logs will include global context
logger.info("User logged in")

# Add request-specific context
request_logger = logger.with_context(
    request_id="req-12345",
    user_id="user-67890"
)
request_logger.info("Processing request")
```

### Request Tracking

```python
from py_core import Logger, LogLevel

logger = Logger(name="my-app", level=LogLevel.INFO)

# Set request ID for tracking
logger.set_request_id("trace-abc123")

logger.info("Request started")
logger.info("Processing")
logger.info("Request completed")
```

### Async Logging

```python
import asyncio
from py_core import Logger, LogLevel

async def main():
    logger = Logger(name="async-app", level=LogLevel.INFO)
    
    # Enable async logging
    logger.enable_async_logging(queue_size=1000)
    await logger.start_async()
    
    # Log asynchronously
    for i in range(1000):
        await logger.ainfo(f"Message {i}")
    
    await logger.stop_async()

asyncio.run(main())
```

### JSON Formatted Logging

```python
from py_core import Logger, LogLevel
from py_core.logging import JSONFormatter, ConsoleHandler

logger = Logger(name="json-app", level=LogLevel.INFO)

# Remove default handler
logger._handlers.clear()

# Add JSON handler
json_handler = ConsoleHandler(level=LogLevel.INFO)
json_handler.set_formatter(JSONFormatter(indent=True))
logger.add_handler(json_handler)

logger.info("Structured log", user_id="12345")
```

### File Logging

```python
from py_core import Logger, LogLevel
from py_core.logging import FileHandler

logger = Logger(name="file-app", level=LogLevel.DEBUG)

# Add file handler
file_handler = FileHandler(
    file_path="app.log",
    level=LogLevel.DEBUG,
    max_size=10 * 1024 * 1024,  # 10MB
    backup_count=5
)
logger.add_handler(file_handler)

logger.info("This will be written to file")
```

## Dependency Injection

### Service Registration

```python
from py_core import App, AppConfig

class DatabaseService:
    def __init__(self):
        self.connected = False

class CacheService:
    def __init__(self):
        self.cache = {}

async def main():
    app = App(AppConfig(name="di-app"))
    
    # Register services
    app.register_service(DatabaseService, DatabaseService)
    app.register_service(CacheService, CacheService)
    
    await app.start()
    
    # Resolve services
    db = app._container.resolve(DatabaseService)
    cache = app._container.resolve(CacheService)
    
    print(f"Database: {db}, Cache: {cache}")
    
    await app.stop()
```

### Singleton vs Transient

```python
from py_core import App, AppConfig

class DatabaseService:
    def __init__(self):
        self.connected = False

async def main():
    app = App(AppConfig(name="di-app"))
    
    # Singleton (default) - same instance every time
    app.register_service(DatabaseService, DatabaseService, singleton=True)
    
    await app.start()
    
    db1 = app._container.resolve(DatabaseService)
    db2 = app._container.resolve(DatabaseService)
    
    assert db1 is db2  # Same instance
    
    await app.stop()
```

### Instance Registration

```python
from py_core import App, AppConfig

class ConfigService:
    def __init__(self, config):
        self.config = config

async def main():
    app = App(AppConfig(name="di-app"))
    
    # Register instance
    config_service = ConfigService({"key": "value"})
    app.register_instance(ConfigService, config_service)
    
    await app.start()
    
    resolved = app._container.resolve(ConfigService)
    assert resolved is config_service
    
    await app.stop()
```

## Middleware

### Adding Middleware

```python
from py_core import App, AppConfig
from py_core.middleware import RequestIDMiddleware, TimingMiddleware

async def main():
    app = App(AppConfig(name="middleware-app"))
    
    # Add middleware
    app.middleware.add_middleware(RequestIDMiddleware())
    app.middleware.add_middleware(TimingMiddleware())
    
    await app.start()
    
    # Execute through middleware
    async def handler(request):
        return f"processed: {request}"
    
    result = await app.execute_with_middleware("test-request", handler)
    print(result)
    
    await app.stop()
```

### Custom Middleware

```python
from py_core.middleware import MiddlewareInterface

class CustomMiddleware(MiddlewareInterface):
    async def process(self, request, next_handler):
        # Pre-processing
        print(f"Before: {request}")
        
        # Call next handler
        response = await next_handler(request)
        
        # Post-processing
        print(f"After: {response}")
        
        return response

# Usage
app.middleware.add_middleware(CustomMiddleware())
```

## Best Practices

### 1. Always Use Async/Await for I/O

```python
# Good
async def fetch_data():
    await app.http.get("https://api.example.com")

# Bad
def fetch_data():
    app.http.get("https://api.example.com")
```

### 2. Use Context Injection for Request Data

```python
# Good
request_logger = logger.with_context(request_id="req-123", user_id="user-456")
request_logger.info("Processing")

# Bad
logger.info("Processing", request_id="req-123", user_id="user-456")
```

### 3. Validate Configuration with Pydantic

```python
# Good
class DatabaseConfig(BaseModel):
    url: str = Field(..., min_length=1)

db_config = config.validate_section("database", DatabaseConfig)

# Bad
db_url = config.get("database.url")  # No validation
```

### 4. Use Async Logging for High Throughput

```python
# Good for high-throughput scenarios
logger.enable_async_logging()
await logger.start_async()
await logger.ainfo("Message")

# Good for low-throughput scenarios
logger.info("Message")
```

### 5. Clean Up Resources with Shutdown Hooks

```python
def on_shutdown(app):
    app.logger.info("Cleaning up...")
    # Close connections, release resources

app.add_shutdown_hook(on_shutdown)
```

### 6. Set Appropriate Log Levels

```python
# Development
LogLevel.DEBUG

# Production
LogLevel.INFO

# Critical systems
LogLevel.WARNING
```

## Common Patterns

### Web Application Pattern

```python
import asyncio
from py_core import App, AppConfig

async def main():
    app = App(AppConfig(
        name="web-app",
        environment="production",
        log_level="INFO"
    ))
    
    def on_startup(app):
        app.logger.info("Starting web server...")
    
    def on_shutdown(app):
        app.logger.info("Stopping web server...")
    
    app.add_startup_hook(on_startup)
    app.add_shutdown_hook(on_shutdown)
    
    await app.start()
    
    # Your web application logic here
    
    await app.stop()

asyncio.run(main())
```

### Background Worker Pattern

```python
import asyncio
from py_core import App, AppConfig

async def worker_task(app):
    while True:
        app.logger.info("Processing task")
        await asyncio.sleep(1)

async def main():
    app = App(AppConfig(name="worker-app"))
    await app.start()
    
    # Run background task
    await worker_task(app)
    
    await app.stop()

asyncio.run(main())
```

### API Service Pattern

```python
import asyncio
from py_core import App, AppConfig
from py_core.logging import Logger, LogLevel

async def main():
    app = App(AppConfig(
        name="api-service",
        environment="production",
        log_level="INFO"
    ))
    
    await app.start()
    
    # Add request tracking
    logger = Logger(name="api", level=LogLevel.INFO)
    logger.set_request_id("req-12345")
    
    logger.info("API request received")
    logger.info("Processing request")
    logger.info("Request completed")
    
    await app.stop()

asyncio.run(main())
```

## Migration Guides

### From python-dotenv

```python
# Before
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

# After
from py_core import Config, AppConfig

config = Config(AppConfig(env_prefix=""))
await config.load()
API_KEY = config.get("api_key")
```

### From logging module

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

### From custom config

```python
# Before
import json

with open("config.json") as f:
    config = json.load(f)
    db_url = config["database"]["url"]

# After
from py_core import Config, AppConfig

config = Config(AppConfig(config_path="config.json"))
await config.load()
db_url = config.get("database.url")
```

## Support

For more information, see:
- [API Documentation](docs/API.md)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)
- [GitHub Issues](https://github.com/TrixSec/py_core/issues)
