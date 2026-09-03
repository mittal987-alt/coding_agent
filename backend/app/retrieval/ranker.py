"""
Hybrid Ranker — BM25 + Reciprocal Rank Fusion (RRF)

Computes the final retrieval ranking by fusing four signals:

  1. Dense vector cosine similarity (from Qdrant/FAISS)
  2. BM25 lexical keyword match (rank_bm25 library)
  3. AST symbol graph degree centrality
  4. Structural bonus (class > method > function > chunk)

RRF formula: score(d) = Σ 1/(k + rank_i(d))  where k=60

The BM25 index is built lazily on the first call to rank(),
using the corpus of all result content chunks.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import RetrievalResult

logger = logging.getLogger(__name__)

# RRF smoothing constant (standard value from literature)
RRF_K: int = 60


class HybridRanker:
    """
    Fuses multiple retrieval signals into a single ranked list using RRF.

    Usage::

        ranker = HybridRanker(repository)
        ranked_results = ranker.rank(query, merged_results)
    """

    def __init__(self, repository: RepositoryIndex) -> None:
        self.repository = repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """
        Rank a merged list of retrieval results using BM25 + RRF fusion.

        Args:
            query:   The developer's original search query.
            results: Merged list of RetrievalResult objects from all sources.

        Returns:
            Results sorted by descending RRF-fused score.
        """
        if not results:
            return results

        # Step 1: Build BM25 lexical rankings over the result corpus
        bm25_ranks = self._bm25_rank(query, results)

        # Step 2: Extract per-source semantic ranks (from result order)
        semantic_ranks = {r.chunk.id: idx + 1 for idx, r in enumerate(results)}

        # Step 3: Compute fused RRF score for each result
        for result in results:
            chunk_id = result.chunk.id
            rrf_score = 0.0

            # Dense vector rank (from result list order by .score)
            sem_rank = semantic_ranks.get(chunk_id, len(results))
            rrf_score += 1.0 / (RRF_K + sem_rank)

            # BM25 lexical rank
            bm25_rank = bm25_ranks.get(chunk_id, len(results))
            rrf_score += 1.0 / (RRF_K + bm25_rank)

            # Structural bonus (class > method > function > chunk)
            rrf_score += self._structure_bonus(result)

            # AST graph degree centrality bonus
            rrf_score += self._graph_bonus(result)

            # Multi-source confirmation bonus (seen in more sources = higher confidence)
            rrf_score += self._multi_source_bonus(result)

            result.metadata["rrf_score"] = round(rrf_score, 6)
            result.metadata["bm25_rank"] = bm25_rank
            result.metadata["semantic_rank"] = sem_rank

        # Step 4: Sort by final RRF score descending
        results.sort(key=lambda r: r.metadata["rrf_score"], reverse=True)

        return results

    # ------------------------------------------------------------------
    # BM25 Lexical Ranking
    # ------------------------------------------------------------------

    def _bm25_rank(
        self,
        query: str,
        results: list[RetrievalResult],
    ) -> dict[str, int]:
        """
        Build a BM25 index over the result corpus and return per-chunk ranks.

        Args:
            query:   Raw query string.
            results: Result list whose content forms the BM25 corpus.

        Returns:
            Dict mapping chunk_id → 1-indexed BM25 rank.
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.warning(
                "rank_bm25 not installed — BM25 ranking disabled. "
                "Run: pip install rank-bm25"
            )
            return {}

        # Tokenise corpus (simple whitespace split; improve with nltk if needed)
        corpus: list[list[str]] = []
        chunk_ids: list[str] = []

        for result in results:
            tokens = (result.chunk.content or "").lower().split()
            corpus.append(tokens)
            chunk_ids.append(result.chunk.id)

        if not corpus:
            return {}

        bm25 = BM25Okapi(corpus)
        query_tokens = query.lower().split()
        scores = bm25.get_scores(query_tokens)

        # Rank chunks by descending BM25 score (ties share the same rank)
        indexed = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True,
        )
        rank_map: dict[str, int] = {}
        for rank, (corpus_idx, _) in enumerate(indexed, start=1):
            cid = chunk_ids[corpus_idx]
            if cid not in rank_map:
                rank_map[cid] = rank

        return rank_map

    # ------------------------------------------------------------------
    # Bonus score helpers
    # ------------------------------------------------------------------

    def _structure_bonus(self, result: RetrievalResult) -> float:
        """Structural bonus: class definitions are most valuable."""
        bonuses = {"class": 0.015, "method": 0.010, "function": 0.008}
        return bonuses.get(result.chunk.kind or "", 0.0)

    def _graph_bonus(self, result: RetrievalResult) -> float:
        """
        AST import-graph degree bonus: symbols with more callers/callees
        are more likely to be relevant architectural anchors.
        """
        symbol = result.chunk.symbol
        if not symbol:
            return 0.0
        try:
            graph = self.repository.graph
            degree = graph.degree(symbol)
            # Cap at 0.025 to prevent graph-heavy symbols from dominating
            return min(degree * 0.002, 0.025)
        except Exception:
            return 0.0

    def _multi_source_bonus(self, result: RetrievalResult) -> float:
        """Bonus for chunks confirmed by multiple retrieval modalities."""
        num_sources = result.metadata.get("num_sources", 1)
        return (num_sources - 1) * 0.010