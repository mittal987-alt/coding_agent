# vector/manager.py

from __future__ import annotations

import logging
from typing import Any

from app.memory.embeddings import EmbeddingService

from .faiss_store import BaseVectorStore
from .retrieval import VectorRetriever

logger = logging.getLogger(__name__)


class VectorMemoryManager:
    """
    High-level manager for vector memory.

    Coordinates embedding generation,
    indexing, retrieval, and maintenance.
    """

    def __init__(
        self,
        *,
        embedding_service: EmbeddingService,
        vector_store: BaseVectorStore,
    ) -> None:

        self.embedding_service = embedding_service
        self.vector_store = vector_store

        self.retriever = VectorRetriever(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

    async def index_document(
        self,
        *,
        document_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Generate an embedding and index a document.
        """

        embedding = await self.embedding_service.embed_text(
            content
        )

        await self.vector_store.add(
            document_id=document_id,
            embedding=embedding,
            metadata=metadata,
        )

        logger.info(
            "Indexed document %s",
            document_id,
        )

    async def update_document(
        self,
        *,
        document_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Replace an indexed document.

        FAISS Flat indexes don't support in-place updates,
        so this implementation performs a logical delete
        followed by re-indexing.
        """

        await self.remove_document(document_id)

        await self.index_document(
            document_id=document_id,
            content=content,
            metadata=metadata,
        )

    async def remove_document(
        self,
        document_id: str,
    ) -> None:

        await self.vector_store.delete(
            document_id
        )

    async def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        minimum_score: float = 0.75,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict]:
        """
        Perform semantic search.
        """

        return await self.retriever.retrieve(
            query,
            top_k=top_k,
            minimum_score=minimum_score,
            metadata_filter=metadata_filter,
        )

    async def batch_index(
        self,
        documents: list[dict],
    ) -> None:
        """
        Index multiple documents.
        """

        for document in documents:

            await self.index_document(
                document_id=document["id"],
                content=document["content"],
                metadata=document.get(
                    "metadata",
                    {},
                ),
            )

        logger.info(
            "Indexed %d documents.",
            len(documents),
        )

    async def rebuild_index(
        self,
        documents: list[dict],
    ) -> None:
        """
        Rebuild the vector index from scratch.
        """

        for document in documents:

            await self.index_document(
                document_id=document["id"],
                content=document["content"],
                metadata=document.get(
                    "metadata",
                    {},
                ),
            )

        logger.info(
            "Vector index rebuilt."
        )

    async def save(self) -> None:
        """
        Persist the vector index.
        """

        await self.vector_store.save()

    async def load(self) -> None:
        """
        Load the vector index.
        """

        await self.vector_store.load()

    async def statistics(self) -> dict:
        """
        Basic vector index statistics.
        """

        return {
            "documents": len(
                self.vector_store.document_ids
            ),
            "dimension": self.vector_store.dimension,
        }