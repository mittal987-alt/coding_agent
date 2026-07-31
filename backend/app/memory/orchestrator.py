# orchestrator.py
from __future__ import annotations

import logging
from collections import defaultdict

from .manager import MemoryManager
from .models import (
    MemoryQuery,
    MemoryResult,
    MemoryType,
)

logger = logging.getLogger(__name__)


class MemoryOrchestrator:
    """
    High-level orchestration layer.

    Responsible for deciding which
    memories should be retrieved
    for the current task.
    """

    DEFAULT_MEMORY_TYPES = [
        MemoryType.PROJECT,
        MemoryType.SEMANTIC,
        MemoryType.EPISODIC,
        MemoryType.DECISION,
    ]

    AGENT_MEMORY_TYPES = {
        "planner": [
            MemoryType.PROJECT,
            MemoryType.DECISION,
            MemoryType.SEMANTIC,
        ],
        "coder": [
            MemoryType.PROJECT,
            MemoryType.SEMANTIC,
            MemoryType.CONVERSATION,
        ],
        "reviewer": [
            MemoryType.PROJECT,
            MemoryType.DECISION,
            MemoryType.EPISODIC,
        ],
        "tester": [
            MemoryType.PROJECT,
            MemoryType.EPISODIC,
        ],
        "repository": [
            MemoryType.PROJECT,
            MemoryType.SEMANTIC,
        ],
    }

    def __init__(
        self,
        memory: MemoryManager,
    ) -> None:

        self.memory = memory

    async def retrieve_context(
        self,
        query: str,
        *,
        agent: str = "planner",
        project_id: str | None = None,
        conversation_id: str | None = None,
        limit: int = 10,
    ) -> list[MemoryResult]:
        """
        Retrieve context for an agent.
        """

        memory_types = self.AGENT_MEMORY_TYPES.get(
            agent,
            self.DEFAULT_MEMORY_TYPES,
        )

        results = await self.memory.search(
            MemoryQuery(
                query=query,
                memory_types=memory_types,
                project_id=project_id,
                conversation_id=conversation_id,
                limit=limit * 3,
            )
        )

        merged = self._deduplicate(results)

        return merged[:limit]

    async def build_prompt_context(
        self,
        query: str,
        *,
        agent: str,
        project_id: str | None = None,
        conversation_id: str | None = None,
        limit: int = 10,
    ) -> str:
        """
        Convert retrieved memories into
        LLM-ready prompt context.
        """

        memories = await self.retrieve_context(
            query,
            agent=agent,
            project_id=project_id,
            conversation_id=conversation_id,
            limit=limit,
        )

        sections = []

        for memory in memories:

            doc = memory.document

            sections.append(
                f"""
### {doc.title}

Type: {doc.memory_type.value}

Summary:
{doc.summary or doc.content}
"""
            )

        return "\n".join(sections)

    async def remember_execution(
        self,
        title: str,
        summary: str,
        metadata: dict,
    ) -> None:
        """
        Store an execution as episodic memory.
        """

        await self.memory.remember(
            title=title,
            content=summary,
            memory_type=MemoryType.EPISODIC,
            metadata=metadata,
        )

    async def remember_decision(
        self,
        title: str,
        decision: str,
        metadata: dict,
    ) -> None:

        await self.memory.remember(
            title=title,
            content=decision,
            memory_type=MemoryType.DECISION,
            metadata=metadata,
        )

    def _deduplicate(
        self,
        results: list[MemoryResult],
    ) -> list[MemoryResult]:

        best: dict[str, MemoryResult] = {}

        for result in results:

            doc = result.document

            existing = best.get(doc.id)

            if existing is None:

                best[doc.id] = result

            elif result.score > existing.score:

                best[doc.id] = result

        return sorted(
            best.values(),
            key=lambda r: r.score,
            reverse=True,
        )

    def summarize_statistics(
        self,
        results: list[MemoryResult],
    ) -> dict:

        counts = defaultdict(int)

        for result in results:

            counts[
                result.document.memory_type.value
            ] += 1

        return {
            "total": len(results),
            "memory_types": dict(counts),
        }