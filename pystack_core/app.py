"""
Application Core - Runtime and lifecycle management
"""

import asyncio
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import inspect


class AppState(Enum):
    """Application state"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "app"
    version: str = "1.0.0"
    debug: bool = False
    auto_start: bool = True


class App:
    """Application runtime with lifecycle management"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        self._config = config or AppConfig()
        self._state = AppState.INITIALIZING
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        self._middleware: List[Callable] = []
        self._context: Dict[str, Any] = {}
    
    def add_startup_hook(self, hook: Callable):
        """Add startup hook"""
        self._startup_hooks.append(hook)
    
    def add_shutdown_hook(self, hook: Callable):
        """Add shutdown hook"""
        self._shutdown_hooks.append(hook)
    
    def add_middleware(self, middleware: Callable):
        """Add middleware"""
        self._middleware.append(middleware)
    
    async def startup(self):
        """Execute startup sequence"""
        self._state = AppState.INITIALIZING
        
        # Execute startup hooks
        for hook in self._startup_hooks:
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()
        
        self._state = AppState.RUNNING
    
    async def shutdown(self):
        """Execute shutdown sequence"""
        self._state = AppState.STOPPING
        
        # Execute shutdown hooks in reverse order
        for hook in reversed(self._shutdown_hooks):
            if inspect.iscoroutinefunction(hook):
                await hook()
            else:
                hook()
        
        self._state = AppState.STOPPED
    
    async def run(self):
        """Run application"""
        await self.startup()
        try:
            # Main application loop
            while self._state == AppState.RUNNING:
                await asyncio.sleep(0.1)
        finally:
            await self.shutdown()
    
    def get_state(self) -> AppState:
        """Get current application state"""
        return self._state
    
    def set_context(self, key: str, value: Any):
        """Set context value"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self._context.get(key, default)
