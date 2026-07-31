from __future__ import annotations

import logging
import platform
import time
from dataclasses import dataclass, field
from typing import Any

from app.bootstrap.container import ServiceContainer

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------

@dataclass
class HealthStatus:
    name: str
    healthy: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    healthy: bool
    timestamp: float
    uptime: float
    services: list[HealthStatus] = field(default_factory=list)


# ----------------------------------------------------------------
# HealthManager
# ----------------------------------------------------------------

class HealthManager:
    """
    Collects health information from all registered services.
    """

    def __init__(self, container: ServiceContainer) -> None:
        self.container = container
        self.started_at = time.time()

    async def check(self) -> HealthReport:

        services: list[HealthStatus] = []

        services.append(await self._llm_health())
        services.append(await self._memory_health())
        services.append(await self._workspace_health())
        services.append(await self._tool_health())
        services.append(self._system_health())

        healthy = all(s.healthy for s in services)

        return HealthReport(
            healthy=healthy,
            timestamp=time.time(),
            uptime=time.time() - self.started_at,
            services=services,
        )

    async def json(self) -> dict[str, Any]:

        report = await self.check()

        return {
            "healthy": report.healthy,
            "timestamp": report.timestamp,
            "uptime": report.uptime,
            "services": [
                {
                    "name": service.name,
                    "healthy": service.healthy,
                    "message": service.message,
                    "details": service.details,
                }
                for service in report.services
            ],
        }

    async def _llm_health(self) -> HealthStatus:

        if not self.container.exists("llm_registry"):
            return HealthStatus(name="llm", healthy=False, message="Registry not found")

        registry = self.container.resolve("llm_registry")

        if hasattr(registry, "health"):
            providers = await registry.health()
            return HealthStatus(
                name="llm",
                healthy=all(providers.values()) if providers else True,
                details=providers,
            )

        return HealthStatus(name="llm", healthy=True)

    async def _memory_health(self) -> HealthStatus:

        if not self.container.exists("memory"):
            return HealthStatus(name="memory", healthy=True, message="Not configured")

        memory = self.container.resolve("memory")

        if hasattr(memory, "health_check"):
            ok = await memory.health_check()
            return HealthStatus(name="memory", healthy=ok)

        return HealthStatus(name="memory", healthy=True)

    async def _workspace_health(self) -> HealthStatus:

        if not self.container.exists("workspace"):
            return HealthStatus(name="workspace", healthy=True, message="Not configured")

        workspace = self.container.resolve("workspace")

        if hasattr(workspace, "health_check"):
            ok = await workspace.health_check()
            return HealthStatus(name="workspace", healthy=ok)

        return HealthStatus(name="workspace", healthy=True)

    async def _tool_health(self) -> HealthStatus:

        if not self.container.exists("tool_registry"):
            return HealthStatus(name="tools", healthy=True, message="Not configured")

        registry = self.container.resolve("tool_registry")

        if hasattr(registry, "health_check"):
            ok = await registry.health_check()
            return HealthStatus(name="tools", healthy=ok)

        return HealthStatus(name="tools", healthy=True)

    def _system_health(self) -> HealthStatus:

        return HealthStatus(
            name="system",
            healthy=True,
            details={
                "python": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
            },
        )