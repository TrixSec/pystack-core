"""
Database Example - demonstrating SQLite and database operations
"""

import asyncio
from pystack_core import SQLiteDatabase, DatabaseManager, Transaction

async def basic_sqlite_example():
    """Basic SQLite database operations"""
    print("=== Basic SQLite Example ===")
    
    db = SQLiteDatabase(":memory:")
    await db.connect()
    
    try:
        # Create table
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        print("Created users table")
        
        # Insert data
        await db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John", "john@example.com"))
        await db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Jane", "jane@example.com"))
        print("Inserted 2 users")
        
        # Query single row
        user = await db.fetch_one("SELECT * FROM users WHERE name = ?", ("John",))
        print(f"Found user: {user}")
        
        # Query all rows
        users = await db.fetch_all("SELECT * FROM users")
        print(f"All users: {users}")
        
        # Query single value
        count = await db.fetch_val("SELECT COUNT(*) FROM users")
        print(f"Total users: {count}")
        
    finally:
        await db.disconnect()

async def transaction_example():
    """Transaction management"""
    print("\n=== Transaction Example ===")
    
    db = SQLiteDatabase(":memory:")
    await db.connect()
    
    try:
        await db.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER)")
        await db.execute("INSERT INTO accounts (id, balance) VALUES (1, 100)")
        await db.execute("INSERT INTO accounts (id, balance) VALUES (2, 50)")
        print("Initial accounts created")
        
        # Transaction with commit
        await db.begin_transaction()
        await db.execute("UPDATE accounts SET balance = balance - 10 WHERE id = 1")
        await db.execute("UPDATE accounts SET balance = balance + 10 WHERE id = 2")
        await db.commit_transaction()
        print("Transaction committed")
        
        # Check balances
        account1 = await db.fetch_one("SELECT * FROM accounts WHERE id = 1")
        account2 = await db.fetch_one("SELECT * FROM accounts WHERE id = 2")
        print(f"Account 1: {account1}")
        print(f"Account 2: {account2}")
        
        # Transaction with rollback
        await db.begin_transaction()
        await db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        await db.rollback_transaction()
        print("Transaction rolled back")
        
        # Verify rollback
        account1_after = await db.fetch_one("SELECT * FROM accounts WHERE id = 1")
        print(f"Account 1 after rollback: {account1_after}")
        
    finally:
        await db.disconnect()

async def context_manager_example():
    """Transaction context manager"""
    print("\n=== Context Manager Example ===")
    
    db = SQLiteDatabase(":memory:")
    await db.connect()
    
    try:
        await db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER)")
        
        # Successful transaction
        async with Transaction(db):
            await db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Widget", 10))
            await db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Gadget", 20))
        print("Transaction committed successfully")
        
        # Failed transaction (auto-rollback)
        try:
            async with Transaction(db):
                await db.execute("INSERT INTO products (name, price) VALUES (?, ?)", ("Tool", 15))
                raise Exception("Simulated error")
        except Exception as e:
            print(f"Transaction rolled back due to error: {e}")
        
        # Check results
        products = await db.fetch_all("SELECT * FROM products")
        print(f"Products in database: {products}")
        
    finally:
        await db.disconnect()

async def batch_operations_example():
    """Batch query execution"""
    print("\n=== Batch Operations Example ===")
    
    db = SQLiteDatabase(":memory:")
    await db.connect()
    
    try:
        await db.execute("CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, department TEXT)")
        
        # Batch insert
        employees = [
            (1, "Alice", "Engineering"),
            (2, "Bob", "Marketing"),
            (3, "Charlie", "Engineering"),
            (4, "Diana", "Sales")
        ]
        result = await db.execute_many(
            "INSERT INTO employees (id, name, department) VALUES (?, ?, ?)",
            employees
        )
        print(f"Batch insert affected {result.affected_rows} rows")
        
        # Query all
        all_employees = await db.fetch_all("SELECT * FROM employees")
        print(f"Total employees: {len(all_employees)}")
        
    finally:
        await db.disconnect()

async def database_manager_example():
    """Database manager for unified backend management"""
    print("\n=== Database Manager Example ===")
    
    manager = DatabaseManager()
    await manager.connect()
    
    try:
        # Create table
        await manager.execute("CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)")
        
        # Insert settings
        await manager.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("theme", "dark"))
        await manager.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("language", "en"))
        
        # Query settings
        theme = await manager.fetch_one("SELECT * FROM settings WHERE key = ?", ("theme",))
        print(f"Theme setting: {theme}")
        
        # Get all settings
        all_settings = await manager.fetch_all("SELECT * FROM settings")
        print(f"All settings: {all_settings}")
        
    finally:
        await manager.disconnect()

async def connection_info_example():
    """Database connection information"""
    print("\n=== Connection Info Example ===")
    
    db = SQLiteDatabase(":memory:")
    await db.connect()
    
    try:
        info = db.get_connection_info()
        print(f"Connection info: {info}")
        print(f"Connected: {await db.is_connected()}")
        
    finally:
        await db.disconnect()
        print(f"Connected after disconnect: {await db.is_connected()}")

async def main():
    """Run all examples"""
    await basic_sqlite_example()
    await transaction_example()
    await context_manager_example()
    await batch_operations_example()
    await database_manager_example()
    await connection_info_example()

if __name__ == "__main__":
    asyncio.run(main())
