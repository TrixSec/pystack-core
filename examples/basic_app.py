"""
Basic pystack-core Application Example

This example demonstrates the basic usage of pystack-core v0.1.0:
- Application lifecycle management
- Configuration loading from multiple sources
- Structured logging with context injection
"""

import asyncio
from py_core.app import App, AppConfig
from py_core.logging.interfaces import LogLevel


async def main():
    # Create application with custom configuration
    config = AppConfig(
        name="example-app",
        environment="production",
        debug=False,
        log_level="INFO"
    )
    
    app = App(config=config)
    
    # Add startup hook
    def on_startup(app_instance):
        app_instance.logger.info("Application starting up...")
        app_instance.set_context("startup_time", "2024-01-01")
    
    app.add_startup_hook(on_startup)
    
    # Add shutdown hook
    def on_shutdown(app_instance):
        app_instance.logger.info("Application shutting down...")
    
    app.add_shutdown_hook(on_shutdown)
    
    # Start the application
    await app.start()
    
    # Use the logger
    app.logger.info("Application is running")
    app.logger.warning("This is a warning message")
    app.logger.error("This is an error message")
    
    # Demonstrate context
    app.logger.add_global_context(app_version="1.0.0")
    app.logger.info("Logging with global context")
    
    # Demonstrate contextual logger
    contextual_logger = app.logger.with_context(request_id="req-12345", user_id="user-67890")
    contextual_logger.info("Request processing started")
    
    # Stop the application
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
