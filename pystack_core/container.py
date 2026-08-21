"""
Dependency Injection Container
"""

from typing import Type, Dict, Any, Callable, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ServiceLifetime(Enum):
    """Service lifetime"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceDescriptor:
    """Service descriptor"""
    service_type: Type
    implementation: Union[Type, Callable, Any]
    lifetime: ServiceLifetime
    instance: Optional[Any] = None


class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type, implementation: Union[Type, Callable, Any]):
        """Register singleton service"""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON
        )
    
    def register_transient(self, service_type: Type, implementation: Union[Type, Callable]):
        """Register transient service"""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT
        )
    
    def register_scoped(self, service_type: Type, implementation: Union[Type, Callable]):
        """Register scoped service"""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED
        )
    
    def register_instance(self, service_type: Type, instance: Any):
        """Register service instance"""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=instance,
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance
        )
        self._instances[service_type] = instance
    
    def resolve(self, service_type: Type) -> Any:
        """Resolve service"""
        if service_type not in self._services:
            raise ServiceNotFoundError(f"Service {service_type} not registered")
        
        descriptor = self._services[service_type]
        
        # Return existing instance for singletons
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._instances:
                return self._instances[service_type]
            
            instance = self._create_instance(descriptor)
            self._instances[service_type] = instance
            return instance
        
        # Create new instance for transient
        if descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._create_instance(descriptor)
        
        # Create new instance for scoped
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._create_instance(descriptor)
        
        raise ServiceNotFoundError(f"Cannot resolve service {service_type}")
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create service instance"""
        implementation = descriptor.implementation
        
        # If it's already an instance
        if not callable(implementation):
            return implementation
        
        # If it's a class, instantiate it
        if isinstance(implementation, type):
            return implementation()
        
        # If it's a factory function
        return implementation()
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service is registered"""
        return service_type in self._services
    
    def clear(self):
        """Clear all services"""
        self._services.clear()
        self._instances.clear()


class ServiceNotFoundError(Exception):
    """Service not found error"""
    pass
