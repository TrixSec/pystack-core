"""
Database Implementation with SQLite and PostgreSQL support
"""

import asyncio
import time
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import sqlite3

from pystack_core.database.interfaces import DatabaseInterface, DatabaseBackend, QueryResult


class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation"""
    
    def __init__(self, database_path: str = ":memory:"):
        self._database_path = database_path
        self._connection = None
        self._in_transaction = False
        self._connection_info = {"backend": DatabaseBackend.SQLITE, "path": database_path}
    
    async def connect(self):
        """Establish database connection"""
        self._connection = sqlite3.connect(self._database_path)
        self._connection.row_factory = sqlite3.Row
    
    async def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    async def is_connected(self) -> bool:
        """Check if connected to database"""
        return self._connection is not None
    
    async def execute(self, query: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute SQL query"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        start_time = time.time()
        cursor = self._connection.cursor()
        
        try:
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            
            # Only commit if not in a transaction
            if not self._in_transaction:
                self._connection.commit()
            
            return QueryResult(
                rows=[dict(row) for row in cursor.fetchall()],
                affected_rows=affected_rows,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            if not self._in_transaction:
                self._connection.rollback()
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        finally:
            cursor.close()
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    async def fetch_val(self, query: str, params: Optional[tuple] = None) -> Any:
        """Fetch single value"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
    
    async def begin_transaction(self):
        """Begin transaction"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        if self._in_transaction:
            raise RuntimeError("Transaction already in progress")
        
        self._connection.execute("BEGIN TRANSACTION")
        self._in_transaction = True
    
    async def commit_transaction(self):
        """Commit transaction"""
        if not self._in_transaction:
            raise RuntimeError("No transaction in progress")
        
        self._connection.commit()
        self._in_transaction = False
    
    async def rollback_transaction(self):
        """Rollback transaction"""
        if not self._in_transaction:
            raise RuntimeError("No transaction in progress")
        
        self._connection.rollback()
        self._in_transaction = False
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        start_time = time.time()
        cursor = self._connection.cursor()
        
        try:
            cursor.executemany(query, params_list)
            affected_rows = cursor.rowcount
            
            # Only commit if not in a transaction
            if not self._in_transaction:
                self._connection.commit()
            
            return QueryResult(
                rows=[],
                affected_rows=affected_rows,
                execution_time=time.time() - start_time
            )
        except Exception as e:
            if not self._in_transaction:
                self._connection.rollback()
            raise DatabaseError(f"Batch execution failed: {str(e)}") from e
        finally:
            cursor.close()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return self._connection_info.copy()


class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation (placeholder for asyncpg integration)"""
    
    def __init__(self, host: str = "localhost", port: int = 5432, database: str = "postgres", user: str = "postgres", password: str = ""):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._connection = None
        self._pool = None
        self._in_transaction = False
        self._connection_info = {
            "backend": DatabaseBackend.POSTGRESQL,
            "host": host,
            "port": port,
            "database": database,
            "user": user
        }
    
    async def connect(self):
        """Establish database connection"""
        # In production, use asyncpg for async PostgreSQL
        # For now, use SQLite as fallback
        print(f"PostgreSQL connection not yet implemented. Using SQLite fallback.")
        self._sqlite = SQLiteDatabase(":memory:")
        await self._sqlite.connect()
        self._connection = self._sqlite._connection
    
    async def disconnect(self):
        """Close database connection"""
        if hasattr(self, '_sqlite'):
            await self._sqlite.disconnect()
            self._connection = None
    
    async def is_connected(self) -> bool:
        """Check if connected to database"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.is_connected()
        return False
    
    async def execute(self, query: str, params: Optional[tuple] = None) -> QueryResult:
        """Execute SQL query"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.execute(query, params)
        raise RuntimeError("Not connected to database")
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.fetch_one(query, params)
        raise RuntimeError("Not connected to database")
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.fetch_all(query, params)
        raise RuntimeError("Not connected to database")
    
    async def fetch_val(self, query: str, params: Optional[tuple] = None) -> Any:
        """Fetch single value"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.fetch_val(query, params)
        raise RuntimeError("Not connected to database")
    
    async def begin_transaction(self):
        """Begin transaction"""
        if hasattr(self, '_sqlite'):
            await self._sqlite.begin_transaction()
    
    async def commit_transaction(self):
        """Commit transaction"""
        if hasattr(self, '_sqlite'):
            await self._sqlite.commit_transaction()
    
    async def rollback_transaction(self):
        """Rollback transaction"""
        if hasattr(self, '_sqlite'):
            await self._sqlite.rollback_transaction()
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        if hasattr(self, '_sqlite'):
            return await self._sqlite.execute_many(query, params_list)
        raise RuntimeError("Not connected to database")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return self._connection_info.copy()


class DatabaseManager:
    """Database manager for automatic backend selection"""
    
    def __init__(self, default_backend: DatabaseBackend = DatabaseBackend.SQLITE):
        self._default_backend = default_backend
        self._databases: Dict[DatabaseBackend, DatabaseInterface] = {}
        self.register_backend(DatabaseBackend.SQLITE, SQLiteDatabase())
    
    def register_backend(self, backend_type: DatabaseBackend, database: DatabaseInterface):
        """Register a database backend"""
        self._databases[backend_type] = database
    
    def get_backend(self, backend_type: Optional[DatabaseBackend] = None) -> DatabaseInterface:
        """Get database backend"""
        backend_type = backend_type or self._default_backend
        if backend_type not in self._databases:
            raise ValueError(f"Backend {backend_type} not registered")
        return self._databases[backend_type]
    
    def get_database(self, backend_type: Optional[DatabaseBackend] = None) -> DatabaseInterface:
        """Get database backend"""
        backend_type = backend_type or self._default_backend
        if backend_type not in self._databases:
            raise ValueError(f"Backend {backend_type} not registered")
        return self._databases[backend_type]
    
    async def connect(self, backend: Optional[DatabaseBackend] = None):
        """Connect to database"""
        database = self.get_database(backend)
        await database.connect()
    
    async def disconnect(self, backend: Optional[DatabaseBackend] = None):
        """Disconnect from database"""
        database = self.get_database(backend)
        await database.disconnect()
    
    async def execute(self, query: str, params: Optional[tuple] = None, backend: Optional[DatabaseBackend] = None) -> QueryResult:
        """Execute query"""
        database = self.get_database(backend)
        return await database.execute(query, params)
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None, backend: Optional[DatabaseBackend] = None) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        database = self.get_database(backend)
        return await database.fetch_one(query, params)
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None, backend: Optional[DatabaseBackend] = None) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        database = self.get_database(backend)
        return await database.fetch_all(query, params)


class DatabaseError(Exception):
    """Database error"""
    pass


class Transaction:
    """Context manager for database transactions"""
    
    def __init__(self, database: DatabaseInterface):
        self._database = database
    
    async def __aenter__(self):
        await self._database.begin_transaction()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self._database.commit_transaction()
        else:
            await self._database.rollback_transaction()
