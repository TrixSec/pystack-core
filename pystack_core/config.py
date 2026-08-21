"""
Configuration Management - Multi-source configuration with validation
"""

import os
from typing import Optional, Dict, Any, Union
from pathlib import Path
import json
import yaml
try:
    import tomli
    HAS_TOMLI = True
except ImportError:
    HAS_TOMLI = False

from pydantic import BaseModel, ValidationError


class Config:
    """Configuration management with multiple sources"""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._config_path = config_path
        self._env_prefix = ""
        self._schema: Optional[type] = None
    
    def load_from_env(self, prefix: str = ""):
        """Load configuration from environment variables"""
        self._env_prefix = prefix
        for key, value in os.environ.items():
            if prefix and key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._config[config_key] = self._convert_value(value)
    
    def load_from_yaml(self, path: str):
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                self._config.update(yaml_config)
    
    def load_from_json(self, path: str):
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            json_config = json.load(f)
            self._config.update(json_config)
    
    def load_from_toml(self, path: str):
        """Load configuration from TOML file"""
        if HAS_TOMLI:
            with open(path, 'rb') as f:
                toml_config = tomli.load(f)
                self._config.update(toml_config)
        else:
            raise ImportError("tomli is required for TOML support")
    
    def load_from_dict(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary"""
        self._config.update(config_dict)
    
    def set_schema(self, schema: type):
        """Set Pydantic schema for validation"""
        self._schema = schema
    
    def validate(self) -> Optional[BaseModel]:
        """Validate configuration against schema"""
        if self._schema:
            try:
                return self._schema(**self._config)
            except ValidationError as e:
                raise ConfigError(f"Configuration validation failed: {e}")
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert string value to appropriate type"""
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value


class ConfigError(Exception):
    """Configuration error"""
    pass
