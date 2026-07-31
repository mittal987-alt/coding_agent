from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class MCPTransport(str, Enum):

    STDIO = "stdio"

    HTTP = "http"

    WEBSOCKET = "websocket"


class MCPCapability(str, Enum):

    TOOL = "tool"

    RESOURCE = "resource"

    PROMPT = "prompt"


class MCPServerInfo(BaseModel):

    id: str

    name: str

    version: str

    transport: MCPTransport

    endpoint: str


class MCPTool(BaseModel):

    name: str

    description: str

    input_schema: dict[str, Any]

    output_schema: dict[str, Any]


class MCPResource(BaseModel):

    uri: str

    name: str

    description: str


class MCPPrompt(BaseModel):

    name: str

    description: str


class MCPRequest(BaseModel):

    method: str

    params: dict[str, Any] = {}


class MCPResponse(BaseModel):

    success: bool

    result: dict[str, Any] | None = None

    error: str | None = None