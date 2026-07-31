from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from .embeddings import EmbeddingService
from .exceptions import (
    MemoryAlreadyExistsError,
    MemoryNotFoundError,
)
from .models import (
    MemoryDocument,
    MemoryQuery,
    MemoryResult,
)
from .retrieval import MemoryRetriever

logger = logging.getLogger(__name__)


class BaseMemoryStore(ABC):
    """
    Abstract persistent memory storage.
    """

    @abstractmethod
    async def create(
        self,
        document: MemoryDocument,
    ) -> None:
        ...

    @abstractmethod
    async def update(
        self,
        document: MemoryDocument,
    ) -> None:
        ...

    @abstractmethod
    async def delete(
        self,
        memory_id: str,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        memory_id: str,
    ) -> MemoryDocument | None:
        ...

    @abstractmethod
    async def exists(
        self,
        memory_id: str,
    ) -> bool:
        ...


class BaseVectorStore(ABC):
    """
    Abstract vector database.
    """

    @abstractmethod
    async def upsert(
        self,
        document: MemoryDocument,
        embedding: list[float],
    ) -> None:
        ...

    @abstractmethod
    async def delete(
        self,
        memory_id: str,
    ) -> None:
        ...


class MemoryManager:
    """
    Main entry point for the memory subsystem.
    """

    def __init__(
        self,
        store: BaseMemoryStore,
        vector_store: BaseVectorStore,
        embeddings: EmbeddingService,
        retriever: MemoryRetriever,
    ) -> None:

        self.store = store

        self.vector_store = vector_store

        self.embeddings = embeddings

        self.retriever = retriever

    async def create(
        self,
        document: MemoryDocument,
    ) -> MemoryDocument:

        if await self.store.exists(document.id):

            raise MemoryAlreadyExistsError(
                document.id
            )

        embedding = await self.embeddings.embed(
            document.content
        )

        await self.store.create(document)

        await self.vector_store.upsert(
            document,
            embedding,
        )

        logger.info(
            "Memory created %s",
            document.id,
        )

        return document

    async def update(
        self,
        document: MemoryDocument,
    ) -> MemoryDocument:

        if not await self.store.exists(
            document.id
        ):

            raise MemoryNotFoundError(
                document.id
            )

        embedding = await self.embeddings.embed(
            document.content
        )

        await self.store.update(document)

        await self.vector_store.upsert(
            document,
            embedding,
        )

        return document

    async def delete(
        self,
        memory_id: str,
    ) -> None:

        if not await self.store.exists(
            memory_id
        ):

            raise MemoryNotFoundError(
                memory_id
            )

        await self.store.delete(memory_id)

        await self.vector_store.delete(
            memory_id
        )

    async def get(
        self,
        memory_id: str,
    ) -> MemoryDocument:

        memory = await self.store.get(
            memory_id
        )

        if memory is None:

            raise MemoryNotFoundError(
                memory_id
            )

        return memory

    async def search(
        self,
        query: MemoryQuery,
    ) -> list[MemoryResult]:

        return await self.retriever.search(
            query
        )

    async def remember(
        self,
        title: str,
        content: str,
        memory_type,
        **kwargs,
    ) -> MemoryDocument:

        document = MemoryDocument(
            title=title,
            content=content,
            memory_type=memory_type,
            **kwargs,
        )

        return await self.create(
            document
        )

    async def recall(
        self,
        query: str,
        limit: int = 5,
    ) -> list[MemoryResult]:

        return await self.search(

            MemoryQuery(

                query=query,

                limit=limit,

            )

        )