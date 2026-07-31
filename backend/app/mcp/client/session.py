from dataclasses import dataclass

from app.mcp.models import MCPServerInfo


@dataclass
class MCPSession:

    server: MCPServerInfo

    initialized: bool = False

    protocol_version: str | None = None

    capabilities: list[str] = None