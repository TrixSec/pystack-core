"""
Log formatters - Production-ready formatters for different output formats
"""

from typing import Any, Dict
from datetime import datetime
import json


class ConsoleFormatter:
    """Colored console formatter for human-readable output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def __init__(self, show_colors: bool = True, show_timestamp: bool = True):
        self.show_colors = show_colors
        self.show_timestamp = show_timestamp
    
    def format(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry for console output"""
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        context = log_entry.get('context', {})
        extra = {k: v for k, v in log_entry.items() if k not in ['level', 'message', 'context', 'formatted']}
        
        # Build the log line
        parts = []
        
        # Add timestamp
        if self.show_timestamp:
            timestamp = context.get('timestamp', datetime.now().isoformat())
            parts.append(f"[{timestamp}]")
        
        # Add level with color
        if self.show_colors and level in self.COLORS:
            parts.append(f"{self.COLORS[level]}{level}{self.COLORS['RESET']}")
        else:
            parts.append(level)
        
        # Add message
        parts.append(message)
        
        # Add context info
        if context:
            context_str = ' '.join(f"{k}={v}" for k, v in context.items() if k != 'timestamp')
            if context_str:
                parts.append(f"({context_str})")
        
        # Add extra fields
        if extra:
            extra_str = ' '.join(f"{k}={v}" for k, v in extra.items())
            if extra_str:
                parts.append(f"[{extra_str}]")
        
        return ' '.join(parts)


class JSONFormatter:
    """JSON formatter for structured logging"""
    
    def __init__(self, indent: bool = False):
        self.indent = indent
    
    def format(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry as JSON"""
        # Remove the formatted field if it exists
        clean_entry = {k: v for k, v in log_entry.items() if k != 'formatted'}
        
        # Ensure timestamp is ISO format
        if 'context' in clean_entry and 'timestamp' in clean_entry['context']:
            timestamp = clean_entry['context']['timestamp']
            if isinstance(timestamp, (int, float)):
                clean_entry['context']['timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
        
        if self.indent:
            return json.dumps(clean_entry, indent=2, default=str)
        return json.dumps(clean_entry, default=str)


class TextFormatter:
    """Simple text formatter without colors"""
    
    def __init__(self, show_timestamp: bool = True):
        self.show_timestamp = show_timestamp
    
    def format(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry as plain text"""
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        context = log_entry.get('context', {})
        extra = {k: v for k, v in log_entry.items() if k not in ['level', 'message', 'context', 'formatted']}
        
        parts = []
        
        if self.show_timestamp:
            timestamp = context.get('timestamp', datetime.now().isoformat())
            parts.append(f"[{timestamp}]")
        
        parts.append(f"[{level}]")
        parts.append(message)
        
        if context:
            context_str = ' '.join(f"{k}={v}" for k, v in context.items() if k != 'timestamp')
            if context_str:
                parts.append(f"({context_str})")
        
        if extra:
            extra_str = ' '.join(f"{k}={v}" for k, v in extra.items())
            if extra_str:
                parts.append(f"[{extra_str}]")
        
        return ' '.join(parts)
