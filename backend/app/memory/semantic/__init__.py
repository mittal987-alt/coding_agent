# semantic/__init__.py
"""
Semantic Memory

Stores long-term factual knowledge learned by the AI.

Examples:
- API documentation
- Architecture decisions
- Coding patterns
- Best practices
- Framework knowledge
- Design principles
- Extracted lessons from episodic memory
"""

from .manager import SemanticMemoryManager
from .models import (
    KnowledgeCategory,
    KnowledgeSource,
    SemanticMemory,
)

__all__ = [
    "SemanticMemoryManager",
    "SemanticMemory",
    "KnowledgeCategory",
    "KnowledgeSource",
]