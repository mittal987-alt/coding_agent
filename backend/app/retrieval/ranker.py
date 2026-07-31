"""
Hybrid Ranker

Ranks retrieval results using multiple signals.
"""

from __future__ import annotations

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import RetrievalResult


class HybridRanker:

    """
    Computes the final ranking score.

    Final Score =

        Semantic
      + Symbol
      + Graph
      + Multi-Source
      + Structure
    """

    def __init__(
        self,
        repository: RepositoryIndex,
    ):

        self.repository = repository

    def rank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        for result in results:

            score = self.compute_score(
                query=query,
                result=result,
            )

            result.metadata["final_score"] = score

        results.sort(

            key=lambda r: r.metadata["final_score"],

            reverse=True,

        )

        return results

    def compute_score(
        self,
        query: str,
        result: RetrievalResult,
    ) -> float:

        score = 0.0

        score += self.semantic_score(result)

        score += self.symbol_score(query, result)

        score += self.graph_score(result)

        score += self.multi_source_score(result)

        score += self.structure_score(result)

        return score

    def semantic_score(
        self,
        result: RetrievalResult,
    ) -> float:

        return result.score

    def symbol_score(
        self,
        query: str,
        result: RetrievalResult,
    ) -> float:

        symbol = result.chunk.symbol

        if symbol is None:
            return 0.0

        query = query.lower()

        symbol = symbol.lower()

        if symbol in query:
            return 0.40

        return 0.0

    def graph_score(
        self,
        result: RetrievalResult,
    ) -> float:

        symbol = result.chunk.symbol

        if symbol is None:
            return 0.0

        graph = self.repository.graph

        degree = graph.degree(symbol)

        return min(
            degree * 0.02,
            0.25,
        )

    def multi_source_score(
        self,
        result: RetrievalResult,
    ) -> float:

        count = result.metadata.get(
            "num_sources",
            1,
        )

        return count * 0.10

    def structure_score(
        self,
        result: RetrievalResult,
    ) -> float:

        kind = result.chunk.kind

        if kind == "class":
            return 0.15

        if kind == "method":
            return 0.10

        if kind == "function":
            return 0.08

        return 0.0