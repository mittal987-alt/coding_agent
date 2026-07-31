from enum import Enum
from pydantic import BaseModel


class CapabilityType(str, Enum):

    TOOL = "tool"

    RESOURCE = "resource"

    PROMPT = "prompt"


class Capability(BaseModel):

    server: str

    name: str

    description: str

    capability_type: CapabilityType

    version: str

    metadata: dict = {}


class CapabilitySet(BaseModel):

    capabilities: list[Capability]