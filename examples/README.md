# pystack-core v0.1.0 Examples

This directory contains example projects demonstrating the features available in pystack-core v0.1.0.

## Available Examples

### 1. basic_app.py
Demonstrates the basic application lifecycle:
- Application initialization with custom configuration
- Startup and shutdown hooks
- Basic logging usage
- Context management

Run with:
```bash
python basic_app.py
```

### 2. config_example.py
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

### 3. logging_example.py
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

## v0.1.0 Features

These examples demonstrate the core features available in pystack-core v0.1.0:

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
python basic_app.py
python config_example.py
python logging_example.py
```

Make sure you have pystack-core installed in your environment:

```bash
pip install -e .
```

## Next Steps

After running these examples, you can explore the source code to understand how the features work under the hood. The modular structure makes it easy to extend and customize for your specific needs.
