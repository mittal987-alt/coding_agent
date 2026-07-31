# learning/__init__.py
"""
Learning Memory

Stores knowledge extracted from experience to continuously
improve AI behavior.

Responsibilities:
- Learn from successful executions
- Learn from failures
- User feedback
- Tool performance analysis
- Planning improvements
- Bug fix patterns
- Coding preferences
- Best practices
- Performance optimization
"""

from .manager import LearningMemoryManager
from .models import (
    LearningMemory,
    LearningCategory,
    LearningSource,
    LearningOutcome,
    LearningFeedback,
)

__all__ = [
    "LearningMemoryManager",
    "LearningMemory",
    "LearningCategory",
    "LearningSource",
    "LearningOutcome",
    "LearningFeedback",
]