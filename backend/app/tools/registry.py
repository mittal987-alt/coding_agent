from __future__ import annotations

from app.tools.base import BaseTool


class ToolRegistry:

    def __init__(self):

        self.tools = {}

    def register(

        self,

        tool: BaseTool,

    ):

        self.tools[tool.name] = tool

    def get(

        self,

        name: str,

    ):

        return self.tools.get(name)

    def all(self):

        return list(

            self.tools.values()

        )