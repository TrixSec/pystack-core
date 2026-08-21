"""
Middleware Pipeline
"""

from typing import Callable, List, Any, Optional
import inspect


class MiddlewarePipeline:
    """Middleware pipeline for request/response processing"""
    
    def __init__(self):
        self._middleware: List[Callable] = []
    
    def add(self, middleware: Callable):
        """Add middleware to pipeline"""
        self._middleware.append(middleware)
    
    async def execute(self, context: Any, handler: Optional[Callable] = None) -> Any:
        """Execute middleware pipeline"""
        if not self._middleware:
            if handler:
                if inspect.iscoroutinefunction(handler):
                    return await handler(context)
                else:
                    return handler(context)
            return context
        
        # Build middleware chain
        pipeline = self._build_pipeline(handler)
        
        # Execute pipeline
        if inspect.iscoroutinefunction(pipeline):
            return await pipeline(context)
        else:
            return pipeline(context)
    
    def _build_pipeline(self, handler: Optional[Callable] = None) -> Callable:
        """Build middleware chain"""
        if not self._middleware:
            return handler or (lambda ctx: ctx)
        
        # Build chain from last to first
        chain = handler or (lambda ctx: ctx)
        
        for middleware in reversed(self._middleware):
            def create_wrapper(middleware, next_handler):
                async def async_wrapper(context):
                    if inspect.iscoroutinefunction(middleware):
                        return await middleware(context, next_handler)
                    else:
                        return middleware(context, next_handler)
                
                def sync_wrapper(context):
                    return middleware(context, next_handler)
                
                return async_wrapper if inspect.iscoroutinefunction(middleware) else sync_wrapper
            
            chain = create_wrapper(middleware, chain)
        
        return chain
    
    def clear(self):
        """Clear all middleware"""
        self._middleware.clear()
    
    def __len__(self) -> int:
        """Get middleware count"""
        return len(self._middleware)
