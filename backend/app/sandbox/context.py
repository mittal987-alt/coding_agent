from uuid import uuid4

from pydantic import BaseModel

from app.sandbox.limits import ResourceLimits


class ExecutionContext(BaseModel):

    execution_id: str = str(uuid4())

    workspace: str

    image: str

    command: str

    environment: dict[str, str] = {}

    limits: ResourceLimits

    network_enabled: bool = False

    interactive: bool = False