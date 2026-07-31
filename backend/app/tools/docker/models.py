

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ContainerStatus(str, Enum):

    CREATED = "created"

    RUNNING = "running"

    STOPPED = "stopped"

    REMOVED = "removed"


class DockerRequest(BaseModel):

    image: str

    workspace: str

    command: str

    timeout: int = 600


class DockerResult(BaseModel):

    success: bool

    stdout: str

    stderr: str

    exit_code: int

    container_id: str