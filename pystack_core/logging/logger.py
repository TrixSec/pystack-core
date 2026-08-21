"""
Structured Logger with multiple formatters and context injection
"""

import asyncio
import time
import uuid
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class LogLevel(Enum):
    """Log level"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Log entry"""
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class LogFormatter:
    """Base log formatter"""
    
    def format(self, entry: LogEntry) -> str:
        """Format log entry"""
        raise NotImplementedError


class ConsoleFormatter(LogFormatter):
    """Console formatter with colors"""
    
    def __init__(self, use_colors: bool = True):
        self._use_colors = use_colors
        self._colors = {
            LogLevel.DEBUG: "\033[36m",    # Cyan
            LogLevel.INFO: "\033[32m",     # Green
            LogLevel.WARNING: "\033[33m",  # Yellow
            LogLevel.ERROR: "\033[31m",    # Red
            LogLevel.CRITICAL: "\033[35m", # Magenta
        }
        self._reset = "\033[0m"
    
    def format(self, entry: LogEntry) -> str:
        """Format log entry for console"""
        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        level = entry.level.value
        message = entry.message
        
        color = ""
        if self._use_colors:
            color = self._colors.get(entry.level, "")
            reset = self._reset
        else:
            reset = ""
        
        request_id = f" [{entry.request_id}]" if entry.request_id else ""
        context_str = f" {json.dumps(entry.context)}" if entry.context else ""
        
        return f"{color}[{timestamp}] {level}{request_id}: {message}{context_str}{reset}"


class JSONFormatter(LogFormatter):
    """JSON formatter for structured logging"""
    
    def format(self, entry: LogEntry) -> str:
        """Format log entry as JSON"""
        log_dict = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level.value,
            "message": entry.message,
            "context": entry.context,
            "request_id": entry.request_id,
            "extra": entry.extra
        }
        return json.dumps(log_dict)


class LogHandler:
    """Base log handler"""
    
    async def handle(self, entry: LogEntry):
        """Handle log entry"""
        raise NotImplementedError


class ConsoleHandler(LogHandler):
    """Console log handler"""
    
    def __init__(self, formatter: Optional[LogFormatter] = None):
        self._formatter = formatter or ConsoleFormatter()
    
    async def handle(self, entry: LogEntry):
        """Handle log entry by printing to console"""
        formatted = self._formatter.format(entry)
        print(formatted)


class AsyncQueueHandler(LogHandler):
    """Async queue-based log handler"""
    
    def __init__(self, handler: LogHandler, queue_size: int = 1000):
        self._handler = handler
        self._queue = asyncio.Queue(maxsize=queue_size)
        self._running = False
        self._worker_task = None
    
    async def start(self):
        """Start queue processor"""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._process_queue())
    
    async def stop(self):
        """Stop queue processor"""
        if self._running:
            self._running = False
            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
    
    async def handle(self, entry: LogEntry):
        """Handle log entry by adding to queue"""
        try:
            await self._queue.put(entry)
        except asyncio.QueueFull:
            # Drop log entry if queue is full
            pass
    
    async def _process_queue(self):
        """Process log entries from queue"""
        while self._running:
            try:
                entry = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                await self._handler.handle(entry)
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue


class Logger:
    """Structured logger with context injection"""
    
    def __init__(self, name: str = "app", level: LogLevel = LogLevel.INFO):
        self._name = name
        self._level = level
        self._handlers: List[LogHandler] = []
        self._context: Dict[str, Any] = {}
        self._request_id: Optional[str] = None
        self._extra: Dict[str, Any] = {}
    
    def add_handler(self, handler: LogHandler):
        """Add log handler"""
        self._handlers.append(handler)
    
    def set_level(self, level: LogLevel):
        """Set log level"""
        self._level = level
    
    def set_context(self, key: str, value: Any):
        """Set context value"""
        self._context[key] = value
    
    def set_request_id(self, request_id: str):
        """Set request ID"""
        self._request_id = request_id
    
    def set_extra(self, key: str, value: Any):
        """Set extra field"""
        self._extra[key] = value
    
    def clear_context(self):
        """Clear all context"""
        self._context.clear()
        self._request_id = None
        self._extra.clear()
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if level should be logged"""
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        return levels.index(level) >= levels.index(self._level)
    
    async def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal log method"""
        if not self._should_log(level):
            return
        
        entry = LogEntry(
            level=level,
            message=message,
            context=self._context.copy(),
            request_id=self._request_id,
            extra={**self._extra, **kwargs}
        )
        
        for handler in self._handlers:
            await handler.handle(entry)
    
    async def debug(self, message: str, **kwargs):
        """Log debug message"""
        await self._log(LogLevel.DEBUG, message, **kwargs)
    
    async def info(self, message: str, **kwargs):
        """Log info message"""
        await self._log(LogLevel.INFO, message, **kwargs)
    
    async def warning(self, message: str, **kwargs):
        """Log warning message"""
        await self._log(LogLevel.WARNING, message, **kwargs)
    
    async def error(self, message: str, **kwargs):
        """Log error message"""
        await self._log(LogLevel.ERROR, message, **kwargs)
    
    async def critical(self, message: str, **kwargs):
        """Log critical message"""
        await self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def with_context(self, **context) -> "Logger":
        """Create logger with additional context"""
        new_logger = Logger(self._name, self._level)
        new_logger._handlers = self._handlers.copy()
        new_logger._context = {**self._context, **context}
        new_logger._request_id = self._request_id
        new_logger._extra = self._extra.copy()
        return new_logger
    
    def with_request_id(self, request_id: str) -> "Logger":
        """Create logger with request ID"""
        new_logger = Logger(self._name, self._level)
        new_logger._handlers = self._handlers.copy()
        new_logger._context = self._context.copy()
        new_logger._request_id = request_id
        new_logger._extra = self._extra.copy()
        return new_logger
