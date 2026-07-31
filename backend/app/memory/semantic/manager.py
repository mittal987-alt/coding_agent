# semantic/manager.py
from __future__ import annotations

import logging
from datetime import datetime

from app.memory.episodic.models import EpisodicMemory

from .models import (
    KnowledgeCategory,
    KnowledgeSource,
    SemanticMemory,
)
from .storage import BaseSemanticStorage

logger = logging.getLogger(__name__)


class SemanticMemoryManager:
    """
    High-level service responsible for managing
    long-term semantic knowledge.
    """

    def __init__(
        self,
        storage: BaseSemanticStorage,
    ) -> None:
        self.storage = storage

    async def create(
        self,
        knowledge: SemanticMemory,
    ) -> SemanticMemory:

        await self.storage.create(knowledge)

        logger.info(
            "Created semantic knowledge %s",
            knowledge.id,
        )

        return knowledge

    async def update(
        self,
        knowledge: SemanticMemory,
    ) -> SemanticMemory:

        knowledge.updated_at = datetime.utcnow()

        await self.storage.update(
            knowledge
        )

        return knowledge

    async def delete(
        self,
        knowledge_id: str,
    ) -> None:

        await self.storage.delete(
            knowledge_id
        )

    async def get(
        self,
        knowledge_id: str,
    ) -> SemanticMemory | None:

        return await self.storage.get(
            knowledge_id
        )

    async def search(
        self,
        query: str,
    ) -> list[SemanticMemory]:

        return await self.storage.search(
            query
        )

    async def related(
        self,
        knowledge_id: str,
    ) -> list[SemanticMemory]:

        return await self.storage.related(
            knowledge_id
        )

    async def statistics(self) -> dict:

        return await self.storage.statistics()

    async def promote(
        self,
        knowledge: SemanticMemory,
    ) -> SemanticMemory:
        """
        Mark knowledge as verified.
        """

        knowledge.verified = True

        knowledge.importance = min(
            1.0,
            knowledge.importance + 0.2,
        )

        await self.storage.update(
            knowledge
        )

        return knowledge

    async def increase_confidence(
        self,
        knowledge: SemanticMemory,
        amount: float = 0.05,
    ) -> SemanticMemory:

        knowledge.confidence = min(
            1.0,
            knowledge.confidence + amount,
        )

        await self.storage.update(
            knowledge
        )

        return knowledge

    async def decrease_confidence(
        self,
        knowledge: SemanticMemory,
        amount: float = 0.1,
    ) -> SemanticMemory:

        knowledge.confidence = max(
            0.0,
            knowledge.confidence - amount,
        )

        await self.storage.update(
            knowledge
        )

        return knowledge

    async def learn_from_episode(
        self,
        episode: EpisodicMemory,
    ) -> list[SemanticMemory]:
        """
        Extract reusable knowledge from an
        episodic execution.

        Production systems should use an LLM
        to extract structured lessons.
        """

        extracted = []

        if episode.reflection is None:

            return extracted

        for lesson in episode.reflection.lessons_learned:

            memory = SemanticMemory(
                title=lesson[:80],
                summary=lesson,
                content=lesson,
                category=KnowledgeCategory.BEST_PRACTICE,
                source=KnowledgeSource.EPISODIC_MEMORY,
                confidence=0.8,
                importance=0.8,
                project_id=episode.project_id,
                tags=["episode"],
            )

            await self.storage.create(
                memory
            )

            extracted.append(
                memory
            )

        logger.info(
            "Extracted %d knowledge entries from episode %s",
            len(extracted),
            episode.id,
        )

        return extracted

    async def merge(
        self,
        existing: SemanticMemory,
        incoming: SemanticMemory,
    ) -> SemanticMemory:
        """
        Merge duplicate knowledge entries.

        Production systems should use
        semantic similarity.
        """

        existing.content += (
            "\n\n"
            + incoming.content
        )

        existing.summary = (
            incoming.summary
        )

        existing.confidence = max(
            existing.confidence,
            incoming.confidence,
        )

        existing.importance = max(
            existing.importance,
            incoming.importance,
        )

        existing.tags = list(
            set(existing.tags)
            | set(incoming.tags)
        )

        existing.updated_at = datetime.utcnow()

        await self.storage.update(
            existing
        )

        return existing