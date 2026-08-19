"""
Dependency Injection Container - Production-ready implementation
"""

from typing import Type, TypeVar, Callable, Any, Dict, Optional, get_type_hints
from abc import ABC
import inspect
import functools

T = TypeVar('T')


class Container:
    """Production-ready dependency injection container with lifecycle management"""
    
    def __init__(self):
        self._factories: Dict[Type, Callable] = {}
        self._instances: Dict[Type, Any] = {}
        self._singletons: set[Type] = set()
        self._initializing: set[Type] = set()
        self._decorators: Dict[Type, list[Callable]] = {}
    
    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = True) -> None:
        """Register an implementation for an interface"""
        def factory():
            return implementation()
        
        self._factories[interface] = factory
        if singleton:
            self._singletons.add(interface)
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register an instance for an interface (always singleton)"""
        self._instances[interface] = instance
        self._singletons.add(interface)
    
    def register_factory(self, interface: Type[T], factory: Callable[..., T], singleton: bool = True) -> None:
        """Register a factory function for an interface"""
        self._factories[interface] = factory
        if singleton:
            self._singletons.add(interface)
    
    def register_decorator(self, interface: Type[T], decorator: Callable[[T], T]) -> None:
        """Register a decorator to be applied to instances of a type"""
        if interface not in self._decorators:
            self._decorators[interface] = []
        self._decorators[interface].append(decorator)
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve an interface to its implementation with dependency injection"""
        # Check if instance already exists (singleton)
        if interface in self._instances:
            return self._instances[interface]
        
        # Check for circular dependency
        if interface in self._initializing:
            raise RuntimeError(f"Circular dependency detected for {interface}")
        
        # Get factory
        if interface not in self._factories:
            # Try to auto-register concrete classes
            if isinstance(interface, type) and hasattr(interface, '__init__'):
                self._factories[interface] = interface
                # Don't auto-add to singletons - let it be transient by default
            else:
                raise RuntimeError(f"No factory registered for {interface}")
        
        # Initialize
        self._initializing.add(interface)
        try:
            factory = self._factories[interface]
            
            # Check if factory expects container argument
            sig = inspect.signature(factory)
            if 'container' in sig.parameters:
                instance = factory(container=self)
            else:
                instance = factory()
            
            # Apply decorators if any
            if interface in self._decorators:
                for decorator in self._decorators[interface]:
                    instance = decorator(instance)
            
            # Store if singleton
            if interface in self._singletons:
                self._instances[interface] = instance
            
            return instance
        finally:
            self._initializing.discard(interface)
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if an interface is registered"""
        return interface in self._factories or interface in self._instances
    
    def reset(self) -> None:
        """Reset the container (clear all instances)"""
        self._instances.clear()
        self._initializing.clear()
    
    def inject(self, func: Callable) -> Callable:
        """Decorator to inject dependencies into a function based on type hints"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get type hints
            hints = get_type_hints(func)
            
            # Inject dependencies
            for param_name, param_type in hints.items():
                if param_name not in kwargs and self.is_registered(param_type):
                    kwargs[param_name] = self.resolve(param_type)
            
            return func(*args, **kwargs)
        return wrapper
