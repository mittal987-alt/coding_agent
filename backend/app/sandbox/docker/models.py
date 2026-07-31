# Models module
from enum import Enum
from pydantic import BaseModel


class ContainerStatus(str, Enum):

    CREATED = "created"

    RUNNING = "running"

    STOPPED = "stopped"

    FAILED = "failed"


class SandboxContainer(BaseModel):

    id: str

    image: str

    workspace: str

    status: ContainerStatus