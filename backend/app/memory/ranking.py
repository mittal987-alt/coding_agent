# ranking.py
from __future__ import annotations

import math
from dataclasses import dataclass

from .models import MemoryDocument, MemoryResult


@dataclass(slots=True)
class RankingWeights:
    """
    Weights for hybrid memory ranking.
    """

    vector: float = 0.40
    keyword: float = 0.20
    semantic: float = 0.15
    importance: float = 0.10
    recency: float = 0.10
    access: float = 0.05


class HybridMemoryRanker:
    """
    Hybrid ranking engine.

    Combines:
    - Vector similarity
    - Keyword score
    - Semantic score
    - Importance
    - Recency
    - Access frequency
    """

    def __init__(
        self,
        weights: RankingWeights | None = None,
    ) -> None:

        self.weights = weights or RankingWeights()

    def rank(
        self,
        results: list[MemoryResult],
    ) -> list[MemoryResult]:

        for result in results:

            result.score = self.compute_score(result)

        return sorted(
            results,
            key=lambda r: r.score,
            reverse=True,
        )

    def compute_score(
        self,
        result: MemoryResult,
    ) -> float:

        doc = result.document

        importance = max(
            0.0,
            min(doc.importance, 1.0),
        )

        access = self._access_score(
            doc.access_count
        )

        recency = self._recency_score(doc)

        score = (

            result.vector_score
            * self.weights.vector

            + result.keyword_score
            * self.weights.keyword

            + result.semantic_score
            * self.weights.semantic

            + importance
            * self.weights.importance

            + recency
            * self.weights.recency

            + access
            * self.weights.access

        )

        return round(score, 5)

    @staticmethod
    def _access_score(
        access_count: int,
    ) -> float:
        """
        Logarithmic scaling.
        """

        return min(
            1.0,
            math.log(access_count + 1, 10),
        )

    @staticmethod
    def _recency_score(
        document: MemoryDocument,
    ) -> float:
        """
        Simple recency scoring.
        """

        if document.last_accessed_at is None:
            return 0.2

        age_days = (
            (
                document.updated_at
                - document.last_accessed_at
            ).days
        )

        if age_days <= 1:
            return 1.0

        if age_days <= 7:
            return 0.9

        if age_days <= 30:
            return 0.7

        if age_days <= 90:
            return 0.5

        return 0.2