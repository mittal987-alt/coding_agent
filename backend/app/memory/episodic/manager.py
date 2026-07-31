# episodic/manager.py
from __future__ import annotations

import logging
from datetime import datetime

from .models import (
    EpisodicMemory,
    EpisodeStatus,
    EpisodeStep,
    EpisodeType,
    Reflection,
    ToolInvocation,
)
from .storage import BaseEpisodeStorage

logger = logging.getLogger(__name__)


class EpisodicMemoryManager:
    """
    High-level service for managing episodic memories.

    This is the interface used by AI agents to
    record their execution history.
    """

    def __init__(
        self,
        storage: BaseEpisodeStorage,
    ) -> None:
        self.storage = storage

    async def start_episode(
        self,
        *,
        title: str,
        description: str,
        episode_type: EpisodeType,
        agent: str,
        user_request: str,
        project_id: str | None = None,
        workflow_id: str | None = None,
        branch: str | None = None,
        metadata: dict | None = None,
    ) -> EpisodicMemory:
        """
        Create a new execution episode.
        """

        episode = EpisodicMemory(
            title=title,
            description=description,
            episode_type=episode_type,
            status=EpisodeStatus.RUNNING,
            project_id=project_id,
            workflow_id=workflow_id,
            branch=branch,
            agent=agent,
            user_request=user_request,
            metadata=metadata or {},
        )

        await self.storage.create(episode)

        logger.info(
            "Started episode %s",
            episode.id,
        )

        return episode

    async def add_step(
        self,
        episode: EpisodicMemory,
        step: EpisodeStep,
    ) -> EpisodeStep:
        """
        Add a step to an episode.
        """

        episode.steps.append(step)

        await self.storage.update(episode)

        return step

    async def add_tool_invocation(
        self,
        step: EpisodeStep,
        invocation: ToolInvocation,
    ) -> ToolInvocation:
        """
        Record a tool execution.
        """

        step.tool_invocations.append(invocation)

        return invocation

    async def complete_step(
        self,
        step: EpisodeStep,
        *,
        success: bool = True,
    ) -> None:

        step.status = (
            EpisodeStatus.SUCCESS
            if success
            else EpisodeStatus.FAILED
        )

        step.completed_at = datetime.utcnow()

        if step.started_at:
            step.duration_seconds = (
                step.completed_at
                - step.started_at
            ).total_seconds()

    async def complete_episode(
        self,
        episode: EpisodicMemory,
        *,
        reflection: Reflection | None = None,
    ) -> EpisodicMemory:
        """
        Finish an episode.
        """

        episode.status = EpisodeStatus.SUCCESS

        episode.success = True

        episode.completed_at = datetime.utcnow()

        episode.duration_seconds = (
            episode.completed_at
            - episode.started_at
        ).total_seconds()

        episode.reflection = reflection

        await self.storage.update(episode)

        logger.info(
            "Completed episode %s",
            episode.id,
        )

        return episode

    async def fail_episode(
        self,
        episode: EpisodicMemory,
        *,
        error: str,
    ) -> EpisodicMemory:
        """
        Mark an episode as failed.
        """

        episode.status = EpisodeStatus.FAILED

        episode.success = False

        episode.metadata["error"] = error

        episode.completed_at = datetime.utcnow()

        episode.duration_seconds = (
            episode.completed_at
            - episode.started_at
        ).total_seconds()

        await self.storage.update(episode)

        logger.warning(
            "Episode %s failed: %s",
            episode.id,
            error,
        )

        return episode

    async def generate_reflection(
        self,
        episode: EpisodicMemory,
    ) -> Reflection:
        """
        Generate a basic reflection.

        In production this should call an LLM.
        """

        reflection = Reflection(
            summary=(
                f"Episode '{episode.title}' "
                f"completed with status "
                f"{episode.status.value}."
            ),
            lessons_learned=[],
            mistakes=[],
            recommendations=[],
            confidence=1.0,
            score=1.0,
        )

        episode.reflection = reflection

        await self.storage.update(episode)

        return reflection

    async def search(
        self,
        query: str,
    ) -> list[EpisodicMemory]:
        """
        Search execution history.
        """

        return await self.storage.search(query)

    async def timeline(
        self,
        project_id: str,
    ) -> list[EpisodicMemory]:
        """
        Retrieve chronological execution history.
        """

        return await self.storage.timeline(project_id)

    async def statistics(self) -> dict:
        """
        Get storage statistics.
        """

        return await self.storage.statistics()