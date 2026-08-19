"""
Configuration module - Production-ready unified configuration management
"""

from typing import Any, Optional, Dict, Type, TypeVar, Union
from pathlib import Path
import os
from dataclasses import dataclass, field
from enum import Enum
import json

import yaml
try:
    import toml
except ImportError:
    try:
        import tomli as toml
    except ImportError:
        toml = None
from pydantic import BaseModel, Field, ValidationError


class ConfigSource(Enum):
    """Configuration source types"""
    ENVIRONMENT = "environment"
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"
    DEFAULTS = "defaults"


@dataclass
class AppConfig:
    """Application configuration"""
    name: str = "pystack-core-app"
    environment: str = "development"
    debug: bool = False
    config_path: Optional[str] = None
    env_prefix: str = "APP_"


class Config:
    """Configuration manager with support for multiple sources"""
    
    def __init__(self, app_config: AppConfig):
        self._app_config = app_config
        self._config: Dict[str, Any] = {}
        self._sources: list[ConfigSource] = []
        self._loaded = False
    
    async def load(self) -> None:
        """Load configuration from all sources"""
        if self._loaded:
            return
        
        # Load in priority order: defaults -> file -> environment
        self._load_defaults()
        
        if self._app_config.config_path:
            await self._load_from_file(self._app_config.config_path)
        
        self._load_from_environment()
        
        self._loaded = True
    
    def _load_defaults(self) -> None:
        """Load default configuration"""
        defaults = {
            "app": {
                "name": self._app_config.name,
                "environment": self._app_config.environment,
                "debug": self._app_config.debug,
            }
        }
        self._config = self._deep_merge(self._config, defaults)
        self._sources.append(ConfigSource.DEFAULTS)
    
    async def _load_from_file(self, path: str) -> None:
        """Load configuration from a file with error handling"""
        file_path = Path(path)
        
        if not file_path.exists():
            return
        
        try:
            content = file_path.read_text()
        except IOError as e:
            raise ValueError(f"Cannot read config file {path}: {e}")
        
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                file_config = yaml.safe_load(content) or {}
                self._sources.append(ConfigSource.YAML)
            elif file_path.suffix == '.json':
                file_config = json.loads(content)
                self._sources.append(ConfigSource.JSON)
            elif file_path.suffix == '.toml':
                if toml is None:
                    raise ValueError("TOML parsing requires 'toml' package for Python >=3.11 or 'tomli' for Python <3.11")
                file_config = toml.loads(content)
                self._sources.append(ConfigSource.TOML)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
            if file_config:
                self._config = self._deep_merge(self._config, file_config)
        except (yaml.YAMLError, json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Error parsing config file {path}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        env_config = {}
        prefix = self._app_config.env_prefix
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert APP_DATABASE_URL to database.url
                config_key = key[len(prefix):].lower()
                # Replace underscores with dots for nested config
                config_key = config_key.replace('_', '.')
                
                # Set nested value
                self._set_nested_value(env_config, config_key, value)
        
        if env_config:
            self._config = self._deep_merge(self._config, env_config)
            self._sources.append(ConfigSource.ENVIRONMENT)
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: str) -> None:
        """Set a nested value in config using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Try to convert to appropriate type
        current[keys[-1]] = self._convert_value(value)
    
    def _convert_value(self, value: Any) -> Any:
        """Convert value to appropriate type with better handling"""
        # If not a string, return as-is
        if not isinstance(value, str):
            return value
        
        # Try boolean
        if value.lower() in ('true', 'false', 'yes', 'no', '1', '0'):
            return value.lower() in ('true', 'yes', '1')
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try JSON for complex types
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # Return as string
        return value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        keys = key.split('.')
        current = self._config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_typed(self, key: str, type_: Type[T]) -> T:
        """Get a configuration value with type conversion"""
        value = self.get(key)
        if value is None:
            raise KeyError(f"Configuration key not found: {key}")
        
        try:
            return type_(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot convert {key}={value} to {type_}") from e
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self._set_nested_value(self._config, key, value)
    
    def validate(self, schema: Type[BaseModel]) -> BaseModel:
        """Validate configuration against a Pydantic schema with detailed errors"""
        try:
            return schema(**self._config)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    def validate_section(self, section: str, schema: Type[BaseModel]) -> BaseModel:
        """Validate a specific configuration section against a Pydantic schema"""
        section_config = self.get_section(section)
        try:
            return schema(**section_config._config)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed for section '{section}': {e}")
    
    def reload(self) -> None:
        """Reload configuration from all sources"""
        self._config.clear()
        self._sources.clear()
        self._loaded = False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary"""
        return self._config.copy()
    
    def has(self, key: str) -> bool:
        """Check if a configuration key exists"""
        return self.get(key) is not None
    
    def get_section(self, section: str) -> 'Config':
        """Get a configuration section as a new Config object"""
        section_config = self.get(section, {})
        new_config = Config(self._app_config)
        new_config._config = section_config
        new_config._loaded = True
        return new_config
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        self._config.clear()
        self._sources.clear()
        self._loaded = False
    
    def __repr__(self) -> str:
        return f"Config(sources={self._sources})"
