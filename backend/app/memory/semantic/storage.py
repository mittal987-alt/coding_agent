from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter

from .models import (
    KnowledgeCategory,
    SemanticMemory,
)


class BaseSemanticStorage(ABC):
    """
    Abstract storage backend for semantic memory.
    """

    @abstractmethod
    async def create(
        self,
        knowledge: SemanticMemory,
    ) -> None:
        ...

    @abstractmethod
    async def update(
        self,
        knowledge: SemanticMemory,
    ) -> None:
        ...

    @abstractmethod
    async def delete(
        self,
        knowledge_id: str,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        knowledge_id: str,
    ) -> SemanticMemory | None:
        ...

    @abstractmethod
    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SemanticMemory]:
        ...