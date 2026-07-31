from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from .models import (
    DecisionMemory,
    DecisionOutcome,
    DecisionStatistics,
    DecisionStatus,
    DecisionType,
)


class BaseDecisionStorage(ABC):
    """
    Abstract storage backend for decision memory.
    """

    @abstractmethod
    async def create(
        self,
        decision: DecisionMemory,
    ) -> DecisionMemory:
        ...

    @abstractmethod
    async def get(
        self,
        decision_id: str,
    ) -> DecisionMemory | None:
        ...

    @abstractmethod
    async def update(
        self,
        decision: DecisionMemory,
    ) -> DecisionMemory:
        ...

    @abstractmethod
    async def delete(
        self,
        decision_id: str,
    ) -> bool:
        ...

    @abstractmethod
    async def list(
        self,
    ) -> list[DecisionMemory]:
        ...

    @abstractmethod
    async def statistics(
        self,
    ) -> DecisionStatistics:
        ...


class InMemoryDecisionStorage(BaseDecisionStorage):
    """
    Reference in-memory implementation.
    """

    def __init__(self) -> None:

        self._decisions: dict[str, DecisionMemory] = {}

    async def create(
        self,
        decision: DecisionMemory,
    ) -> DecisionMemory:

        self._decisions[decision.id] = decision

        return decision

    async def get(
        self,
        decision_id: str,
    ) -> DecisionMemory | None:

        return self._decisions.get(decision_id)

    async def update(
        self,
        decision: DecisionMemory,
    ) -> DecisionMemory:

        decision.updated_at = datetime.now(UTC)

        self._decisions[decision.id] = decision

        return decision

    async def delete(
        self,
        decision_id: str,
    ) -> bool:

        return self._decisions.pop(
            decision_id,
            None,
        ) is not None

    async def list(
        self,
    ) -> list[DecisionMemory]:

        return sorted(
            self._decisions.values(),
            key=lambda d: d.created_at,
            reverse=True,
        )

    async def by_project(
        self,
        project_id: str,
    ) -> list[DecisionMemory]:

        return [
            decision
            for decision in self._decisions.values()
            if decision.project_id == project_id
        ]

    async def by_type(
        self,
        decision_type: DecisionType,
    ) -> list[DecisionMemory]:

        return [
            decision
            for decision in self._decisions.values()
            if decision.decision_type == decision_type
        ]

    async def by_status(
        self,
        status: DecisionStatus,
    ) -> list[DecisionMemory]:

        return [
            decision
            for decision in self._decisions.values()
            if decision.status == status
        ]

    async def by_outcome(
        self,
        outcome: DecisionOutcome,
    ) -> list[DecisionMemory]:

        return [
            decision
            for decision in self._decisions.values()
            if decision.outcome == outcome
        ]

    async def search(
        self,
        query: str,
    ) -> list[DecisionMemory]:

        query = query.lower()

        return [
            decision
            for decision in self._decisions.values()
            if (
                query in decision.title.lower()
                or query in decision.description.lower()
                or query in decision.reasoning.lower()
                or query in decision.rationale.lower()
            )
        ]

    async def statistics(
        self,
    ) -> DecisionStatistics:

        decisions = list(
            self._decisions.values()
        )

        accepted = sum(
            1
            for d in decisions
            if d.status == DecisionStatus.ACCEPTED
        )

        rejected = sum(
            1
            for d in decisions
            if d.status == DecisionStatus.REJECTED
        )

        superseded = sum(
            1
            for d in decisions
            if d.status == DecisionStatus.SUPERSEDED
        )

        successful = sum(
            1
            for d in decisions
            if d.outcome == DecisionOutcome.SUCCESS
        )

        failed = sum(
            1
            for d in decisions
            if d.outcome == DecisionOutcome.FAILURE
        )

        average_confidence = (
            sum(d.confidence for d in decisions)
            / len(decisions)
            if decisions
            else 0.0
        )

        return DecisionStatistics(
            total_decisions=len(decisions),
            accepted=accepted,
            rejected=rejected,
            superseded=superseded,
            successful=successful,
            failed=failed,
            average_confidence=average_confidence,
            last_updated=datetime.now(UTC),
        )