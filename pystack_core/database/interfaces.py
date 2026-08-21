"""
Database Interfaces
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum


class DatabaseBackend(Enum):
    """Database backend types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


@dataclass
class QueryResult:
    """Query result"""
    rows: List[Dict[str, Any]]
    affected_rows: int = 0
    execution_time: float = 0.0


class DatabaseInterface(ABC):
    """Interface for database implementations"""
    
    @abstractmethod
    async def connect(self):
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close database connection"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if connected to database"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute SQL query"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        pass
    
    @abstractmethod
    async def fetch_val(self, query: str, params: Optional[tuple] = None) -> Any:
        """Fetch single value"""
        pass
    
    @abstractmethod
    async def begin_transaction(self):
        """Begin transaction"""
        pass
    
    @abstractmethod
    async def commit_transaction(self):
        """Commit transaction"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self):
        """Rollback transaction"""
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[tuple]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        pass
