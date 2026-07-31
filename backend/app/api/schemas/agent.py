#
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)
class AgentRunRequest(BaseSchema):
    """
    Start a new autonomous agent task.
    """

    goal: str = Field(
        min_length=1,
        max_length=10000,
    )

    workspace: str

    model: str | None = None

    context: dict[str, Any] = Field(
        default_factory=dict,
    )

    timeout: int = Field(
        default=1800,
        ge=60,
        le=86400,
    )

    allow_tools: bool = True

    stream: bool = False
class AgentStatus(BaseSchema):

    status: Literal[
        "queued",
        "planning",
        "running",
        "waiting",
        "completed",
        "failed",
        "cancelled",
    ]
class AgentProgress(BaseSchema):

    percentage: float = Field(
        ge=0,
        le=100,
    )

    current_step: str

    completed_steps: int

    total_steps: int
class PlannerStep(BaseSchema):

    id: str

    title: str

    description: str

    completed: bool = False
class ExecutionLog(TimestampSchema):

    level: Literal[
        "debug",
        "info",
        "warning",
        "error",
    ]

    source: str

    message: str
class ToolExecution(BaseSchema):

    tool: str

    arguments: dict[str, Any]

    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ]

    started_at: datetime | None = None

    finished_at: datetime | None = None
class AgentResult(BaseSchema):

    success: bool

    output: str

    files: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
class AgentRunResponse(BaseSchema):

    task_id: str

    status: str
class AgentStatusResponse(BaseSchema):

    task_id: str

    status: str

    progress: AgentProgress

    current_step: str
class AgentTask(TimestampSchema):

    id: str

    goal: str

    workspace: str

    model: str

    status: AgentStatus

    progress: AgentProgress

    planner: list[PlannerStep] = Field(
        default_factory=list,
    )

    tools: list[ToolExecution] = Field(
        default_factory=list,
    )

    logs: list[ExecutionLog] = Field(
        default_factory=list,
    )

    result: AgentResult | None = None

class CancelAgentRequest(BaseSchema):

    reason: str | None = None
class RetryAgentRequest(BaseSchema):

    reuse_workspace: bool = True

    reuse_memory: bool = True

class AgentEvent(BaseSchema):

    event: Literal[
        "started",
        "planning",
        "progress",
        "tool_start",
        "tool_end",
        "completed",
        "failed",
        "cancelled",
    ]

    task_id: str

    data: dict[str, Any] = Field(
        default_factory=dict,
    )