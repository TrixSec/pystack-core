# pystack-core v0.2.0 Examples

This directory contains example projects demonstrating the features available in pystack-core v0.2.0.

## Available Examples

### v0.2.0 Examples

#### 1. http_example.py
Demonstrates the HTTP client module:
- Basic HTTP requests (GET, POST, etc.)
- Custom retry policies with exponential backoff
- Authentication (basic auth and bearer tokens)
- Circuit breaker for fault tolerance
- Metrics collection and monitoring

Run with:
```bash
python http_example.py
```

#### 2. cache_example.py
Demonstrates the cache module:
- Memory cache with LRU eviction
- TTL (time-to-live) support
- Batch operations (get_many, set_many)
- Counter operations (increment/decrement)
- Cache manager for unified backend management
- Statistics tracking (hit rate, cache size)

Run with:
```bash
python cache_example.py
```

#### 3. database_example.py
Demonstrates the database module:
- SQLite database operations
- Transaction management
- Context managers for automatic commit/rollback
- Batch query execution
- Database manager for unified backend management
- Connection information and status tracking

Run with:
```bash
python database_example.py
```

### v0.1.0 Examples

#### 4. basic_app.py
Demonstrates the basic application lifecycle:
- Application initialization with custom configuration
- Startup and shutdown hooks
- Basic logging usage
- Context management

Run with:
```bash
python basic_app.py
```

#### 5. config_example.py
Demonstrates the configuration system:
- Loading configuration from YAML files
- Environment variable loading with automatic type conversion
- Pydantic schema validation
- Configuration merging from multiple sources
- Nested configuration management

Run with:
```bash
python config_example.py
```

#### 6. logging_example.py
Demonstrates the logging system:
- Console logging with colored output
- JSON structured logging
- Async logging for high-performance scenarios
- Context injection (global and request-specific)
- Request tracking with unique IDs

Run with:
```bash
python logging_example.py
```

## v0.2.0 Features

These examples demonstrate the new features available in pystack-core v0.2.0:

### HTTP Client
- **Automatic retry**: Configurable retry policy with exponential backoff
- **Timeout management**: Configurable request timeouts
- **Metrics collection**: Track requests, success rates, and latency
- **Circuit breaker**: Prevent cascading failures
- **Authentication**: Basic auth and bearer token support
- **Middleware pipeline**: Request/response processing

### Cache
- **Multi-backend**: Memory, Redis, and disk storage
- **TTL support**: Time-to-live for cache entries
- **LRU eviction**: Automatic eviction of least recently used items
- **Statistics**: Track hit rates and performance
- **Batch operations**: Efficient multi-item operations
- **Cache manager**: Unified backend management

### Database
- **SQLite support**: Full async SQLite implementation
- **PostgreSQL support**: PostgreSQL with SQLite fallback
- **Transaction management**: Context managers for transactions
- **Connection pooling**: Efficient connection management
- **Batch queries**: Execute multiple queries efficiently
- **Database manager**: Unified backend management

## v0.1.0 Features

These examples also demonstrate the core features available in pystack-core v0.1.0:

### Core Runtime
- **App**: Main application class with lifecycle management
- **Container**: Dependency injection container with singleton/transient support
- **Middleware**: Pipeline for cross-cutting concerns with performance tracking

### Configuration
- **Multi-source loading**: Environment variables, YAML, JSON, TOML files
- **Type conversion**: Automatic conversion of string values to appropriate types
- **Validation**: Pydantic schema validation for configuration
- **Merging**: Smart merging of configuration from multiple sources

### Logging
- **Structured logging**: Automatic context injection (timestamp, thread_id, request_id)
- **Multiple formatters**: Console (colored), JSON, text formats
- **Async support**: Non-blocking async logging for high-performance scenarios
- **File logging**: Async file writing with rotation support
- **Cloud adapters**: CloudWatch and Loggly integration (placeholders for implementation)
- **Request tracking**: Async-safe request ID tracking using contextvars

## Running the Examples

All examples can be run directly with Python:

```bash
# v0.2.0 examples
python http_example.py
python cache_example.py
python database_example.py

# v0.1.0 examples
python basic_app.py
python config_example.py
python logging_example.py
```

Make sure you have pystack-core installed in your environment:

```bash
pip install -e .
```

## Integration Example

For a complete integration example combining HTTP, cache, and database modules, see the documentation in `docs/V0.2.0_FEATURES.md`.

## Next Steps

After running these examples, you can explore the source code to understand how the features work under the hood. The modular structure makes it easy to extend and customize for your specific needs.
