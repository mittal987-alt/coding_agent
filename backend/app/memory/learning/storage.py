from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from .models import (
    LearningCategory,
    LearningMemory,
    LearningOutcome,
    LearningSource,
    LearningStatistics,
)


class BaseLearningStorage(ABC):
    """
    Abstract storage backend for learning memory.
    """

    @abstractmethod
    async def create(
        self,
        learning: LearningMemory,
    ) -> LearningMemory:
        ...

    @abstractmethod
    async def get(
        self,
        learning_id: str,
    ) -> LearningMemory | None:
        ...

    @abstractmethod
    async def update(
        self,
        learning: LearningMemory,
    ) -> LearningMemory:
        ...

    @abstractmethod
    async def delete(
        self,
        learning_id: str,
    ) -> bool:
        ...

    @abstractmethod
    async def list(
        self,
    ) -> list[LearningMemory]:
        ...

    @abstractmethod
    async def statistics(
        self,
    ) -> LearningStatistics:
        ...


class InMemoryLearningStorage(BaseLearningStorage):
    """
    Reference in-memory implementation.
    """

    def __init__(self) -> None:
        self._lessons: dict[str, LearningMemory] = {}

    async def create(
        self,
        learning: LearningMemory,
    ) -> LearningMemory:

        self._lessons[learning.id] = learning

        return learning

    async def get(
        self,
        learning_id: str,
    ) -> LearningMemory | None:

        return self._lessons.get(learning_id)

    async def update(
        self,
        learning: LearningMemory,
    ) -> LearningMemory:

        learning.updated_at = datetime.now(UTC)

        self._lessons[learning.id] = learning

        return learning

    async def delete(
        self,
        learning_id: str,
    ) -> bool:

        return self._lessons.pop(
            learning_id,
            None,
        ) is not None

    async def list(
        self,
    ) -> list[LearningMemory]:

        return sorted(
            self._lessons.values(),
            key=lambda lesson: lesson.created_at,
            reverse=True,
        )

    async def by_category(
        self,
        category: LearningCategory,
    ) -> list[LearningMemory]:

        return [
            lesson
            for lesson in self._lessons.values()
            if lesson.category == category
        ]

    async def by_source(
        self,
        source: LearningSource,
    ) -> list[LearningMemory]:

        return [
            lesson
            for lesson in self._lessons.values()
            if lesson.source == source
        ]

    async def by_outcome(
        self,
        outcome: LearningOutcome,
    ) -> list[LearningMemory]:

        return [
            lesson
            for lesson in self._lessons.values()
            if lesson.outcome == outcome
        ]

    async def by_project(
        self,
        project_id: str,
    ) -> list[LearningMemory]:

        return [
            lesson
            for lesson in self._lessons.values()
            if project_id in lesson.project_ids
        ]

    async def search(
        self,
        query: str,
    ) -> list[LearningMemory]:

        query = query.lower()

        return [
            lesson
            for lesson in self._lessons.values()
            if (
                query in lesson.title.lower()
                or query in lesson.description.lower()
                or query in lesson.lesson.lower()
                or any(
                    query in tag.lower()
                    for tag in lesson.tags
                )
            )
        ]

    async def statistics(
        self,
    ) -> LearningStatistics:

        lessons = list(self._lessons.values())

        successful = sum(
            1
            for lesson in lessons
            if lesson.outcome == LearningOutcome.SUCCESS
        )

        failed = sum(
            1
            for lesson in lessons
            if lesson.outcome == LearningOutcome.FAILURE
        )

        average_confidence = (
            sum(
                lesson.confidence
                for lesson in lessons
            )
            / len(lessons)
            if lessons
            else 0.0
        )

        total_feedback = sum(
            len(lesson.feedback)
            for lesson in lessons
        )

        total_usage = sum(
            lesson.usage_count
            for lesson in lessons
        )

        return LearningStatistics(
            total_lessons=len(lessons),
            successful_patterns=successful,
            failed_patterns=failed,
            average_confidence=average_confidence,
            total_feedback=total_feedback,
            total_usage=total_usage,
            last_updated=datetime.now(UTC),
        )