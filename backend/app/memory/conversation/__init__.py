# conversation/__init__.py
"""
Conversation Memory

Maintains conversational context for AI agents.

Responsibilities:
- Conversation history
- Context windows
- Message retrieval
- Conversation summaries
- Token budgeting
- Session continuity
"""

from .manager import ConversationMemoryManager
from .models import (
    Conversation,
    ConversationMessage,
    ConversationRole,
    ConversationSummary,
)

__all__ = [
    "ConversationMemoryManager",
    "Conversation",
    "ConversationMessage",
    "ConversationRole",
    "ConversationSummary",
]