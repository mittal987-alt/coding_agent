# models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Goal(BaseModel):
    """
    Parsed user goal.
    """

    title: str

    description: str

    project_type: str | None = None

    language: str | None = None

    framework: str | None = None

    requirements: list[str] = Field(default_factory=list)

    constraints: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskNode(BaseModel):
    """
    Single executable task.
    """

    id: str

    title: str

    description: str

    agent: str

    priority: TaskPriority = TaskPriority.MEDIUM

    status: TaskStatus = TaskStatus.PENDING

    estimated_minutes: int = 10

    dependencies: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskGraph(BaseModel):
    """
    DAG of executable tasks.
    """

    goal: Goal

    tasks: list[TaskNode]

    created_at: datetime = Field(default_factory=datetime.utcnow)