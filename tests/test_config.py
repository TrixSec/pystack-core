"""
Production-ready configuration tests
"""

import pytest
import os
import tempfile
from pathlib import Path
import yaml
import json
import asyncio

from py_core.config import Config, AppConfig, ConfigSource


class TestConfigLoading:
    """Test configuration loading from various sources"""
    
    def test_load_defaults(self):
        """Test loading default configuration"""
        config = Config(AppConfig(name="test-app"))
        config._load_defaults()
        
        assert config.get("app.name") == "test-app"
        assert config.get("app.environment") == "development"
        assert config.get("app.debug") is False
    
    def test_load_from_yaml(self):
        """Test loading configuration from YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"database": {"url": "postgresql://localhost/db"}}, f)
            yaml_path = f.name
        
        try:
            config = Config(AppConfig(config_path=yaml_path))
            # Load directly without async for testing
            import asyncio
            asyncio.run(config._load_from_file(yaml_path))
            
            assert config.get("database.url") == "postgresql://localhost/db"
            assert ConfigSource.YAML in config._sources
        finally:
            os.unlink(yaml_path)
    
    def test_load_from_json(self):
        """Test loading configuration from JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"api": {"key": "secret123"}}, f)
            json_path = f.name
        
        try:
            config = Config(AppConfig(config_path=json_path))
            import asyncio
            asyncio.run(config._load_from_file(json_path))
            
            assert config.get("api.key") == "secret123"
            assert ConfigSource.JSON in config._sources
        finally:
            os.unlink(json_path)
    
    def test_load_from_environment(self):
        """Test loading configuration from environment variables"""
        os.environ["TEST_DATABASE_URL"] = "postgresql://test/db"
        os.environ["TEST_API_KEY"] = "test-key"
        
        try:
            config = Config(AppConfig(env_prefix="TEST_"))
            config._load_from_environment()
            
            assert config.get("database.url") == "postgresql://test/db"
            assert config.get("api.key") == "test-key"
            assert ConfigSource.ENVIRONMENT in config._sources
        finally:
            del os.environ["TEST_DATABASE_URL"]
            del os.environ["TEST_API_KEY"]
    
    def test_config_merging(self):
        """Test configuration merging with environment overrides"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"database": {"url": "postgresql://file/db", "pool_size": 10}}, f)
            yaml_path = f.name
        
        os.environ["TEST_DATABASE_URL"] = "postgresql://env/db"
        
        try:
            config = Config(AppConfig(config_path=yaml_path, env_prefix="TEST_"))
            import asyncio
            asyncio.run(config._load_from_file(yaml_path))
            config._load_from_environment()
            
            # Environment should override file
            assert config.get("database.url") == "postgresql://env/db"
            # File settings should be preserved
            assert config.get("database.pool_size") == 10
        finally:
            os.unlink(yaml_path)
            del os.environ["TEST_DATABASE_URL"]


class TestConfigTypeConversion:
    """Test configuration type conversion"""
    
    def test_boolean_conversion(self):
        """Test boolean type conversion"""
        config = Config(AppConfig())
        assert config._convert_value("true") is True
        assert config._convert_value("false") is False
        assert config._convert_value("yes") is True
        assert config._convert_value("no") is False
        assert config._convert_value("1") is True
        assert config._convert_value("0") is False
    
    def test_integer_conversion(self):
        """Test integer type conversion"""
        config = Config(AppConfig())
        assert config._convert_value("42") == 42
        assert config._convert_value("-10") == -10
    
    def test_float_conversion(self):
        """Test float type conversion"""
        config = Config(AppConfig())
        assert config._convert_value("3.14") == 3.14
        assert config._convert_value("-0.5") == -0.5
    
    def test_json_conversion(self):
        """Test JSON type conversion"""
        config = Config(AppConfig())
        result = config._convert_value('{"key": "value"}')
        assert result == {"key": "value"}
        
        result = config._convert_value('[1, 2, 3]')
        assert result == [1, 2, 3]


class TestConfigValidation:
    """Test configuration validation with Pydantic"""
    
    def test_validate_with_pydantic(self):
        """Test validation against Pydantic schema"""
        from pydantic import BaseModel, Field
        
        class DatabaseConfig(BaseModel):
            url: str = Field(..., min_length=1)
            pool_size: int = Field(default=10, ge=1, le=100)
        
        config = Config(AppConfig())
        config._config = {
            "url": "postgresql://localhost/db",
            "pool_size": 20
        }
        
        validated = config.validate(DatabaseConfig)
        assert validated.url == "postgresql://localhost/db"
        assert validated.pool_size == 20
    
    def test_validation_error(self):
        """Test validation error handling"""
        from pydantic import BaseModel, Field, ValidationError
        
        class InvalidConfig(BaseModel):
            url: str = Field(..., min_length=10)
        
        config = Config(AppConfig())
        config._config = {"url": "short"}
        
        with pytest.raises(ValueError, match="Configuration validation failed"):
            config.validate(InvalidConfig)


class TestConfigUtilityMethods:
    """Test configuration utility methods"""
    
    def test_get_with_default(self):
        """Test getting values with defaults"""
        config = Config(AppConfig())
        config._config = {"existing": "value"}
        
        assert config.get("existing") == "value"
        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"
    
    def test_set_nested_value(self):
        """Test setting nested configuration values"""
        config = Config(AppConfig())
        config.set("database.url", "postgresql://localhost/db")
        config.set("database.pool_size", 20)
        
        assert config.get("database.url") == "postgresql://localhost/db"
        assert config.get("database.pool_size") == 20
    
    def test_get_section(self):
        """Test getting configuration sections"""
        config = Config(AppConfig())
        config._config = {
            "database": {"url": "postgresql://localhost/db", "pool_size": 20},
            "api": {"key": "secret"}
        }
        
        db_section = config.get_section("database")
        assert db_section.get("url") == "postgresql://localhost/db"
        assert db_section.get("pool_size") == 20
        assert db_section.get("api.key") is None
    
    def test_has_key(self):
        """Test checking if keys exist"""
        config = Config(AppConfig())
        config._config = {"existing": "value", "nested": {"key": "value"}}
        
        assert config.has("existing") is True
        assert config.has("nonexistent") is False
        assert config.has("nested.key") is True


class TestConfigAsync:
    """Test async configuration operations"""
    
    @pytest.mark.asyncio
    async def test_async_load(self):
        """Test async configuration loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"test": "value"}, f)
            yaml_path = f.name
        
        try:
            config = Config(AppConfig(config_path=yaml_path))
            await config.load()
            
            assert config.get("test") == "value"
            assert config._loaded is True
        finally:
            os.unlink(yaml_path)
    
    @pytest.mark.asyncio
    async def test_async_cleanup(self):
        """Test async configuration cleanup"""
        config = Config(AppConfig())
        config._config = {"test": "value"}
        config._loaded = True
        
        await config.cleanup()
        
        assert config._config == {}
        assert config._loaded is False


