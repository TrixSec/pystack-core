"""
Logging interfaces - Production-ready base interfaces for logging module
"""

from typing import Any, Dict, Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio


class LogLevel(Enum):
    """Log levels with numeric values for filtering"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Convert string to LogLevel"""
        try:
            return cls[level_str.upper()]
        except KeyError:
            return cls.INFO  # Default to INFO


class LogFormatter(ABC):
    """Base log formatter interface"""
    
    @abstractmethod
    def format(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry for output"""
        pass


class LogHandler(ABC):
    """Base log handler interface with async support"""
    
    def __init__(self, level: LogLevel = LogLevel.DEBUG):
        self.level = level
        self._formatter: Optional[LogFormatter] = None
        self._filters: list[Callable[[Dict[str, Any]], bool]] = []
    
    def set_formatter(self, formatter: LogFormatter) -> None:
        """Set the formatter for this handler"""
        self._formatter = formatter
    
    def add_filter(self, filter_func: Callable[[Dict[str, Any]], bool]) -> None:
        """Add a filter function"""
        self._filters.append(filter_func)
    
    def should_log(self, log_entry: Dict[str, Any]) -> bool:
        """Check if this log entry should be handled"""
        # Check level
        entry_level = LogLevel.from_string(log_entry.get('level', 'INFO'))
        if entry_level.value < self.level.value:
            return False
        
        # Check filters
        for filter_func in self._filters:
            if not filter_func(log_entry):
                return False
        
        return True
    
    @abstractmethod
    async def emit(self, log_entry: Dict[str, Any]) -> None:
        """Emit log entry"""
        pass
    
    async def handle(self, log_entry: Dict[str, Any]) -> None:
        """Handle log entry with formatting and filtering"""
        if not self.should_log(log_entry):
            return
        
        if self._formatter:
            log_entry['formatted'] = self._formatter.format(log_entry)
        
        await self.emit(log_entry)
