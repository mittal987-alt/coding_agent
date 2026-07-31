# project/__init__.py
"""
Project Memory

Stores long-term project knowledge that persists across
coding sessions.

Responsibilities:
- Project metadata
- Architecture
- Tech stack
- Folder structure
- Coding conventions
- APIs
- Database schema
- Dependencies
- Design decisions
- Project-specific documentation
"""

from .manager import ProjectMemoryManager
from .models import (
    ProjectMemory,
    ProjectArchitecture,
    ProjectDependency,
    ProjectFile,
    ProjectDecision,
    ProjectConvention,
)

__all__ = [
    "ProjectMemoryManager",
    "ProjectMemory",
    "ProjectArchitecture",
    "ProjectDependency",
    "ProjectFile",
    "ProjectDecision",
    "ProjectConvention",
]