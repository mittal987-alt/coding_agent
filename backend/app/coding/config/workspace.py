from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

WorkspaceIsolation = Literal[
    "none",
    "directory",
    "docker",
]

GitStrategy = Literal[
    "reuse",
    "clone",
    "mirror",
]



@dataclass(slots=True)
class WorkspacePathConfig:
    """
    Workspace directory configuration.
    """

    root: Path = Path("workspace")

    repositories: Path = Path("workspace/repos")

    temporary: Path = Path("workspace/tmp")

    cache: Path = Path("workspace/cache")

    artifacts: Path = Path("workspace/artifacts")

    logs: Path = Path("workspace/logs")

@dataclass(slots=True)
class RepositoryConfig:
    """
    Git repository settings.
    """

    clone_depth: int = 1

    auto_pull: bool = False

    cleanup_after_task: bool = False

    git_strategy: GitStrategy = "clone"

    default_branch: str = "main"

@dataclass(slots=True)
class IsolationConfig:
    """
    Workspace isolation settings.
    """

    enabled: bool = True

    mode: WorkspaceIsolation = "directory"

    separate_temp: bool = True

    readonly_input: bool = False

    auto_cleanup: bool = True

@dataclass(slots=True)
class StorageConfig:
    """
    Workspace storage limits.
    """

    max_workspace_size_mb: int = 10240

    max_repository_size_mb: int = 2048

    max_file_size_mb: int = 100

    cleanup_interval_minutes: int = 60
@dataclass(slots=True)
class FileManagerConfig:
    """
    File operation settings.
    """

    backup_before_write: bool = True

    preserve_permissions: bool = True

    overwrite_existing: bool = True

    create_missing_directories: bool = True

    follow_symlinks: bool = False

@dataclass(slots=True)
class GitConfig:
    """
    Git integration.
    """

    enabled: bool = True

    auto_commit: bool = False

    auto_push: bool = False

    commit_message_prefix: str = "[AI]"

    author_name: str = "AI Software Engineer"

    author_email: str = "ai@example.com"

@dataclass(slots=True)
class WorkspaceManagerConfig:
    """
    Workspace manager settings.
    """

    max_active_workspaces: int = 20

    idle_timeout_minutes: int = 30

    preload_projects: bool = False

    enable_indexing: bool = True

@dataclass(slots=True)
class WorkspaceConfig:
    """
    Complete workspace configuration.
    """

    paths: WorkspacePathConfig = field(
        default_factory=WorkspacePathConfig,
    )

    repositories: RepositoryConfig = field(
        default_factory=RepositoryConfig,
    )

    isolation: IsolationConfig = field(
        default_factory=IsolationConfig,
    )

    storage: StorageConfig = field(
        default_factory=StorageConfig,
    )

    files: FileManagerConfig = field(
        default_factory=FileManagerConfig,
    )

    git: GitConfig = field(
        default_factory=GitConfig,
    )

    manager: WorkspaceManagerConfig = field(
        default_factory=WorkspaceManagerConfig,
    )

def create_workspace_config() -> WorkspaceConfig:
    """
    Create the default workspace configuration.
    """
    return WorkspaceConfig()