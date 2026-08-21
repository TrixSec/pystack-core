"""
Database module - Multi-backend database support with SQLite and PostgreSQL
"""

from .database import SQLiteDatabase, PostgreSQLDatabase, DatabaseManager, DatabaseError, Transaction
from .interfaces import DatabaseInterface, DatabaseBackend, QueryResult

__all__ = [
    "SQLiteDatabase",
    "PostgreSQLDatabase",
    "DatabaseManager",
    "DatabaseError",
    "Transaction",
    "DatabaseInterface",
    "DatabaseBackend",
    "QueryResult",
]
