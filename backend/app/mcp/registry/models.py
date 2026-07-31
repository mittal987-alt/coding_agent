from enum import Enum

from pydantic import BaseModel


class ServerStatus(str, Enum):

    CONNECTING = "connecting"

    ONLINE = "online"

    OFFLINE = "offline"

    ERROR = "error"


class RegisteredServer(BaseModel):

    id: str

    name: str

    status: ServerStatus

    capabilities: list[str]

    tools: list[str]