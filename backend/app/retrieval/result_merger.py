"""
Hybrid Result Merger

Combines results from multiple retrievers.

Responsibilities:

- Remove duplicates
- Merge scores
- Track retrieval sources
- Normalize scores
"""

from __future__ import annotations

from collections import defaultdict

from app.retrieval.models import RetrievalResult


class ResultMerger:

    """
    Merge retrieval results coming from

    - Vector Retriever
    - Symbol Retriever
    - Graph Retriever
    """

    def merge(
        self,
        *result_sets: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        merged: dict[str, RetrievalResult] = {}

        source_map = defaultdict(set)

        for results in result_sets:

            for result in results:

                chunk_id = result.chunk.id

                if chunk_id not in merged:

                    merged[chunk_id] = result

                else:

                    merged[chunk_id].score += result.score

                source_map[chunk_id].add(
                    result.source.value
                )

        for chunk_id, result in merged.items():

            result.metadata["sources"] = sorted(
                list(source_map[chunk_id])
            )

            result.metadata["num_sources"] = len(
                source_map[chunk_id]
            )

        return list(merged.values())