"""
Middleware Pipeline - Production-ready cross-cutting concerns management
"""

from typing import Callable, Any, Awaitable, List, Optional, Dict
from abc import ABC, abstractmethod
import time
import uuid
import asyncio


class MiddlewareInterface(ABC):
    """Base middleware interface"""
    
    @abstractmethod
    async def process(self, 
                     request: Any, 
                     next_handler: Callable[[Any], Awaitable[Any]]) -> Any:
        """Process request through middleware"""
        pass


class MiddlewarePipeline:
    """Production-ready middleware pipeline manager with performance tracking"""
    
    def __init__(self):
        self._middleware: List[MiddlewareInterface] = []
        self._compiled_handler: Optional[Callable] = None
        self._middleware_order: Dict[str, int] = {}
        self._execution_times: Dict[str, float] = {}
        self._total_executions: int = 0
    
    def add_middleware(self, middleware: MiddlewareInterface, order: Optional[int] = None) -> None:
        """Add middleware to the pipeline with optional ordering"""
        middleware_name = middleware.__class__.__name__
        
        if order is not None:
            self._middleware_order[middleware_name] = order
            # Re-sort middleware based on order
            self._middleware.sort(key=lambda m: self._middleware_order.get(m.__class__.__name__, float('inf')))
        else:
            self._middleware.append(middleware)
        
        self._compiled_handler = None  # Force recompilation
    
    def remove_middleware(self, middleware_class: type) -> bool:
        """Remove middleware by class"""
        for i, middleware in enumerate(self._middleware):
            if isinstance(middleware, middleware_class):
                middleware_name = middleware.__class__.__name__
                self._middleware.pop(i)
                if middleware_name in self._middleware_order:
                    del self._middleware_order[middleware_name]
                self._compiled_handler = None
                return True
        return False
    
    def _compile_handler(self, base_handler: Callable) -> Callable:
        """Compose middleware into a single async function with error handling"""
        handler = base_handler
        for middleware in reversed(self._middleware):
            def create_wrapper(m, h):
                async def wrapper(req):
                    start_time = time.time()
                    middleware_name = m.__class__.__name__
                    
                    try:
                        result = await m.process(req, h)
                        exec_time = time.time() - start_time
                        self._execution_times[middleware_name] = exec_time
                        return result
                    except Exception as e:
                        exec_time = time.time() - start_time
                        self._execution_times[f"{middleware_name}_error"] = exec_time
                        raise  # Re-raise to allow error handling middleware
                return wrapper
            handler = create_wrapper(middleware, handler)
        return handler
    
    async def execute(self, request: Any, handler: Callable) -> Any:
        """Execute the middleware pipeline with performance tracking"""
        self._total_executions += 1
        start_time = time.time()
        
        if not self._compiled_handler:
            self._compiled_handler = self._compile_handler(handler)
        
        try:
            result = await self._compiled_handler(request)
            return result
        finally:
            total_time = time.time() - start_time
            self._execution_times["total_pipeline"] = total_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for middleware execution"""
        return {
            "total_executions": self._total_executions,
            "execution_times": self._execution_times.copy(),
            "middleware_count": len(self._middleware),
            "middleware_order": [m.__class__.__name__ for m in self._middleware]
        }
    
    def reset_performance_stats(self) -> None:
        """Reset performance statistics"""
        self._execution_times.clear()
        self._total_executions = 0


class RequestIDMiddleware(MiddlewareInterface):
    """Middleware that adds unique request IDs to requests"""
    
    async def process(self, request: Any, next_handler: Callable) -> Any:
        """Add request ID if not present"""
        if hasattr(request, 'request_id') and not request.request_id:
            request.request_id = str(uuid.uuid4())
        elif not hasattr(request, 'request_id'):
            # For dict-like requests
            if isinstance(request, dict):
                request['request_id'] = str(uuid.uuid4())
        
        return await next_handler(request)


class TimingMiddleware(MiddlewareInterface):
    """Middleware that tracks request timing"""
    
    def __init__(self):
        self.request_times: Dict[str, float] = {}
    
    async def process(self, request: Any, next_handler: Callable) -> Any:
        """Track request timing"""
        request_id = getattr(request, 'request_id', str(uuid.uuid4()))
        start_time = time.time()
        
        try:
            result = await next_handler(request)
            return result
        finally:
            duration = time.time() - start_time
            self.request_times[request_id] = duration
    
    def get_average_time(self) -> float:
        """Get average request time"""
        if not self.request_times:
            return 0.0
        return sum(self.request_times.values()) / len(self.request_times)
