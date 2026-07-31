"""
Graph Retriever

Traverses repository graphs to discover
related code beyond semantic search.

Supports:

- Call Graph
- Dependency Graph
- Knowledge Graph
"""

from __future__ import annotations

from typing import List, Set

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import (
    RetrievalResult,
    RetrievalSource,
)


class GraphRetriever:
    """
    Repository-aware retrieval using graphs.
    """

    def __init__(
        self,
        repository: RepositoryIndex,
    ) -> None:

        self.repository = repository

    def retrieve(
        self,
        symbol: str,
        depth: int = 2,
    ) -> List[RetrievalResult]:

        visited: Set[str] = set()

        results: List[RetrievalResult] = []

        self._dfs(
            symbol=symbol,
            depth=depth,
            visited=visited,
            results=results,
        )

        return results

    def _dfs(
        self,
        symbol: str,
        depth: int,
        visited: Set[str],
        results: List[RetrievalResult],
    ) -> None:

        if depth < 0:
            return

        if symbol in visited:
            return

        visited.add(symbol)

        chunk = self.repository.embeddings.chunk_for_symbol(
            symbol
        )

        if chunk:

            results.append(

                RetrievalResult(

                    chunk=chunk,

                    score=0.8,

                    source=RetrievalSource.GRAPH,

                    metadata={
                        "depth": depth,
                    },

                )

            )

        graph = self.repository.graph

        neighbors = graph.neighbors(symbol)

        for next_symbol in neighbors:

            self._dfs(
                symbol=next_symbol,
                depth=depth - 1,
                visited=visited,
                results=results,
            )

    def callers(
        self,
        symbol: str,
    ) -> List[RetrievalResult]:

        graph = self.repository.graph

        callers = graph.callers(symbol)

        return self._convert(callers)

    def callees(
        self,
        symbol: str,
    ) -> List[RetrievalResult]:

        graph = self.repository.graph

        callees = graph.callees(symbol)

        return self._convert(callees)

    def imports(
        self,
        file: str,
    ) -> List[RetrievalResult]:

        graph = self.repository.graph

        imports = graph.imports(file)

        return self._convert(imports)

    def imported_by(
        self,
        file: str,
    ) -> List[RetrievalResult]:

        graph = self.repository.graph

        files = graph.imported_by(file)

        return self._convert(files)

    def inheritance(
        self,
        class_name: str,
    ) -> List[RetrievalResult]:

        graph = self.repository.graph

        classes = graph.inheritance(class_name)

        return self._convert(classes)

    def _convert(
        self,
        symbols: List[str],
    ) -> List[RetrievalResult]:

        results = []

        for symbol in symbols:

            chunk = self.repository.embeddings.chunk_for_symbol(
                symbol
            )

            if chunk is None:
                continue

            results.append(

                RetrievalResult(

                    chunk=chunk,

                    score=0.75,

                    source=RetrievalSource.GRAPH,

                )

            )

        return results