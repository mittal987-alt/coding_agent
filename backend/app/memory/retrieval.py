

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod

from .cache import MemoryCache
from .models import (
    MemoryDocument,
    MemoryQuery,
    MemoryResult,
)
from .ranking import HybridMemoryRanker

logger = logging.getLogger(__name__)


class BaseVectorRetriever(ABC):
    """
    Interface implemented by FAISS,
    Qdrant, Milvus, Pinecone, etc.
    """

    @abstractmethod
    async def search(
        self,
        query: MemoryQuery,
    ) -> list[MemoryResult]:
        ...


class BaseKeywordRetriever(ABC):
    """
    Interface implemented by BM25,
    PostgreSQL Full Text Search, Elasticsearch, etc.
    """

    @abstractmethod
    async def search(
        self,
        query: MemoryQuery,
    ) -> list[MemoryResult]:
        ...


class RetrievalStatistics:
    def __init__(self) -> None:

        self.requests = 0
        self.cache_hits = 0
        self.vector_requests = 0
        self.keyword_requests = 0


class MemoryRetriever:
    """
    Production hybrid retrieval engine.
    """

    def __init__(
        self,
        vector_retriever: BaseVectorRetriever,
        keyword_retriever: BaseKeywordRetriever,
        ranker: HybridMemoryRanker,
        cache: MemoryCache | None = None,
    ) -> None:

        self.vector = vector_retriever

        self.keyword = keyword_retriever

        self.ranker = ranker

        self.cache = cache or MemoryCache()

        self.stats = RetrievalStatistics()

    async def search(
        self,
        query: MemoryQuery,
    ) -> list[MemoryResult]:

        self.stats.requests += 1

        cache_key = self._cache_key(query)

        cached = await self.cache.get(cache_key)

        if cached is not None:

            self.stats.cache_hits += 1

            return cached

        vector_results = await self.vector.search(
            query
        )

        self.stats.vector_requests += 1

        keyword_results = await self.keyword.search(
            query
        )

        self.stats.keyword_requests += 1

        merged = self._merge(
            vector_results,
            keyword_results,
        )

        ranked = self.ranker.rank(merged)

        ranked = ranked[: query.limit]

        await self.cache.set(
            cache_key,
            ranked,
        )

        return ranked

    def _merge(
        self,
        vector_results: list[MemoryResult],
        keyword_results: list[MemoryResult],
    ) -> list[MemoryResult]:
        """
        Merge duplicate documents while
        preserving individual scores.
        """

        merged: dict[str, MemoryResult] = {}

        for result in vector_results:

            merged[result.document.id] = result

        for result in keyword_results:

            if result.document.id in merged:

                existing = merged[result.document.id]

                existing.keyword_score = max(
                    existing.keyword_score,
                    result.keyword_score,
                )

                existing.semantic_score = max(
                    existing.semantic_score,
                    result.semantic_score,
                )

                existing.vector_score = max(
                    existing.vector_score,
                    result.vector_score,
                )

            else:

                merged[result.document.id] = result

        return list(merged.values())

    @staticmethod
    def _cache_key(
        query: MemoryQuery,
    ) -> str:

        key = (
            query.query
            + "|"
            + ",".join(
                sorted(
                    t.value
                    for t in query.memory_types
                )
            )
            + "|"
            + str(query.limit)
            + "|"
            + str(query.project_id)
            + "|"
            + str(query.tags)
        )

        return hashlib.sha256(
            key.encode()
        ).hexdigest()