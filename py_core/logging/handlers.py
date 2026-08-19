"""
Log handlers - Production-ready handlers for different outputs
"""

from typing import Any, Dict, Optional
from datetime import datetime
import asyncio
import sys
from pathlib import Path
import aiofiles
from py_core.logging.interfaces import LogHandler, LogLevel
from py_core.logging.formatters import ConsoleFormatter, JSONFormatter, TextFormatter


class ConsoleHandler(LogHandler):
    """Console handler with colored output"""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG, use_colors: bool = True):
        super().__init__(level)
        self.use_colors = use_colors
        self.set_formatter(ConsoleFormatter(show_colors=use_colors))
    
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to console"""
        formatted = log_entry.get('formatted', str(log_entry))
        print(formatted, file=sys.stderr if log_entry.get('level') in ['ERROR', 'CRITICAL'] else sys.stdout)
        sys.stdout.flush()


class FileHandler(LogHandler):
    """Async file handler with rotation support"""
    
    def __init__(self, 
                 file_path: str, 
                 level: LogLevel = LogLevel.DEBUG,
                 max_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 formatter_type: str = 'text'):
        super().__init__(level)
        self.file_path = Path(file_path)
        self.max_size = max_size
        self.backup_count = backup_count
        self._lock = asyncio.Lock()
        
        # Create formatter
        if formatter_type == 'json':
            self.set_formatter(JSONFormatter())
        else:
            self.set_formatter(TextFormatter())
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def _rotate_file(self) -> None:
        """Rotate log file if it exceeds max size"""
        if not self.file_path.exists():
            return
        
        if self.file_path.stat().st_size >= self.max_size:
            # Rotate existing backup files
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = self.file_path.with_suffix(f'.{i}')
                new_backup = self.file_path.with_suffix(f'.{i + 1}')
                if old_backup.exists():
                    old_backup.rename(new_backup)
            
            # Move current file to .1
            backup_path = self.file_path.with_suffix('.1')
            self.file_path.rename(backup_path)
    
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to file with rotation"""
        async with self._lock:
            await self._rotate_file()
            
            formatted = log_entry.get('formatted', str(log_entry))
            try:
                async with aiofiles.open(self.file_path, mode='a', encoding='utf-8') as f:
                    await f.write(formatted + '\n')
            except IOError as e:
                # Fallback to console if file writing fails
                print(f"Error writing to log file: {e}", file=sys.stderr)


class AsyncQueueHandler(LogHandler):
    """Async queue handler for non-blocking logging"""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG, queue_size: int = 1000):
        super().__init__(level)
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._consumer_task: Optional[asyncio.Task] = None
        self._handlers: list[LogHandler] = []
        self._running = False
    
    def add_handler(self, handler: LogHandler) -> None:
        """Add a child handler to process log entries"""
        self._handlers.append(handler)
    
    async def _consumer(self) -> None:
        """Consumer task that processes log entries from the queue"""
        while self._running or not self._queue.empty():
            try:
                log_entry = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                for handler in self._handlers:
                    await handler.handle(log_entry)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error in log consumer: {e}", file=sys.stderr)
    
    async def start(self) -> None:
        """Start the consumer task"""
        if not self._running:
            self._running = True
            self._consumer_task = asyncio.create_task(self._consumer())
    
    async def stop(self) -> None:
        """Stop the consumer task"""
        self._running = False
        if self._consumer_task:
            await self._consumer_task
            self._consumer_task = None
    
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to queue (non-blocking)"""
        try:
            await asyncio.wait_for(self._queue.put(log_entry), timeout=0.1)
        except asyncio.TimeoutError:
            # Queue is full, drop the log entry
            print("Log queue full, dropping log entry", file=sys.stderr)


class CloudWatchHandler(LogHandler):
    """CloudWatch handler for AWS CloudWatch Logs (placeholder for implementation)"""
    
    def __init__(self, 
                 log_group: str, 
                 log_stream: str,
                 level: LogLevel = LogLevel.INFO):
        super().__init__(level)
        self.log_group = log_group
        self.log_stream = log_stream
        self.set_formatter(JSONFormatter())
        # TODO: Implement AWS CloudWatch integration
        # This would require boto3 and proper AWS credentials
    
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to CloudWatch (placeholder)"""
        # TODO: Implement actual CloudWatch logging
        # For now, this is a placeholder
        formatted = log_entry.get('formatted', str(log_entry))
        print(f"[CloudWatch - {self.log_group}/{self.log_stream}] {formatted}")


class LogglyHandler(LogHandler):
    """Loggly handler for Loggly cloud logging (placeholder for implementation)"""
    
    def __init__(self, 
                 token: str,
                 level: LogLevel = LogLevel.INFO):
        super().__init__(level)
        self.token = token
        self.set_formatter(JSONFormatter())
        # TODO: Implement Loggly HTTP API integration
    
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry to Loggly (placeholder)"""
        # TODO: Implement actual Loggly logging
        # For now, this is a placeholder
        formatted = log_entry.get('formatted', str(log_entry))
        print(f"[Loggly] {formatted}")
