"""
Secrets module - Unified secrets management with multiple provider support
"""

from py_core.secrets.secrets import Secrets
from py_core.secrets.interfaces import SecretProvider

__all__ = [
    "Secrets",
    "SecretProvider",
]
