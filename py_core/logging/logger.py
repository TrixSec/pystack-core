"""
Logger implementation - Production-ready structured logging with automatic context injection
"""

from typing import Any, Dict, Optional
import time
import threading
import uuid
import asyncio
import sys
from contextvars import ContextVar
from datetime import datetime

from py_core.logging.interfaces import LogLevel, LogHandler
from py_core.logging.formatters import ConsoleFormatter, JSONFormatter
from py_core.logging.handlers import ConsoleHandler, AsyncQueueHandler


# Context variable for request tracking (async-safe)
_request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class Logger:
    """Production-ready structured logger with automatic context injection and async support"""
    
    def __init__(self, name: str = "pystack-core", level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self._context: Dict[str, Any] = {}
        self._context_cache: Dict[int, Dict[str, Any]] = {}
        self._handlers: list[LogHandler] = []
        self._async_handlers: list[LogHandler] = []
        self._queue_handler: Optional[AsyncQueueHandler] = None
        self._running = False
        
        # Add default console handler
        self._add_default_handler()
    
    def _add_default_handler(self) -> None:
        """Add default console handler"""
        console_handler = ConsoleHandler(level=self.level, use_colors=True)
        self._handlers.append(console_handler)
    
    def add_handler(self, handler: LogHandler, use_async: bool = False) -> None:
        """Add a log handler"""
        if use_async:
            self._async_handlers.append(handler)
        else:
            self._handlers.append(handler)
    
    def enable_async_logging(self, queue_size: int = 1000) -> None:
        """Enable async logging with queue"""
        if not self._queue_handler:
            self._queue_handler = AsyncQueueHandler(level=self.level, queue_size=queue_size)
            
            # Add existing handlers to queue
            for handler in self._handlers:
                self._queue_handler.add_handler(handler)
            
            # Add async handlers to queue
            for handler in self._async_handlers:
                self._queue_handler.add_handler(handler)
            
            self._handlers = [self._queue_handler]  # Only queue handler in sync list
            self._async_handlers = []
    
    async def start_async(self) -> None:
        """Start async logging consumer"""
        if self._queue_handler and not self._running:
            await self._queue_handler.start()
            self._running = True
    
    async def stop_async(self) -> None:
        """Stop async logging consumer"""
        if self._queue_handler and self._running:
            await self._queue_handler.stop()
            self._running = False
    
    def set_level(self, level: LogLevel) -> None:
        """Set the logging level"""
        self.level = level
        for handler in self._handlers:
            handler.level = level
        for handler in self._async_handlers:
            handler.level = level
        if self._queue_handler:
            self._queue_handler.level = level
    
    def set_request_id(self, request_id: str) -> None:
        """Set the current request ID (async-safe)"""
        _request_id.set(request_id)
    
    def _get_context(self) -> Dict[str, Any]:
        """Get context for current thread/request"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "logger": self.name,
        }
        
        # Add thread ID for sync contexts
        thread_id = threading.get_ident()
        context["thread_id"] = thread_id
        
        # Add request ID if available (async-safe)
        request_id = _request_id.get()
        if request_id:
            context["request_id"] = request_id
        
        # Add cached context
        if thread_id in self._context_cache:
            context.update(self._context_cache[thread_id])
        
        # Add global context
        context.update(self._context)
        
        return context
    
    def _build_log_entry(self, level: LogLevel, message: str, **kwargs: Any) -> Dict[str, Any]:
        """Build a complete log entry"""
        return {
            "level": level.name,
            "message": message,
            "context": self._get_context(),
            **kwargs
        }
    
    async def _emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to all handlers"""
        # Emit to sync handlers
        for handler in self._handlers:
            try:
                await handler.handle(log_entry)
            except Exception as e:
                # Fallback to print if handler fails
                print(f"Handler error: {e}", file=sys.stderr)
                print(f"Log entry: {log_entry}", file=sys.stderr)
        
        # Emit to async handlers
        for handler in self._async_handlers:
            try:
                await handler.handle(log_entry)
            except Exception as e:
                print(f"Async handler error: {e}", file=sys.stderr)
    
    def _log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Core logging method"""
        if level.value < self.level.value:
            return
        
        log_entry = self._build_log_entry(level, message, **kwargs)
        
        # Handle async emission
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context
                asyncio.create_task(self._emit(log_entry))
            else:
                # We're in sync context, run async handlers in sync mode
                asyncio.run(self._emit(log_entry))
        except RuntimeError:
            # No event loop, run synchronously
            asyncio.run(self._emit(log_entry))
    
    async def async_log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Async logging method"""
        if level.value < self.level.value:
            return
        
        log_entry = self._build_log_entry(level, message, **kwargs)
        await self._emit(log_entry)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    # Async versions
    async def adebug(self, message: str, **kwargs: Any) -> None:
        """Async log debug message"""
        await self.async_log(LogLevel.DEBUG, message, **kwargs)
    
    async def ainfo(self, message: str, **kwargs: Any) -> None:
        """Async log info message"""
        await self.async_log(LogLevel.INFO, message, **kwargs)
    
    async def awarning(self, message: str, **kwargs: Any) -> None:
        """Async log warning message"""
        await self.async_log(LogLevel.WARNING, message, **kwargs)
    
    async def aerror(self, message: str, **kwargs: Any) -> None:
        """Async log error message"""
        await self.async_log(LogLevel.ERROR, message, **kwargs)
    
    async def acritical(self, message: str, **kwargs: Any) -> None:
        """Async log critical message"""
        await self.async_log(LogLevel.CRITICAL, message, **kwargs)
    
    def with_context(self, **context: Any) -> 'Logger':
        """Create a logger with additional context"""
        new_logger = Logger(name=self.name, level=self.level)
        new_logger._context = {**self._context, **context}
        new_logger._handlers = self._handlers.copy()
        new_logger._async_handlers = self._async_handlers.copy()
        new_logger._queue_handler = self._queue_handler
        return new_logger
    
    def add_global_context(self, **context: Any) -> None:
        """Add context that will be included in all log entries"""
        self._context.update(context)
    
    def clear_context(self) -> None:
        """Clear all context"""
        self._context.clear()
        self._context_cache.clear()
