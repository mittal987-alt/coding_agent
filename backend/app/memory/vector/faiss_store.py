# vector/faiss_store.py
from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import faiss
import numpy as np


class BaseVectorStore(ABC):
    """
    Abstract vector store interface.
    """

    @abstractmethod
    async def add(
        self,
        document_id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def search(
        self,
        embedding: list[float],
        *,
        top_k: int = 10,
    ) -> list[dict]:
        ...

    @abstractmethod
    async def delete(
        self,
        document_id: str,
    ) -> None:
        ...

    @abstractmethod
    async def save(self) -> None:
        ...

    @abstractmethod
    async def load(self) -> None:
        ...