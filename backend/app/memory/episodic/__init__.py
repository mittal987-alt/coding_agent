# episodic/__init__.py

"""
Episodic Memory

Stores experiences of the AI agent.

Examples

- Completed tasks
- Failed executions
- Bug fixes
- Terminal commands
- PR reviews
- Debug sessions
- Tool usage
"""

from .manager import EpisodicMemoryManager
from .models import (
    EpisodicMemory,
    EpisodeType,
)

__all__ = [
    "EpisodicMemoryManager",
    "EpisodicMemory",
    "EpisodeType",
]