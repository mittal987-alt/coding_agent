"""
Model Context Protocol (MCP) Client Manager

Connects the FastAPI backend to external MCP servers using real transports:
  - HTTP:  JSON-RPC 2.0 over HTTP POST via httpx.AsyncClient
  - STDIO: subprocess stdin/stdout JSON-RPC via asyncio.create_subprocess_exec
  - WS:    WebSocket JSON-RPC (planned)

On connection, performs capability discovery (`tools/list`) to register
all tools exposed by the server.

Usage::

    manager = MCPClientManager()
    await manager.connect_server(server_info)
    tools = manager.list_available_tools()
    result = await manager.execute_tool("github_create_pr", {"title": "Fix bug"})
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from app.mcp.models import (
    MCPServerInfo,
    MCPTool,
    MCPResource,
    MCPTransport,
    MCPRequest,
    MCPResponse,
)

logger = logging.getLogger(__name__)

# Per-request timeout for MCP tool executions (seconds)
MCP_TIMEOUT_SECONDS: float = 30.0


class MCPClientManager:
    """
    Manages active MCP server sessions and routes tool execution requests.

    Supports real HTTP JSON-RPC 2.0 and STDIO transports.
    """

    def __init__(self) -> None:
        self.servers: Dict[str, MCPServerInfo] = {}
        self.tools_registry: Dict[str, MCPTool] = {}
        self.tool_to_server: Dict[str, str] = {}
        self._http_clients: Dict[str, httpx.AsyncClient] = {}

    # ------------------------------------------------------------------
    # Server management
    # ------------------------------------------------------------------

    def register_server(self, server: MCPServerInfo) -> bool:
        """Register an MCP server configuration (does not connect yet)."""
        self.servers[server.id] = server
        logger.info("MCP server registered: %s (%s)", server.name, server.transport)
        return True

    async def connect_server(self, server: MCPServerInfo) -> bool:
        """
        Register a server AND perform capability discovery (tools/list).

        Args:
            server: MCPServerInfo describing the target MCP server.

        Returns:
            True if connection and discovery succeeded, False otherwise.
        """
        self.register_server(server)

        if server.transport == MCPTransport.HTTP:
            return await self._discover_http_tools(server)
        elif server.transport == MCPTransport.STDIO:
            return await self._discover_stdio_tools(server)
        else:
            logger.warning("MCP: unsupported transport %s", server.transport)
            return False

    async def disconnect_all(self) -> None:
        """Close all active HTTP client sessions."""
        for client in self._http_clients.values():
            await client.aclose()
        self._http_clients.clear()

    def register_tool(self, server_id: str, tool: MCPTool) -> None:
        """Manually register a tool exposed by an MCP server."""
        self.tools_registry[tool.name] = tool
        self.tool_to_server[tool.name] = server_id
        logger.debug("MCP tool registered: %s → %s", tool.name, server_id)

    def list_available_tools(self) -> List[MCPTool]:
        """Return all tools discovered across connected MCP servers."""
        return list(self.tools_registry.values())

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> MCPResponse:
        """
        Execute a named tool on its registered MCP server.

        Routes to the correct transport handler based on server config.

        Args:
            tool_name:  Name of the tool as discovered in tools/list.
            arguments:  Dict of argument name → value for the tool call.

        Returns:
            MCPResponse with success flag, result or error.
        """
        if tool_name not in self.tools_registry:
            return MCPResponse(
                success=False,
                error=f"MCP tool '{tool_name}' is not registered. "
                      f"Available: {list(self.tools_registry.keys())}",
            )

        server_id = self.tool_to_server[tool_name]
        server = self.servers.get(server_id)

        if not server:
            return MCPResponse(
                success=False,
                error=f"MCP server '{server_id}' is not registered.",
            )

        try:
            if server.transport == MCPTransport.HTTP:
                return await self._execute_http(server, tool_name, arguments)
            elif server.transport == MCPTransport.STDIO:
                return await self._execute_stdio(server, tool_name, arguments)
            else:
                return MCPResponse(
                    success=False,
                    error=f"Unsupported MCP transport: {server.transport}",
                )
        except asyncio.TimeoutError:
            return MCPResponse(
                success=False,
                error=f"MCP tool '{tool_name}' timed out after {MCP_TIMEOUT_SECONDS}s.",
            )
        except Exception as exc:
            logger.exception("MCP execute_tool error [%s]: %s", tool_name, exc)
            return MCPResponse(success=False, error=str(exc))

    # ------------------------------------------------------------------
    # HTTP JSON-RPC 2.0 transport
    # ------------------------------------------------------------------

    async def _discover_http_tools(self, server: MCPServerInfo) -> bool:
        """
        Call tools/list JSON-RPC method and register discovered tools.

        Args:
            server: HTTP MCP server configuration.

        Returns:
            True if discovery succeeded.
        """
        try:
            response = await self._http_jsonrpc(
                server,
                method="tools/list",
                params={},
            )
            tools_data = response.get("result", {}).get("tools", [])
            for tool_data in tools_data:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                )
                self.register_tool(server.id, tool)

            logger.info(
                "MCP HTTP discovery complete [%s]: %d tools",
                server.name,
                len(tools_data),
            )
            return True
        except Exception as exc:
            logger.error("MCP HTTP discovery failed [%s]: %s", server.name, exc)
            return False

    async def _execute_http(
        self,
        server: MCPServerInfo,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> MCPResponse:
        """Execute a tool call via HTTP JSON-RPC 2.0 POST."""
        raw = await self._http_jsonrpc(
            server,
            method="tools/call",
            params={"name": tool_name, "arguments": arguments},
        )

        if "error" in raw:
            return MCPResponse(
                success=False,
                error=raw["error"].get("message", str(raw["error"])),
            )

        return MCPResponse(success=True, result=raw.get("result", {}))

    async def _http_jsonrpc(
        self,
        server: MCPServerInfo,
        method: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC 2.0 request to an HTTP MCP server endpoint.

        Args:
            server: Target MCP server.
            method: JSON-RPC method name (e.g. 'tools/list').
            params: Method parameters dict.

        Returns:
            Parsed JSON response body as dict.
        """
        client = self._get_http_client(server)
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        headers = {"Content-Type": "application/json"}
        if server.api_key:
            headers["Authorization"] = f"Bearer {server.api_key}"

        resp = await asyncio.wait_for(
            client.post(server.url, json=payload, headers=headers),
            timeout=MCP_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()

    def _get_http_client(self, server: MCPServerInfo) -> httpx.AsyncClient:
        """Return or create a persistent httpx.AsyncClient for this server."""
        if server.id not in self._http_clients:
            self._http_clients[server.id] = httpx.AsyncClient(
                timeout=httpx.Timeout(MCP_TIMEOUT_SECONDS),
            )
        return self._http_clients[server.id]

    # ------------------------------------------------------------------
    # STDIO transport
    # ------------------------------------------------------------------

    async def _discover_stdio_tools(self, server: MCPServerInfo) -> bool:
        """Discover tools by sending tools/list over STDIO subprocess."""
        try:
            response = await self._stdio_jsonrpc(
                server,
                method="tools/list",
                params={},
            )
            tools_data = response.get("result", {}).get("tools", [])
            for tool_data in tools_data:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                )
                self.register_tool(server.id, tool)

            logger.info(
                "MCP STDIO discovery complete [%s]: %d tools",
                server.name,
                len(tools_data),
            )
            return True
        except Exception as exc:
            logger.error("MCP STDIO discovery failed [%s]: %s", server.name, exc)
            return False

    async def _execute_stdio(
        self,
        server: MCPServerInfo,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> MCPResponse:
        """Execute a tool call via STDIO subprocess JSON-RPC."""
        raw = await self._stdio_jsonrpc(
            server,
            method="tools/call",
            params={"name": tool_name, "arguments": arguments},
        )

        if "error" in raw:
            return MCPResponse(
                success=False,
                error=raw["error"].get("message", str(raw["error"])),
            )

        return MCPResponse(success=True, result=raw.get("result", {}))

    async def _stdio_jsonrpc(
        self,
        server: MCPServerInfo,
        method: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Launch MCP server as subprocess, send JSON-RPC via stdin, read from stdout.

        Args:
            server: STDIO MCP server config with server.command = ["npx", "mcp-server", ...]
            method: JSON-RPC method.
            params: Method parameters.

        Returns:
            Parsed JSON-RPC response.
        """
        command: list[str] = getattr(server, "command", [])
        if not command:
            raise ValueError(
                f"STDIO MCP server '{server.id}' has no 'command' configured."
            )

        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }) + "\n"

        proc = await asyncio.wait_for(
            asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            ),
            timeout=10.0,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=payload.encode()),
            timeout=MCP_TIMEOUT_SECONDS,
        )

        if proc.returncode != 0:
            raise RuntimeError(
                f"STDIO MCP server exited with code {proc.returncode}. "
                f"stderr: {stderr.decode()[:500]}"
            )

        return json.loads(stdout.decode().strip())
