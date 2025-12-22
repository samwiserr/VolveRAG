"""
Dependency Injection container for managing service dependencies.

This module provides a simple but effective DI container that eliminates
global state and makes dependencies explicit and testable.
"""
from typing import TypeVar, Type, Callable, Optional, Any, Dict
from functools import lru_cache

T = TypeVar('T')


class ServiceContainer:
    """
    Simple dependency injection container.
    
    Provides service registration and retrieval with support for:
    - Singleton services (same instance returned)
    - Factory functions (new instance each time)
    - Type-based registration
    """
    
    def __init__(self):
        """Initialize empty container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, service_type: Type[T], instance: T) -> None:
        """
        Register a service instance (singleton).
        
        Args:
            service_type: Type/class of the service
            instance: Service instance to register
        """
        self._services[service_type] = instance
        # Also store as singleton
        self._singletons[service_type] = instance
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for creating service instances.
        
        Args:
            service_type: Type/class of the service
            factory: Function that creates a new instance
        """
        self._factories[service_type] = factory
    
    def get(self, service_type: Type[T]) -> T:
        """
        Get service instance.
        
        Priority:
        1. Registered singleton instance
        2. Factory function (creates new instance)
        3. Raises KeyError if not found
        
        Args:
            service_type: Type/class of the service
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
        """
        # Check for singleton first
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check for registered instance
        if service_type in self._services:
            instance = self._services[service_type]
            self._singletons[service_type] = instance
            return instance
        
        # Check for factory
        if service_type in self._factories:
            instance = self._factories[service_type]()
            # Cache as singleton if factory returns same instance
            self._singletons[service_type] = instance
            return instance
        
        raise KeyError(f"Service {service_type.__name__} not registered")
    
    def get_or_none(self, service_type: Type[T]) -> Optional[T]:
        """
        Get service instance or None if not registered.
        
        Args:
            service_type: Type/class of the service
            
        Returns:
            Service instance or None
        """
        try:
            return self.get(service_type)
        except KeyError:
            return None
    
    def clear(self) -> None:
        """Clear all registered services (useful for testing)."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
    
    def is_registered(self, service_type: Type[T]) -> bool:
        """
        Check if service is registered.
        
        Args:
            service_type: Type/class of the service
            
        Returns:
            True if registered, False otherwise
        """
        return (
            service_type in self._services or
            service_type in self._factories or
            service_type in self._singletons
        )


# Global container instance (singleton pattern for the container itself)
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """
    Get global service container (singleton).
    
    Returns:
        ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset global container (useful for testing)."""
    global _container
    _container = None

