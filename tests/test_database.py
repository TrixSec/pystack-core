"""
Tests for Database module
"""

import pytest
import asyncio
from pystack_core.database.database import (
    SQLiteDatabase, PostgreSQLDatabase, DatabaseManager,
    DatabaseError, Transaction
)
from pystack_core.database.interfaces import (
    DatabaseInterface, DatabaseBackend, QueryResult
)


class TestSQLiteDatabase:
    """Test SQLite database implementation"""
    
    @pytest.mark.asyncio
    async def test_sqlite_initialization(self):
        """Test SQLite database initialization"""
        db = SQLiteDatabase(":memory:")
        assert db._database_path == ":memory:"
        assert db._connection_info["backend"] == DatabaseBackend.SQLITE
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Test connect and disconnect"""
        db = SQLiteDatabase(":memory:")
        assert not await db.is_connected()
        await db.connect()
        assert await db.is_connected()
        await db.disconnect()
        assert not await db.is_connected()
    
    @pytest.mark.asyncio
    async def test_execute_query(self):
        """Test execute query"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        # Create table
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        
        # Insert data
        result = await db.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        assert result.affected_rows == 1
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_fetch_one(self):
        """Test fetch one"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        await db.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        
        row = await db.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is not None
        assert row["id"] == 1
        assert row["name"] == "test"
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_fetch_all(self):
        """Test fetch all"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        await db.execute("INSERT INTO test (id, name) VALUES (1, 'test1')")
        await db.execute("INSERT INTO test (id, name) VALUES (2, 'test2')")
        
        rows = await db.fetch_all("SELECT * FROM test ORDER BY id")
        assert len(rows) == 2
        assert rows[0]["name"] == "test1"
        assert rows[1]["name"] == "test2"
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_fetch_val(self):
        """Test fetch single value"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        await db.execute("INSERT INTO test (id, value) VALUES (1, 42)")
        
        value = await db.fetch_val("SELECT value FROM test WHERE id = 1")
        assert value == 42
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        """Test transaction commit"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        await db.begin_transaction()
        await db.execute("INSERT INTO test (id, value) VALUES (1, 100)")
        await db.commit_transaction()
        
        row = await db.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is not None
        assert row["value"] == 100
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test transaction rollback"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        await db.begin_transaction()
        await db.execute("INSERT INTO test (id, value) VALUES (1, 100)")
        await db.rollback_transaction()
        
        row = await db.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is None
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_execute_many(self):
        """Test execute many"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        params_list = [(1, 10), (2, 20), (3, 30)]
        result = await db.execute_many("INSERT INTO test (id, value) VALUES (?, ?)", params_list)
        assert result.affected_rows == 3
        
        rows = await db.fetch_all("SELECT * FROM test ORDER BY id")
        assert len(rows) == 3
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_transaction_context_manager(self):
        """Test transaction context manager"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        async with Transaction(db):
            await db.execute("INSERT INTO test (id, value) VALUES (1, 100)")
        
        row = await db.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is not None
        assert row["value"] == 100
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_transaction_context_manager_rollback(self):
        """Test transaction context manager rollback on error"""
        db = SQLiteDatabase(":memory:")
        await db.connect()
        
        await db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value INTEGER)")
        
        try:
            async with Transaction(db):
                await db.execute("INSERT INTO test (id, value) VALUES (1, 100)")
                raise Exception("Test error")
        except:
            pass
        
        row = await db.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is None
        
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_get_connection_info(self):
        """Test getting connection info"""
        db = SQLiteDatabase(":memory:")
        info = db.get_connection_info()
        assert info["backend"] == DatabaseBackend.SQLITE
        assert "path" in info


class TestDatabaseManager:
    """Test database manager"""
    
    @pytest.mark.asyncio
    async def test_database_manager_initialization(self):
        """Test database manager initialization"""
        manager = DatabaseManager()
        assert manager._default_backend == DatabaseBackend.SQLITE
    
    @pytest.mark.asyncio
    async def test_get_database(self):
        """Test getting database"""
        manager = DatabaseManager()
        db = manager.get_database(DatabaseBackend.SQLITE)
        assert isinstance(db, SQLiteDatabase)
    
    @pytest.mark.asyncio
    async def test_manager_operations(self):
        """Test database manager operations"""
        manager = DatabaseManager()
        await manager.connect()
        
        await manager.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        await manager.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        
        row = await manager.fetch_one("SELECT * FROM test WHERE id = 1")
        assert row is not None
        assert row["name"] == "test"
        
        await manager.disconnect()
    
    @pytest.mark.asyncio
    async def test_register_database(self):
        """Test registering custom database"""
        manager = DatabaseManager()
        custom_db = SQLiteDatabase(":memory:")
        manager.register_backend(DatabaseBackend.SQLITE, custom_db)
        db = manager.get_backend(DatabaseBackend.SQLITE)
        assert db is custom_db


class TestDatabaseInterfaces:
    """Test database interfaces"""
    
    def test_database_backend_enum(self):
        """Test database backend enum"""
        assert DatabaseBackend.SQLITE.value == "sqlite"
        assert DatabaseBackend.POSTGRESQL.value == "postgresql"
        assert DatabaseBackend.MYSQL.value == "mysql"
        assert DatabaseBackend.MONGODB.value == "mongodb"
    
    def test_query_result_dataclass(self):
        """Test query result dataclass"""
        result = QueryResult(rows=[{"id": 1}], affected_rows=1, execution_time=0.1)
        assert result.rows[0]["id"] == 1
        assert result.affected_rows == 1
        assert result.execution_time == 0.1


class TestPostgreSQLDatabase:
    """Test PostgreSQL database implementation"""
    
    @pytest.mark.asyncio
    async def test_postgresql_initialization(self):
        """Test PostgreSQL database initialization"""
        db = PostgreSQLDatabase(host="localhost", port=5432, database="test", user="postgres")
        assert db._host == "localhost"
        assert db._port == 5432
        assert db._connection_info["backend"] == DatabaseBackend.POSTGRESQL
    
    @pytest.mark.asyncio
    async def test_postgresql_fallback(self):
        """Test PostgreSQL fallback to SQLite"""
        db = PostgreSQLDatabase()
        await db.connect()
        # Should use SQLite fallback
        assert await db.is_connected()
        await db.disconnect()
