"""
Application bootstrap package.

This package is responsible for constructing the
entire application and wiring together all major
components such as:

- Configuration
- Dependency Injection
- LLM Providers
- Memory
- Agents
- Tools
- Workspace
- FastAPI
"""

from .application import Application
from .container import ServiceContainer
from .startup import bootstrap_application

__all__ = [
    "Application",
    "ServiceContainer",
    "bootstrap_application",
]