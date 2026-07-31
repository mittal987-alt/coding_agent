# vector/retrieval.py
from __future__ import annotations

import logging
from typing import Any

from app.memory.embeddings import EmbeddingService

from .faiss_store import BaseVectorStore

logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    High-level vector retrieval pipeline.

    Responsible for:
    - embedding generation
    - similarity search
    - metadata filtering
    - reranking
    """

    def __init__(
        self,
        *,
        embedding_service: EmbeddingService,
        vector_store: BaseVectorStore,
    ) -> None:

        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 10,
        minimum_score: float = 0.75,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict]:
        """
        Retrieve the most relevant vectors.
        """

        embedding = await self.embedding_service.embed_text(
            query
        )

        results = await self.vector_store.search(
            embedding,
            top_k=top_k * 2,
        )

        results = self._apply_filters(
            results,
            metadata_filter,
        )

        results = self._threshold(
            results,
            minimum_score,
        )

        results = self._rerank(results)

        return results[:top_k]

    def _apply_filters(
        self,
        results: list[dict],
        metadata_filter: dict[str, Any] | None,
    ) -> list[dict]:

        if not metadata_filter:

            return results

        filtered = []

        for result in results:

            metadata = result.get(
                "metadata",
                {},
            )

            matches = True

            for key, value in metadata_filter.items():

                if metadata.get(key) != value:

                    matches = False

                    break

            if matches:

                filtered.append(result)

        return filtered

    def _threshold(
        self,
        results: list[dict],
        minimum_score: float,
    ) -> list[dict]:

        return [

            result

            for result in results

            if result["score"] >= minimum_score

        ]

    def _rerank(
        self,
        results: list[dict],
    ) -> list[dict]:
        """
        Placeholder reranker.

        Production:
            Cross-Encoder
            ColBERT
            Cohere Rerank
            BGE Reranker
        """

        return sorted(
            results,
            key=lambda x: x["score"],
            reverse=True,
        )

    async def retrieve_context(
        self,
        query: str,
        *,
        top_k: int = 8,
    ) -> str:
        """
        Build context for LLM prompts.
        """

        results = await self.retrieve(
            query,
            top_k=top_k,
        )

        sections = []

        for item in results:

            metadata = item.get(
                "metadata",
                {},
            )

            title = metadata.get(
                "title",
                "Untitled",
            )

            content = metadata.get(
                "content",
                "",
            )

            sections.append(
                f"""
### {title}

Similarity: {item['score']:.3f}

{content}
"""
            )

        return "\n".join(sections)

    async def retrieve_by_project(
        self,
        query: str,
        project_id: str,
    ) -> list[dict]:

        return await self.retrieve(
            query,
            metadata_filter={
                "project_id": project_id,
            },
        )

    async def retrieve_by_category(
        self,
        query: str,
        category: str,
    ) -> list[dict]:

        return await self.retrieve(
            query,
            metadata_filter={
                "category": category,
            },
        )