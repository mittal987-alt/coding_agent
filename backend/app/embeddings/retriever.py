"""
Semantic Retriever

Performs similarity search using FAISS.
"""

from __future__ import annotations

from typing import List

import numpy as np

from app.embeddings.chunk_models import CodeChunk
from app.embeddings.embedding_engine import EmbeddingEngine
from app.embeddings.faiss_store import FaissStore


class Retriever:

    """
    Semantic Retriever.

    Converts a user query into an embedding,
    searches the FAISS index,
    and returns ranked CodeChunks.
    """

    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        vector_store: FaissStore,
    ) -> None:

        self.embedding_engine = embedding_engine
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[CodeChunk]:
        """
        Retrieve top-k chunks.

        Args:
            query: User question
            top_k: Number of chunks

        Returns:
            Ranked CodeChunks
        """

        query_vector = self.embedding_engine.embed_text(query)

        results = self.vector_store.search(
            query_vector,
            k=top_k,
        )

        chunks = []

        for score, chunk in results:

            chunk.metadata["score"] = float(score)

            chunks.append(chunk)

        return chunks

    def retrieve_by_file(
        self,
        file_path: str,
    ) -> List[CodeChunk]:
        """
        Return every chunk from a file.
        """

        return self.vector_store.file_chunks(
            file_path
        )

    def retrieve_by_symbol(
        self,
        symbol: str,
    ) -> List[CodeChunk]:
        """
        Return chunks belonging to a symbol.
        """

        return self.vector_store.symbol_chunks(
            symbol
        )

    def retrieve_related(
        self,
        query: str,
        file_path: str,
        top_k: int = 5,
    ) -> List[CodeChunk]:
        """
        Restrict retrieval to one file.
        """

        query_vector = self.embedding_engine.embed_text(
            query
        )

        return self.vector_store.search_in_file(
            query_vector=query_vector,
            file=file_path,
            k=top_k,
        )

    def retrieve_workspace(
        self,
        workspace_id: int,
        query: str,
        top_k: int = 10,
    ) -> List[CodeChunk]:

        vector = self.embedding_engine.embed_text(
            query
        )

        return self.vector_store.search_workspace(
            workspace_id,
            vector,
            top_k,
        )