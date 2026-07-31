# analytics.py
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean

from .models import MemoryDocument, MemoryType


@dataclass(slots=True)
class RetrievalMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    average_latency_ms: float = 0.0

    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses

        if total == 0:
            return 0.0

        return self.cache_hits / total


@dataclass(slots=True)
class EmbeddingMetrics:
    generated_embeddings: int = 0

    cached_embeddings: int = 0

    failed_embeddings: int = 0

    average_generation_time_ms: float = 0.0


@dataclass(slots=True)
class AgentMetrics:
    queries: int = 0

    retrieved_memories: int = 0

    average_score: float = 0.0


class MemoryAnalytics:
    """
    Analytics and monitoring for the memory subsystem.
    """

    def __init__(self):

        self.retrieval = RetrievalMetrics()

        self.embeddings = EmbeddingMetrics()

        self.agent_metrics: dict[
            str,
            AgentMetrics,
        ] = defaultdict(AgentMetrics)

        self._latencies: list[float] = []

    def record_retrieval(
        self,
        latency_ms: float,
        *,
        success: bool = True,
        cache_hit: bool = False,
    ) -> None:

        self.retrieval.total_requests += 1

        if success:

            self.retrieval.successful_requests += 1

        else:

            self.retrieval.failed_requests += 1

        if cache_hit:

            self.retrieval.cache_hits += 1

        else:

            self.retrieval.cache_misses += 1

        self._latencies.append(latency_ms)

        self.retrieval.average_latency_ms = mean(
            self._latencies
        )

    def record_embedding(
        self,
        generation_time_ms: float,
        *,
        cached: bool = False,
        success: bool = True,
    ) -> None:

        if cached:

            self.embeddings.cached_embeddings += 1

            return

        if success:

            self.embeddings.generated_embeddings += 1

        else:

            self.embeddings.failed_embeddings += 1

        current = self.embeddings.average_generation_time_ms

        total = self.embeddings.generated_embeddings

        if total == 1:

            self.embeddings.average_generation_time_ms = (
                generation_time_ms
            )

        elif total > 1:

            self.embeddings.average_generation_time_ms = (
                current * (total - 1)
                + generation_time_ms
            ) / total

    def record_agent_usage(
        self,
        agent: str,
        retrieved: int,
        average_score: float,
    ) -> None:

        metrics = self.agent_metrics[agent]

        metrics.queries += 1

        metrics.retrieved_memories += retrieved

        metrics.average_score = (
            metrics.average_score
            + average_score
        ) / 2

    def memory_distribution(
        self,
        documents: list[MemoryDocument],
    ) -> dict[str, int]:

        counts = Counter(
            doc.memory_type.value
            for doc in documents
        )

        return dict(counts)

    def storage_usage(
        self,
        documents: list[MemoryDocument],
    ) -> dict:

        total_bytes = sum(

            len(doc.content.encode())

            for doc in documents

        )

        return {

            "documents": len(documents),

            "storage_bytes": total_bytes,

            "storage_mb": round(
                total_bytes / 1024 / 1024,
                2,
            ),

        }

    def health_report(
        self,
        documents: list[MemoryDocument],
    ) -> dict:

        return {

            "generated_at": datetime.utcnow(),

            "retrieval": self.retrieval,

            "embeddings": self.embeddings,

            "distribution": self.memory_distribution(
                documents
            ),

            "storage": self.storage_usage(
                documents
            ),

            "agents": self.agent_metrics,

        }