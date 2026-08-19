"""
AI interfaces - Base interfaces for AI module
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class AIProvider(Enum):
    """AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"


@dataclass
class ChatMessage:
    """Chat message"""
    role: str
    content: str


@dataclass
class ChatCompletionRequest:
    """Chat completion request"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
