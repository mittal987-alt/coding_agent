from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from pydantic import BaseModel


class ToolResult(BaseModel):

    success: bool

    output: str

    metadata: dict = {}


class BaseTool(ABC):

    name: str

    description: str

    @abstractmethod
    async def execute(

        self,

        **kwargs,

    ) -> ToolResult:

        ...