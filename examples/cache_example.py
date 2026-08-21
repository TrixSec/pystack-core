"""
Cache Example - demonstrating multi-backend caching
"""

import asyncio
from pystack_core import MemoryCache, CacheManager, CacheBackend

async def memory_cache_example():
    """Memory cache with LRU eviction"""
    print("=== Memory Cache Example ===")
    
    cache = MemoryCache(max_size=100, default_ttl=3600)
    
    # Set and get values
    await cache.set("user:1", {"name": "John", "age": 30})
    await cache.set("user:2", {"name": "Jane", "age": 25})
    
    user1 = await cache.get("user:1")
    print(f"User 1: {user1}")
    
    # Non-existent key
    user3 = await cache.get("user:3")
    print(f"User 3 (non-existent): {user3}")
    
    # Check existence
    exists = await cache.exists("user:1")
    print(f"User 1 exists: {exists}")
    
    # Delete
    await cache.delete("user:1")
    user1_after = await cache.get("user:1")
    print(f"User 1 after delete: {user1_after}")
    
    # Statistics
    stats = cache.get_stats()
    print(f"Cache stats: hits={stats.hits}, misses={stats.misses}, hit_rate={stats.hit_rate:.2%}")

async def ttl_example():
    """Cache with TTL expiration"""
    print("\n=== TTL Example ===")
    
    cache = MemoryCache(default_ttl=3600)
    
    # Set with specific TTL
    await cache.set("session:abc", "user_data", ttl=1)  # 1 second
    print("Set session with 1 second TTL")
    
    # Immediate get
    session = await cache.get("session:abc")
    print(f"Session immediately: {session}")
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    session_expired = await cache.get("session:abc")
    print(f"Session after expiration: {session_expired}")

async def batch_operations_example():
    """Batch cache operations"""
    print("\n=== Batch Operations Example ===")
    
    cache = MemoryCache()
    
    # Set multiple values
    mapping = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    await cache.set_many(mapping)
    print("Set multiple keys")
    
    # Get multiple values
    keys = ["key1", "key2", "key4"]
    result = await cache.get_many(keys)
    print(f"Get multiple: {result}")
    
    # Delete multiple
    await cache.delete_many(["key1", "key2"])
    print("Deleted key1 and key2")

async def counter_operations_example():
    """Increment/decrement operations"""
    print("\n=== Counter Operations Example ===")
    
    cache = MemoryCache()
    
    # Increment
    count1 = await cache.increment("counter", 5)
    print(f"Counter after +5: {count1}")
    
    count2 = await cache.increment("counter", 3)
    print(f"Counter after +3: {count2}")
    
    # Decrement
    count3 = await cache.decrement("counter", 2)
    print(f"Counter after -2: {count3}")

async def cache_manager_example():
    """Cache manager for unified backend management"""
    print("\n=== Cache Manager Example ===")
    
    manager = CacheManager()
    
    # Use default backend (memory)
    await manager.set("app:config", {"debug": True, "port": 8080})
    config = await manager.get("app:config")
    print(f"Config: {config}")
    
    # Get statistics for all backends
    all_stats = manager.get_all_stats()
    print(f"All backend stats: {all_stats}")

async def lru_eviction_example():
    """LRU eviction demonstration"""
    print("\n=== LRU Eviction Example ===")
    
    cache = MemoryCache(max_size=3)  # Small cache for demonstration
    
    # Fill cache
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.set("key3", "value3")
    print("Cache filled with 3 items")
    
    # Access key1 to make it recently used
    await cache.get("key1")
    print("Accessed key1")
    
    # Add new item (should evict key2)
    await cache.set("key4", "value4")
    print("Added key4 (should evict key2)")
    
    # Check what remains
    key1_exists = await cache.exists("key1")
    key2_exists = await cache.exists("key2")
    key3_exists = await cache.exists("key3")
    key4_exists = await cache.exists("key4")
    
    print(f"key1 exists: {key1_exists}")
    print(f"key2 exists: {key2_exists}")
    print(f"key3 exists: {key3_exists}")
    print(f"key4 exists: {key4_exists}")

async def main():
    """Run all examples"""
    await memory_cache_example()
    await ttl_example()
    await batch_operations_example()
    await counter_operations_example()
    await cache_manager_example()
    await lru_eviction_example()

if __name__ == "__main__":
    asyncio.run(main())
