# learning/manager.py
from __future__ import annotations

from datetime import UTC, datetime

from .models import (
    LearningCategory,
    LearningFeedback,
    LearningMemory,
    LearningOutcome,
    LearningPattern,
    LearningSource,
    LearningStatistics,
)
from .storage import BaseLearningStorage


class LearningMemoryManager:
    """
    High-level manager for learning memory.

    Responsibilities:
    - Store lessons learned
    - Record successes and failures
    - Manage feedback
    - Extract reusable patterns
    - Update confidence
    - Build learning context
    """

    def __init__(
        self,
        storage: BaseLearningStorage,
    ) -> None:
        self.storage = storage

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------

    async def create_learning(
        self,
        *,
        title: str,
        description: str,
        lesson: str,
        category: LearningCategory,
        source: LearningSource,
        outcome: LearningOutcome = LearningOutcome.UNKNOWN,
        confidence: float = 1.0,
        project_ids: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> LearningMemory:

        learning = LearningMemory(
            title=title,
            description=description,
            lesson=lesson,
            category=category,
            source=source,
            outcome=outcome,
            confidence=confidence,
            project_ids=project_ids or [],
            tags=tags or [],
        )

        return await self.storage.create(learning)

    async def get_learning(
        self,
        learning_id: str,
    ) -> LearningMemory | None:
        return await self.storage.get(learning_id)

    async def delete_learning(
        self,
        learning_id: str,
    ) -> bool:
        return await self.storage.delete(learning_id)

    async def list_learning(
        self,
    ) -> list[LearningMemory]:
        return await self.storage.list()

    # ---------------------------------------------------------
    # Updates
    # ---------------------------------------------------------

    async def update_confidence(
        self,
        learning_id: str,
        confidence: float,
    ) -> LearningMemory:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.confidence = confidence
        learning.updated_at = datetime.now(UTC)

        return await self.storage.update(learning)

    async def update_outcome(
        self,
        learning_id: str,
        outcome: LearningOutcome,
    ) -> LearningMemory:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.outcome = outcome
        learning.updated_at = datetime.now(UTC)

        return await self.storage.update(learning)

    # ---------------------------------------------------------
    # Usage Tracking
    # ---------------------------------------------------------

    async def record_success(
        self,
        learning_id: str,
    ) -> None:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.usage_count += 1
        learning.success_count += 1
        learning.updated_at = datetime.now(UTC)

        await self.storage.update(learning)

    async def record_failure(
        self,
        learning_id: str,
    ) -> None:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.usage_count += 1
        learning.failure_count += 1
        learning.updated_at = datetime.now(UTC)

        await self.storage.update(learning)

    # ---------------------------------------------------------
    # Feedback
    # ---------------------------------------------------------

    async def add_feedback(
        self,
        learning_id: str,
        feedback: LearningFeedback,
    ) -> None:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.feedback.append(feedback)
        learning.updated_at = datetime.now(UTC)

        await self.storage.update(learning)

    # ---------------------------------------------------------
    # Pattern Management
    # ---------------------------------------------------------

    async def set_pattern(
        self,
        learning_id: str,
        pattern: LearningPattern,
    ) -> None:

        learning = await self.storage.get(learning_id)

        if learning is None:
            raise ValueError("Learning record not found")

        learning.pattern = pattern
        learning.updated_at = datetime.now(UTC)

        await self.storage.update(learning)

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    async def search(
        self,
        query: str,
    ) -> list[LearningMemory]:

        return await self.storage.search(query)

    async def by_category(
        self,
        category: LearningCategory,
    ) -> list[LearningMemory]:

        return await self.storage.by_category(category)

    async def by_source(
        self,
        source: LearningSource,
    ) -> list[LearningMemory]:

        return await self.storage.by_source(source)

    async def successful_patterns(
        self,
    ) -> list[LearningMemory]:

        return await self.storage.by_outcome(
            LearningOutcome.SUCCESS
        )

    async def failed_patterns(
        self,
    ) -> list[LearningMemory]:

        return await self.storage.by_outcome(
            LearningOutcome.FAILURE
        )

    async def project_learning(
        self,
        project_id: str,
    ) -> list[LearningMemory]:

        return await self.storage.by_project(project_id)

    # ---------------------------------------------------------
    # Context Builder
    # ---------------------------------------------------------

    async def build_context(
        self,
        project_id: str,
    ) -> list[dict]:

        lessons = await self.storage.by_project(project_id)

        lessons.sort(
            key=lambda lesson: lesson.confidence,
            reverse=True,
        )

        return [
            {
                "title": lesson.title,
                "lesson": lesson.lesson,
                "category": lesson.category.value,
                "confidence": lesson.confidence,
                "usage_count": lesson.usage_count,
                "success_count": lesson.success_count,
                "failure_count": lesson.failure_count,
            }
            for lesson in lessons
        ]

    # ---------------------------------------------------------
    # Best Practices
    # ---------------------------------------------------------

    async def best_practices(
        self,
        minimum_confidence: float = 0.8,
    ) -> list[LearningMemory]:

        lessons = await self.storage.list()

        return [
            lesson
            for lesson in lessons
            if lesson.confidence >= minimum_confidence
            and lesson.success_count >= lesson.failure_count
        ]

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    async def statistics(
        self,
    ) -> LearningStatistics:

        return await self.storage.statistics()