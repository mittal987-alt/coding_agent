from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SandboxType = Literal[
    "docker",
    "firejail",
    "subprocess",
    "none",
]

PermissionMode = Literal[
    "allow_all",
    "deny_all",
    "whitelist",
]

ToolProtocol = Literal[
    "internal",
    "mcp",
    "http",
]

@dataclass(slots=True)
class ToolExecutionConfig:
    """
    Tool execution settings.
    """

    timeout: int = 120

    max_concurrent: int = 5

    retry_attempts: int = 2

    capture_stdout: bool = True

    capture_stderr: bool = True

    cleanup_after_execution: bool = True

@dataclass(slots=True)
class SandboxConfig:
    """
    Sandboxed tool execution.
    """

    enabled: bool = True

    sandbox_type: SandboxType = "docker"

    memory_limit_mb: int = 2048

    cpu_limit: float = 2.0

    network_enabled: bool = False

    filesystem_read_only: bool = False

@dataclass(slots=True)
class PermissionConfig:
    """
    Tool permissions.
    """

    mode: PermissionMode = "whitelist"

    allowed_tools: list[str] = field(
        default_factory=list,
    )

    blocked_tools: list[str] = field(
        default_factory=list,
    )

    require_confirmation: bool = False

@dataclass(slots=True)
class MCPConfig:
    """
    Model Context Protocol settings.
    """

    enabled: bool = True

    auto_discover: bool = True

    discovery_interval: int = 300

    connection_timeout: int = 30

    reconnect: bool = True

@dataclass(slots=True)
class ToolDiscoveryConfig:
    """
    Automatic tool discovery.
    """

    enabled: bool = True

    scan_internal_tools: bool = True

    scan_mcp_servers: bool = True

    refresh_interval: int = 300

@dataclass(slots=True)
class ToolRegistryConfig:
    """
    Tool registry settings.
    """

    auto_register: bool = True

    validate_on_register: bool = True

    enable_categories: bool = True

    enable_search: bool = True

@dataclass(slots=True)
class ToolConfig:
    """
    Complete tool configuration.
    """

    execution: ToolExecutionConfig = field(
        default_factory=ToolExecutionConfig,
    )

    sandbox: SandboxConfig = field(
        default_factory=SandboxConfig,
    )

    permissions: PermissionConfig = field(
        default_factory=PermissionConfig,
    )

    mcp: MCPConfig = field(
        default_factory=MCPConfig,
    )

    discovery: ToolDiscoveryConfig = field(
        default_factory=ToolDiscoveryConfig,
    )

    registry: ToolRegistryConfig = field(
        default_factory=ToolRegistryConfig,
    )

def create_tool_config() -> ToolConfig:
    """
    Create the default tool configuration.
    """
    return ToolConfig()

config = create_tool_config()

print(config.execution.timeout)

print(config.sandbox.sandbox_type)

print(config.permissions.mode)

print(config.mcp.enabled)
