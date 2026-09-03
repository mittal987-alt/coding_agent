"""
Reciprocal Rank Fusion (RRF) Hybrid Search Engine.
Combines Lexical (BM25 keyword), Dense Vector (Qdrant/FAISS), and AST Symbol Graph retrieval.
"""

from __future__ import annotations

import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SearchCandidate(BaseModel):
    id: str
    file_path: str
    content: str
    symbol: Optional[str] = None
    dense_rank: Optional[int] = None
    lexical_rank: Optional[int] = None
    ast_rank: Optional[int] = None
    rrf_score: float = 0.0


class ReciprocalRankFusionEngine:
    """
    Implements Reciprocal Rank Fusion (RRF) algorithm:
    RRF_Score(d) = sum( 1 / (k + rank_i(d)) ) across all search modalities.
    """

    def __init__(self, k_constant: int = 60):
        self.k_constant = k_constant

    def compute_rrf(
        self,
        dense_results: List[Dict[str, Any]],
        lexical_results: List[Dict[str, Any]],
        ast_results: List[Dict[str, Any]]
    ) -> List[SearchCandidate]:
        candidates: Dict[str, SearchCandidate] = {}

        # 1. Process Dense Vector Results
        for rank, item in enumerate(dense_results, start=1):
            cid = item["id"]
            if cid not in candidates:
                candidates[cid] = SearchCandidate(
                    id=cid,
                    file_path=item.get("file_path", ""),
                    content=item.get("content", ""),
                    symbol=item.get("symbol")
                )
            candidates[cid].dense_rank = rank
            candidates[cid].rrf_score += 1.0 / (self.k_constant + rank)

        # 2. Process Lexical BM25 Results
        for rank, item in enumerate(lexical_results, start=1):
            cid = item["id"]
            if cid not in candidates:
                candidates[cid] = SearchCandidate(
                    id=cid,
                    file_path=item.get("file_path", ""),
                    content=item.get("content", ""),
                    symbol=item.get("symbol")
                )
            candidates[cid].lexical_rank = rank
            candidates[cid].rrf_score += 1.0 / (self.k_constant + rank)

        # 3. Process AST Symbol Graph Results
        for rank, item in enumerate(ast_results, start=1):
            cid = item["id"]
            if cid not in candidates:
                candidates[cid] = SearchCandidate(
                    id=cid,
                    file_path=item.get("file_path", ""),
                    content=item.get("content", ""),
                    symbol=item.get("symbol")
                )
            candidates[cid].ast_rank = rank
            candidates[cid].rrf_score += 1.0 / (self.k_constant + rank)

        # Sort candidates by final RRF score descending
        sorted_candidates = sorted(
            candidates.values(),
            key=lambda c: c.rrf_score,
            reverse=True
        )
        return sorted_candidates
