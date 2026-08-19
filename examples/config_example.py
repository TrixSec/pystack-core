"""
Configuration Example

This example demonstrates pystack-core's configuration system:
- Loading from multiple sources (environment, files)
- Type conversion and validation
- Pydantic schema validation
"""

import asyncio
import os
import tempfile
import yaml
from pydantic import BaseModel, Field
from py_core.app import AppConfig
from py_core.config import Config


class DatabaseConfig(BaseModel):
    """Database configuration schema"""
    url: str = Field(..., min_length=1)
    pool_size: int = Field(default=10, ge=1, le=100)
    timeout: int = Field(default=30, ge=1)


async def main():
    # Create a temporary YAML config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            "database": {
                "url": "postgresql://localhost/mydb",
                "pool_size": 20,
                "timeout": 60
            },
            "api": {
                "key": "secret-api-key",
                "timeout": 30
            }
        }
        yaml.dump(config_data, f)
        config_path = f.name
    
    try:
        # Set some environment variables
        os.environ["APP_API_TIMEOUT"] = "45"
        os.environ["APP_DEBUG"] = "true"
        
        # Create config object
        app_config = AppConfig(
            name="config-example",
            config_path=config_path,
            env_prefix="APP_"
        )
        
        config = Config(app_config)
        await config.load()
        
        print("=== Configuration Loading Example ===")
        print(f"Config sources: {config._sources}")
        print(f"Database URL: {config.get('database.url')}")
        print(f"Pool size: {config.get('database.pool_size')}")
        print(f"API timeout: {config.get('api.timeout')}")
        print(f"Debug mode: {config.get('app.debug')}")
        
        # Validate against Pydantic schema
        db_config = config.validate_section("database", DatabaseConfig)
        print(f"\nValidated database config: {db_config}")
        
        # Demonstrate type conversion
        print(f"\nType conversion examples:")
        print(f"String 'true' -> {config._convert_value('true')}")
        print(f"String '42' -> {config._convert_value('42')}")
        print(f"String '3.14' -> {config._convert_value('3.14')}")
        
        # Demonstrate nested value setting
        config.set("cache.enabled", True)
        config.set("cache.ttl", 3600)
        print(f"\nCache enabled: {config.get('cache.enabled')}")
        print(f"Cache TTL: {config.get('cache.ttl')}")
        
        # Cleanup
        await config.cleanup()
        
    finally:
        os.unlink(config_path)
        del os.environ["APP_API_TIMEOUT"]
        del os.environ["APP_DEBUG"]


if __name__ == "__main__":
    asyncio.run(main())
