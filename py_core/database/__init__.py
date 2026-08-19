"""
Database module - Unified database interface with multiple backend support
"""

from py_core.database.database import Database
from py_core.database.interfaces import DatabaseBackend, QueryResult

__all__ = [
    "Database",
    "DatabaseBackend",
    "QueryResult",
]
