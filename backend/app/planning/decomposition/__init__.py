# __init__.py
"""
Task Decomposition Engine.

Converts high-level user goals into executable task graphs.

Responsibilities:
- Intent parsing
- Task decomposition
- Dependency graph generation
- Validation
- Optimization
- Complexity estimation
"""

from .engine import TaskDecompositionEngine
from .models import (
    Goal,
    TaskNode,
    TaskGraph,
    TaskStatus,
    TaskPriority,
)

__all__ = [
    "TaskDecompositionEngine",
    "Goal",
    "TaskNode",
    "TaskGraph",
    "TaskStatus",
    "TaskPriority",
]