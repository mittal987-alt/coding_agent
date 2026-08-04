from __future__ import annotations

from datetime import datetime

from typing import Any, Literal

from pydantic import Field, field_validator

from app.api.schemas.base_schema import BaseSchema
from app.models.workspace import ProjectVisibility


class RepositoryInfo(BaseSchema):

    id: str

    owner_id: str

    owner_name: str

    repo_id: str

    repo_name: str

    provider: Literal[
        "github",
        "gitlab",
        "bitbucket",
        "azure",
    ]

    created_at: datetime

    updated_at: datetime
class Collaborator(BaseSchema):

    user_id: str

    email: str | None = None

    role: Literal[
        "owner",
        "admin",
        "developer",
        "viewer",
    ]

    joined_at: datetime

    last_active: datetime | None = None
class ProjectCreateRequest(BaseSchema):

    name: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    visibility: ProjectVisibility = ProjectVisibility.PRIVATE

from app.api.schemas.common import TimestampSchema
class ProjectCreateRequest(BaseSchema):

    name: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    visibility: Literal[
        "private",
        "public",
    ] = "private"
class ProjectUpdateRequest(BaseSchema):

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    visibility: Literal[
        "private",
        "public",
    ] | None = None
class ProjectResponse(TimestampSchema):

    id: str

    name: str

    description: str | None

    visibility: Literal[
        "private",
        "public",
    ]

    owner_id: str

    created_at: datetime

    updated_at: datetime
class WorkspaceUsage(BaseSchema):

    total_workspaces: int

    active_workspaces: int

    inactive_workspaces: int

    total_size_bytes: int

    language_breakdown: dict[str, int]

    created_at: datetime

    updated_at: datetime
class ProjectMember(BaseSchema):

    user_id: str

    role: str

    joined_at: datetime
class ProjectSettings(BaseSchema):

    default_branch: str = "main"

    environment: Literal[
        "development",
        "staging",
        "production",
    ] = "development"

    resource_limits: dict[str, int] = Field(
        default_factory=dict,
    )

    notifications: dict[str, bool] = Field(
        default_factory=dict,
    )   
class AddCollaboratorRequest(BaseSchema):

    email: str

    role: Literal[
        "admin",
        "developer",
        "viewer",
    ]
class RemoveCollaboratorRequest(BaseSchema):

    user_id: str
class EnvironmentVariable(BaseSchema):

    key: str

    value: str

    secret: bool = False
class ProjectEnvironment(BaseSchema):

    name: Literal[
        "development",
        "staging",
        "production",
    ]

    variables: list[EnvironmentVariable] = Field(
        default_factory=list,
    )
class DeploymentConfig(BaseSchema):

    provider: Literal[
        "docker",
        "kubernetes",
        "vercel",
        "render",
        "aws",
        "azure",
        "gcp",
    ]

    auto_deploy: bool = False

    build_command: str | None = None

    start_command: str | None = None    
class ProjectSettings(BaseSchema):

    default_model: str

    enable_memory: bool = True

    enable_tools: bool = True

    enable_planner: bool = True

    enable_rag: bool = True

    max_parallel_agents: int = Field(
        default=4,
        ge=1,
        le=32,
    )
class ProjectResponse(TimestampSchema):

    id: str

    name: str

    description: str | None = None

    visibility: str

    repository: RepositoryInfo | None = None

    collaborators: list[Collaborator] = Field(
        default_factory=list,
    )

    settings: ProjectSettings

    deployment: DeploymentConfig | None = None
class ProjectStatistics(BaseSchema):

    total_files: int

    total_commits: int

    contributors: int

    active_branches: int

    open_tasks: int

    completed_tasks: int

    languages: dict[str, int] = Field(
        default_factory=dict,
    )
class ProjectSummary(BaseSchema):

    id: str

    name: str

    description: str | None = None

    updated_at: datetime
class ProjectList(BaseSchema):

    projects: list[ProjectSummary]
class ProjectEvent(BaseSchema):

    event: Literal[
        "created",
        "updated",
        "deleted",
        "member_added",
        "member_removed",
        "deployment_started",
        "deployment_completed",
    ]

    project_id: str

    data: dict[str, Any] = Field(
        default_factory=dict,
    )
class ProjectMetrics(BaseSchema):

    build_success_rate: float

    average_build_time_ms: float

    deployments: int

    ai_tasks_completed: int

    token_usage: int