class TestConfigErrors:
    """Test error handling in configuration"""
    
    def test_invalid_file_format(self):
        """Test handling of invalid file format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid content")
            txt_path = f.name
        
        try:
            config = Config(AppConfig(config_path=txt_path))
            import asyncio
            with pytest.raises(ValueError, match="Unsupported config file format"):
                asyncio.run(config._load_from_file(txt_path))
        finally:
            os.unlink(txt_path)
    
    def test_invalid_yaml_content(self):
        """Test handling of invalid YAML content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [unclosed")
            yaml_path = f.name
        
        try:
            config = Config(AppConfig(config_path=yaml_path))
            import asyncio
            with pytest.raises(ValueError, match="Error parsing config file"):
                asyncio.run(config._load_from_file(yaml_path))
        finally:
            os.unlink(yaml_path)
    
    def test_invalid_json_content(self):
        """Test handling of invalid JSON content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            json_path = f.name
        
        try:
            config = Config(AppConfig(config_path=json_path))
            import asyncio
            with pytest.raises(ValueError, match="Error parsing config file"):
                asyncio.run(config._load_from_file(json_path))
        finally:
            os.unlink(json_path)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file"""
        config = Config(AppConfig(config_path="/nonexistent/path.yaml"))
        import asyncio
        # Should not raise error, just return without loading
        asyncio.run(config._load_from_file("/nonexistent/path.yaml"))
        assert config._config == {}