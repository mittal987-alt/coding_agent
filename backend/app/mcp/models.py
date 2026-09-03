"""
Model Context Protocol (MCP) Data Models

Defines all Pydantic v2 models for MCP server configurations,
tool definitions, resource descriptors, and JSON-RPC message envelopes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class MCPTransport(str, Enum):
    """Wire transport used to communicate with the MCP server."""

    STDIO = "stdio"
    """Subprocess stdin/stdout (e.g. npx mcp-server, uvx mcp-server)."""

    HTTP = "http"
    """HTTP JSON-RPC 2.0 POST endpoint."""

    WEBSOCKET = "websocket"
    """WebSocket JSON-RPC (planned)."""


class MCPCapability(str, Enum):
    """Capabilities an MCP server may expose."""

    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"


class MCPServerInfo(BaseModel):
    """
    Configuration for a single MCP server connection.

    HTTP servers require `url`.
    STDIO servers require `command`.
    """

    id: str = Field(..., description="Unique server identifier (e.g. 'github-mcp')")
    name: str = Field(..., description="Human-readable server name")
    version: str = Field(default="1.0.0", description="Server version string")
    transport: MCPTransport = Field(..., description="Wire transport type")

    # HTTP transport fields
    url: Optional[str] = Field(
        default=None,
        description="HTTP endpoint URL for JSON-RPC 2.0 calls (required for HTTP transport)",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key sent as Bearer token in Authorization header",
    )

    # STDIO transport fields
    command: Optional[list[str]] = Field(
        default=None,
        description="Command to launch the STDIO MCP server process "
                    "(e.g. ['npx', '@modelcontextprotocol/server-github'])",
    )

    # Legacy field — kept for backwards compat with older server configs
    endpoint: Optional[str] = Field(
        default=None,
        description="Deprecated: use `url` for HTTP servers.",
    )


class MCPTool(BaseModel):
    """A single tool exposed by an MCP server (discovered via tools/list)."""

    name: str = Field(..., description="Tool name used to invoke it (e.g. 'create_pull_request')")
    description: str = Field(default="", description="Human-readable description of the tool")
    input_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema describing the tool's input arguments",
    )
    output_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema describing the tool's output structure",
    )


class MCPResource(BaseModel):
    """A resource exposed by an MCP server (discovered via resources/list)."""

    uri: str
    name: str
    description: str = ""


class MCPPrompt(BaseModel):
    """A prompt template exposed by an MCP server."""

    name: str
    description: str = ""


class MCPRequest(BaseModel):
    """Outbound JSON-RPC 2.0 request envelope."""

    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """Inbound JSON-RPC 2.0 response envelope."""

    success: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None