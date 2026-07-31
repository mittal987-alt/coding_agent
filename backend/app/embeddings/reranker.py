"""
Hybrid Reranker

Combines semantic similarity with repository knowledge.
"""

from __future__ import annotations

from typing import List

from app.embeddings.chunk_models import CodeChunk
from app.indexers.repository_index import RepositoryIndex


class HybridReranker:
    """
    Reranks retrieved chunks using multiple signals.

    Score =
        Semantic +
        Symbol +
        Graph +
        File +
        Neighbor
    """

    def __init__(
        self,
        repository: RepositoryIndex,
    ) -> None:

        self.repository = repository

    def rerank(
        self,
        query: str,
        chunks: List[CodeChunk],
        limit: int = 15,
    ) -> List[CodeChunk]:

        scored = []

        for chunk in chunks:

            score = self._score(
                query=query,
                chunk=chunk,
            )

            chunk.metadata["rerank_score"] = score

            scored.append(chunk)

        scored.sort(
            key=lambda c: c.metadata["rerank_score"],
            reverse=True,
        )

        return scored[:limit]

    def _score(
        self,
        query: str,
        chunk: CodeChunk,
    ) -> float:

        score = 0.0

        score += self._semantic_score(chunk)

        score += self._symbol_score(
            query,
            chunk,
        )

        score += self._graph_score(chunk)

        score += self._file_score(chunk)

        score += self._neighbor_score(chunk)

        return score

    def _semantic_score(
        self,
        chunk: CodeChunk,
    ) -> float:

        return float(
            chunk.metadata.get(
                "score",
                0.0,
            )
        )

    def _symbol_score(
        self,
        query: str,
        chunk: CodeChunk,
    ) -> float:

        if chunk.symbol is None:
            return 0.0

        query = query.lower()

        symbol = chunk.symbol.lower()

        if symbol in query:
            return 0.40

        return 0.0

    def _graph_score(
        self,
        chunk: CodeChunk,
    ) -> float:

        graph = self.repository.graph

        if graph is None:
            return 0.0

        degree = graph.degree(
            chunk.symbol
        )

        return min(
            degree * 0.02,
            0.25,
        )

    def _file_score(
        self,
        chunk: CodeChunk,
    ) -> float:

        file_index = self.repository.files

        if chunk.file not in file_index.files:
            return 0.0

        return 0.05

    def _neighbor_score(
        self,
        chunk: CodeChunk,
    ) -> float:

        if chunk.kind == "class":
            return 0.10

        if chunk.kind == "method":
            return 0.05

        return 0.0