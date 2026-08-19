<p align="center">
  <a href="https://pypi.org/project/pystack-core/"><img src="https://img.shields.io/pypi/v/pystack-core?style=for-the-badge&logo=pypi&logoColor=white&label=PyPI" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/pystack-core/"><img src="https://img.shields.io/pypi/pyversions/pystack-core?style=for-the-badge&logo=python&logoColor=white" alt="Python Versions"></a>
  <a href="https://github.com/TrixSec/pystack-core/blob/main/LICENSE"><img src="https://img.shields.io/github/license/TrixSec/py_core?style=for-the-badge&logo=gnu&logoColor=white&color=blue" alt="License"></a>
</p>

<p align="center">
  <a href="https://github.com/TrixSec/pystack-core/stargazers"><img src="https://img.shields.io/github/stars/TrixSec/py_core?style=for-the-badge&logo=github&color=yellow" alt="GitHub Stars"></a>
  <a href="https://github.com/TrixSec/pystack-core/network/members"><img src="https://img.shields.io/github/forks/TrixSec/py_core?style=for-the-badge&logo=github&color=lightgrey" alt="GitHub Forks"></a>
  <a href="https://github.com/TrixSec/pystack-core/issues"><img src="https://img.shields.io/github/issues/TrixSec/py_core?style=for-the-badge&logo=github&color=red" alt="GitHub Issues"></a>
  <a href="https://github.com/TrixSec/pystack-core/commits/main"><img src="https://img.shields.io/github/last-commit/TrixSec/py_core?style=for-the-badge&logo=github&color=purple" alt="Last Commit"></a>
</p>

<p align="center">
  <a href="https://github.com/TrixSec/pystack-core"><img src="https://img.shields.io/github/repo-size/TrixSec/py_core?style=for-the-badge&logo=github&color=teal" alt="Repo Size"></a>
  <a href="https://github.com/TrixSec/pystack-core/releases"><img src="https://img.shields.io/github/v/release/TrixSec/py_core?style=for-the-badge&logo=github&color=darkgreen" alt="Latest Release"></a>
  <a href="https://t.me/Trixsec"><img src="https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram" alt="Telegram"></a>
</p>

# pystack-core

**Author** : Trix Cyrus (Vicky) 

**Operating System for Python Applications**

pystack-core is a unified runtime layer that provides essential application infrastructure through a single, coherent API. Instead of installing and configuring 20+ packages, install `pystack-core` and gain instant access to configuration, logging, HTTP, caching, databases, AI, scheduling, metrics, and more.

## Vision

Every Python application should start with a solid foundation. pystack-core aims to become the standard runtime layer that Python developers begin their applications with.

## Installation

```bash
pip install pystack-core
```

## Quick Start

```python
from py_core import App

app = App()

# Everything is configured and ready to use
response = await app.http.get("https://api.example.com/users")
await app.cache.set("users", response.json)
users = await app.db.query("SELECT * FROM users")
app.logger.info("Fetched users", count=len(users))
```

## Features

- **Configuration:** Unified configuration from environment variables, files, and remote sources
- **Logging:** Structured logging with automatic context injection
- **HTTP Client:** Automatic retry, timeout, metrics, and tracing
- **Cache:** Multi-backend caching (Memory, Redis, Disk)
- **Database:** Unified database interface (PostgreSQL, MySQL, SQLite, MongoDB)
- **AI:** Provider-agnostic AI interface (OpenAI, Anthropic, Gemini)
- **Queue:** Background tasks with multiple backends
- **Scheduler:** Cron and natural language scheduling
- **Secrets:** Unified secrets management
- **Metrics:** Automatic metrics collection and export
- **Events:** Event bus for cross-module communication
- **Authentication:** Multiple auth strategies
- **CLI:** Project scaffolding and development tools
- **Plugin System:** Extensible plugin architecture

## Documentation

- **[Usage Guide](USAGE.md)** - Comprehensive usage examples and patterns
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[Examples](examples/)** - Working code examples

### Quick Start

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
    
    # Use the logger
    app.logger.info("Application started")
    
    # Stop the application
    await app.stop()

asyncio.run(main())
```

For more examples, see the [examples](examples/) directory.

## v0.1.0 Features

The current release (v0.1.0) includes production-ready implementations of:

### Core Runtime
- Application lifecycle management with async support
- Dependency injection container with singleton/transient resolution
- Middleware pipeline for cross-cutting concerns
- Context management for application state
- Startup and shutdown hooks with error isolation

### Configuration System
- Multi-source configuration loading (environment, YAML, JSON, TOML)
- Automatic type conversion (strings to bool, int, float, JSON)
- Pydantic schema validation with detailed error reporting
- Smart configuration merging from multiple sources
- Nested configuration value management

### Logging System
- Structured logging with automatic context injection
- Multiple formatters (console with colors, JSON, text)
- Async logging with queue-based processing for high performance
- File handlers with rotation support
- Request tracking with async-safe contextvars
- Cloud logging adapters (CloudWatch, Loggly)

## Performance

pystack-core v0.1.0 is designed for high-performance scenarios:

- **Logging:** 10,000+ logs/sec throughput
- **Configuration:** 1,000+ loads/sec
- **App startup:** <1 second
- **App shutdown:** <1 second
- **Dependency resolution:** 10,000+ resolutions/sec

## Testing

The project includes comprehensive test coverage:

- **79 tests** covering all core functionality
- **Integration tests** for all modules
- **Performance benchmarks** meeting production targets
- **Memory efficiency tests**

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=py_core
```

## Development

```bash
# Clone the repository
git clone https://github.com/TrixSec/pystack-core.git
cd py_core

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check py_core
black py_core
mypy py_core
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

GPL-3.0 License - see [LICENSE](LICENSE) for details.

## Community

- **GitHub:** [https://github.com/TrixSec/pystack-core](https://github.com/TrixSec/pystack-core)
- **Telegram:** [https://t.me/Trixsec](https://t.me/Trixsec)
- **Issues:** [https://github.com/TrixSec/pystack-core/issues](https://github.com/TrixSec/pystack-core/issues)
