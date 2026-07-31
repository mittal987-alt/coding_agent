#
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)
class ToolInfo(BaseSchema):
    """
    Registered tool metadata.
    """

    name: str

    display_name: str

    description: str

    category: Literal[
        "filesystem",
        "terminal",
        "git",
        "python",
        "docker",
        "browser",
        "database",
        "network",
        "mcp",
        "plugin",
        "custom",
    ]

    version: str

    enabled: bool = True

    requires_workspace: bool = True

    supports_streaming: bool = False
class ToolListResponse(BaseSchema):

    tools: list[ToolInfo]

class ToolExecuteRequest(BaseSchema):

    tool: str

    arguments: dict[str, Any] = Field(
        default_factory=dict,
    )

    workspace: str | None = None

    timeout: int = Field(
        default=300,
        ge=1,
        le=3600,
    )

    stream: bool = False

class ToolExecutionStatus(BaseSchema):

    status: Literal[
        "queued",
        "running",
        "completed",
        "failed",
        "cancelled",
    ]

class ToolOutput(BaseSchema):

    stdout: str = ""

    stderr: str = ""

    files: list[str] = Field(
        default_factory=list,
    )

class ToolExecuteResponse(BaseSchema):

    execution_id: str

    tool: str

    status: str

    output: ToolOutput

    exit_code: int

    execution_time_ms: float

class ToolStreamChunk(BaseSchema):

    execution_id: str

    chunk: str

    finished: bool = False

class ToolPermission(BaseSchema):

    tool: str

    allowed: bool

    reason: str | None = None

class SandboxConfiguration(BaseSchema):

    cpu_limit: float

    memory_limit_mb: int

    disk_limit_mb: int

    network_enabled: bool

    read_only: bool

class ToolExecutionRecord(TimestampSchema):

    execution_id: str

    tool: str

    workspace: str | None = None

    status: str

    execution_time_ms: float

    exit_code: int

    
class ToolExecutionHistory(BaseSchema):

    executions: list[ToolExecutionRecord]

class MCPServer(BaseSchema):

    name: str

    version: str

    connected: bool

    tools: list[str]
class PluginList(BaseSchema):

    plugins: list[PluginInfo]
class PluginInfo(BaseSchema):

    id: str

    name: str

    version: str

    author: str

    description: str

    enabled: bool
class ToolHealth(BaseSchema):

    tool: str

    healthy: bool

    latency_ms: float

    last_checked: datetime

class ToolEvent(BaseSchema):

    event: Literal[
        "started",
        "progress",
        "stdout",
        "stderr",
        "completed",
        "failed",
        "cancelled",
    ]

    execution_id: str

    data: dict[str, Any] = Field(
        default_factory=dict,
    )

class ToolMetrics(BaseSchema):

    total_executions: int

    successful_executions: int

    failed_executions: int

    average_execution_time_ms: float
class ToolCapability(BaseSchema):

    name: str

    description: str

class ToolDiagnostics(BaseSchema):

    tool: str

    version: str

    capabilities: list[ToolCapability]

    sandbox: SandboxConfiguration | None = None