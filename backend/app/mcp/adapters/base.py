from abc import ABC, abstractmethod

from app.tools.base import BaseTool


class BaseMCPAdapter(BaseTool, ABC):

    @abstractmethod
    async def execute(
        self,
        **kwargs,
    ):
        ...