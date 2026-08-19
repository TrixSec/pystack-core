"""
Logging Example

This example demonstrates pystack-core's logging system:
- Multiple log formatters (console, JSON, text)
- Async logging for performance
- Request tracking with context injection
"""

import asyncio
from py_core.app import AppConfig
from py_core.logging.logger import Logger
from py_core.logging.interfaces import LogLevel
from py_core.logging.formatters import JSONFormatter
from py_core.logging.handlers import ConsoleHandler, AsyncQueueHandler


async def main():
    print("=== Logging System Example ===\n")
    
    # Example 1: Basic console logging
    print("1. Basic Console Logging:")
    logger = Logger(name="console-example", level=LogLevel.INFO)
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Example 2: Custom formatter
    print("\n2. Custom JSON Formatter:")
    json_logger = Logger(name="json-example", level=LogLevel.DEBUG)
    json_formatter = JSONFormatter(indent=True)
    
    # Remove default handler and add JSON handler
    json_logger._handlers.clear()
    json_handler = ConsoleHandler(level=LogLevel.DEBUG)
    json_handler.set_formatter(json_formatter)
    json_logger.add_handler(json_handler)
    
    json_logger.info("JSON formatted log entry", user_id="12345")
    
    # Example 3: Async logging
    print("\n3. Async Logging:")
    async_logger = Logger(name="async-example", level=LogLevel.INFO)
    async_logger.enable_async_logging(queue_size=1000)
    await async_logger.start_async()
    
    # Log many messages asynchronously
    for i in range(10):
        await async_logger.ainfo(f"Async log message {i}")
    
    await async_logger.stop_async()
    
    # Example 4: Context injection
    print("\n4. Context Injection:")
    context_logger = Logger(name="context-example", level=LogLevel.INFO)
    context_logger.add_global_context(app_name="logging-example", version="1.0.0")
    
    context_logger.info("Log with global context")
    
    # Request-specific context
    request_logger = context_logger.with_context(request_id="req-12345", user_id="user-67890")
    request_logger.info("Processing request")
    
    # Example 5: Request tracking
    print("\n5. Request Tracking:")
    tracking_logger = Logger(name="tracking-example", level=LogLevel.INFO)
    tracking_logger.set_request_id("trace-abc123")
    
    tracking_logger.info("Request started")
    tracking_logger.info("Request processing")
    tracking_logger.info("Request completed")
    
    print("\n=== Logging Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
