"""
Database interfaces - Base interfaces for database module
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class DatabaseBackend(Enum):
    """Database backend types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


@dataclass
class QueryResult:
    """Query result with metadata"""
    rows: List[Dict[str, Any]]
    affected_rows: int
    execution_time: float
