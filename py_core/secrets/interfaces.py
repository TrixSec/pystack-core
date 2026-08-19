"""
Secrets interfaces - Base interfaces for secrets module
"""

from typing import Optional
from enum import Enum


class SecretProvider(Enum):
    """Secret providers"""
    ENVIRONMENT = "environment"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_VAULT = "azure_vault"
    GOOGLE_SECRET_MANAGER = "google_secret_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    FILE = "file"
