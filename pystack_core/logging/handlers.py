"""
Log Handlers - File and rotating file handlers
"""

import asyncio
import os
from typing import Optional
from datetime import datetime
from pathlib import Path

from pystack_core.logging.logger import LogHandler, LogEntry, LogFormatter, JSONFormatter


class FileHandler(LogHandler):
    """File log handler"""
    
    def __init__(self, file_path: str, formatter: Optional[LogFormatter] = None):
        self._file_path = file_path
        self._formatter = formatter or JSONFormatter()
        self._lock = asyncio.Lock()
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def handle(self, entry: LogEntry):
        """Handle log entry by writing to file"""
        async with self._lock:
            formatted = self._formatter.format(entry)
            with open(self._file_path, 'a') as f:
                f.write(formatted + '\n')


class RotatingFileHandler(LogHandler):
    """Rotating file log handler"""
    
    def __init__(
        self,
        file_path: str,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        formatter: Optional[LogFormatter] = None
    ):
        self._file_path = file_path
        self._max_size = max_size
        self._backup_count = backup_count
        self._formatter = formatter or JSONFormatter()
        self._lock = asyncio.Lock()
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def handle(self, entry: LogEntry):
        """Handle log entry with rotation"""
        async with self._lock:
            # Check if rotation is needed
            if self._should_rotate():
                await self._rotate()
            
            formatted = self._formatter.format(entry)
            with open(self._file_path, 'a') as f:
                f.write(formatted + '\n')
    
    def _should_rotate(self) -> bool:
        """Check if file rotation is needed"""
        if not os.path.exists(self._file_path):
            return False
        return os.path.getsize(self._file_path) >= self._max_size
    
    async def _rotate(self):
        """Rotate log files"""
        if not os.path.exists(self._file_path):
            return
        
        # Remove oldest backup if needed
        oldest_backup = f"{self._file_path}.{self._backup_count}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        
        # Shift existing backups
        for i in range(self._backup_count - 1, 0, -1):
            old_file = f"{self._file_path}.{i}"
            new_file = f"{self._file_path}.{i + 1}"
            if os.path.exists(old_file):
                os.rename(old_file, new_file)
        
        # Rename current file to .1
        os.rename(self._file_path, f"{self._file_path}.1")
