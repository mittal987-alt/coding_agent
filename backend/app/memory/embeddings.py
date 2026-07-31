# embeddings.py
from __future__ import annotations

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod

from app.memory.cache import MemoryCache
from app.memory.exceptions import (
    EmbeddingDimensionError,
    EmbeddingProviderError,
)

logger = logging.getLogger(__name__)


class BaseEmbeddingProvider(ABC):
    """
    Abstract embedding provider.
    """

    name: str
    dimension: int

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        ...

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return await asyncio.gather(
            *(self.embed(t) for t in texts)
        )


class EmbeddingService:
    """
    Production embedding service.

    Features

    - Provider abstraction
    - Cache
    - Batch embeddings
    - Validation
    - Retry
    """

    def __init__(
        self,
        provider: BaseEmbeddingProvider,
        cache: MemoryCache | None = None,
        retries: int = 2,
    ):

        self.provider = provider

        self.cache = cache or MemoryCache()

        self.retries = retries

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        cache_key = self._cache_key(text)

        cached = await self.cache.get(cache_key)

        if cached is not None:

            return cached

        vector = await self._retry_embed(text)

        self._validate(vector)

        await self.cache.set(
            cache_key,
            vector,
        )

        return vector

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        vectors = []

        for text in texts:

            vectors.append(
                await self.embed(text)
            )

        return vectors

    async def _retry_embed(
        self,
        text: str,
    ) -> list[float]:

        last_exception = None

        for _ in range(self.retries + 1):

            try:

                return await self.provider.embed(text)

            except Exception as exc:

                last_exception = exc

                logger.exception(exc)

        raise EmbeddingProviderError(
            f"Embedding provider '{self.provider.name}' failed."
        ) from last_exception

    def _validate(
        self,
        vector: list[float],
    ) -> None:

        if len(vector) != self.provider.dimension:

            raise EmbeddingDimensionError(
                self.provider.dimension,
                len(vector),
            )

    @staticmethod
    def _cache_key(
        text: str,
    ) -> str:

        return hashlib.sha256(
            text.encode()
        ).hexdigest()