# LLM Module

"""
LLM Orchestration Layer

This package provides a unified interface for interacting with
multiple Large Language Model providers.

Responsibilities:
- Provider abstraction
- Model routing
- Prompt management
- Streaming responses
- Tool/function calling
- Structured outputs
- Response caching
- Retry & fallback handling
- Token management
- Middleware integration
"""

from .manager import LLMManager
from .provider import (
    BaseLLMProvider,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ToolCall,
)
from .registry import LLMRegistry
from .router import LLMRouter

__all__ = [
    "LLMManager",
    "BaseLLMProvider",
    "ChatRequest",
    "ChatResponse",
    "ChatMessage",
    "ToolCall",
    "LLMRegistry",
    "LLMRouter",
]