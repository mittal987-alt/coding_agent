from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime

from .models import (
    EpisodicMemory,
    EpisodeStatus,
)


class BaseEpisodeStorage(ABC):
    """
    Abstract storage backend for episodic memory.
    """

    @abstractmethod
    async def create(
        self,
        episode: EpisodicMemory,
    ) -> None:
        ...

    @abstractmethod
    async def update(
        self,
        episode: EpisodicMemory,
    ) -> None:
        ...

    @abstractmethod
    async def delete(
        self,
        episode_id: str,
    ) -> None:
        ...

    @abstractmethod
    async def get(
        self,
        episode_id: str,
    ) -> EpisodicMemory | None:
        ...

    @abstractmethod
    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EpisodicMemory]:
        ...


class InMemoryEpisodeStorage(
    BaseEpisodeStorage,
):
    """
    Reference implementation.

    Production:
        PostgreSQL
        MongoDB
        DynamoDB
    """

    def __init__(self):

        self._episodes: dict[
            str,
            EpisodicMemory,
        ] = {}

    async def create(
        self,
        episode: EpisodicMemory,
    ) -> None:

        self._episodes[
            episode.id
        ] = episode

    async def update(
        self,
        episode: EpisodicMemory,
    ) -> None:

        self._episodes[
            episode.id
        ] = episode

    async def delete(
        self,
        episode_id: str,
    ) -> None:

        self._episodes.pop(
            episode_id,
            None,
        )

    async def get(
        self,
        episode_id: str,
    ) -> EpisodicMemory | None:

        return self._episodes.get(
            episode_id
        )

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EpisodicMemory]:

        episodes = sorted(
            self._episodes.values(),
            key=lambda e: e.started_at,
            reverse=True,
        )

        return episodes[
            offset : offset + limit
        ]

    async def by_project(
        self,
        project_id: str,
    ) -> list[EpisodicMemory]:

        return [

            episode

            for episode in self._episodes.values()

            if episode.project_id
            == project_id

        ]

    async def by_agent(
        self,
        agent: str,
    ) -> list[EpisodicMemory]:

        return [

            episode

            for episode in self._episodes.values()

            if episode.agent == agent

        ]

    async def by_status(
        self,
        status: EpisodeStatus,
    ) -> list[EpisodicMemory]:

        return [

            episode

            for episode in self._episodes.values()

            if episode.status == status

        ]

    async def timeline(
        self,
        project_id: str,
    ) -> list[EpisodicMemory]:
        """
        Chronological execution history.
        """

        episodes = await self.by_project(
            project_id
        )

        return sorted(
            episodes,
            key=lambda e: e.started_at,
        )

    async def search(
        self,
        query: str,
    ) -> list[EpisodicMemory]:

        query = query.lower()

        results = []

        for episode in self._episodes.values():

            text = (
                episode.title
                + " "
                + episode.description
                + " "
                + episode.user_request
            ).lower()

            if query in text:

                results.append(
                    episode
                )

        return results

    async def statistics(
        self,
    ) -> dict:

        status_counts = defaultdict(int)

        project_counts = defaultdict(int)

        for episode in self._episodes.values():

            status_counts[
                episode.status.value
            ] += 1

            if episode.project_id:

                project_counts[
                    episode.project_id
                ] += 1

        return {

            "total": len(self._episodes),

            "status": dict(
                status_counts
            ),

            "projects": dict(
                project_counts
            ),

        }