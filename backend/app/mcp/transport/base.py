from __future__ import annotations

from abc import ABC, abstractmethod

from app.mcp.models import (
    MCPRequest,
    MCPResponse,
)


class BaseTransport(ABC):

    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def disconnect(self):
        ...

    @abstractmethod
    async def send(
        self,
        request: MCPRequest,
    ) -> MCPResponse:
        ...