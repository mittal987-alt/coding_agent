# episodic/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EpisodeType(str, Enum):
    """
    Types of AI execution episodes.
    """

    TASK = "task"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    REFACTOR = "refactor"
    DEBUGGING = "debugging"
    TERMINAL = "terminal"
    WORKFLOW = "workflow"


class EpisodeStatus(str, Enum):
    """
    Final status of an episode.
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionArtifact(BaseModel):
    """
    Files or outputs generated during execution.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    artifact_type: str

    path: str

    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolInvocation(BaseModel):
    """
    Tool usage during execution.
    """

    tool_name: str

    started_at: datetime

    finished_at: datetime | None = None

    success: bool = True

    input_data: dict[str, Any] = Field(default_factory=dict)

    output_data: dict[str, Any] = Field(default_factory=dict)

    error: str | None = None


class EpisodeStep(BaseModel):
    """
    One step within an episode.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    agent: str

    status: EpisodeStatus = EpisodeStatus.PENDING

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float | None = None

    tool_invocations: list[
        ToolInvocation
    ] = Field(default_factory=list)

    artifacts: list[
        ExecutionArtifact
    ] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class Reflection(BaseModel):
    """
    AI self-reflection after execution.
    """

    summary: str

    lessons_learned: list[str] = Field(
        default_factory=list
    )

    mistakes: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )

    confidence: float = 1.0

    score: float = 1.0


class EpisodicMemory(BaseModel):
    """
    Complete execution episode.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    episode_type: EpisodeType

    status: EpisodeStatus = EpisodeStatus.PENDING

    project_id: str | None = None

    workflow_id: str | None = None

    branch: str | None = None

    agent: str

    user_request: str

    steps: list[
        EpisodeStep
    ] = Field(default_factory=list)

    reflection: Reflection | None = None

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    started_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    completed_at: datetime | None = None

    duration_seconds: float | None = None

    success: bool = False