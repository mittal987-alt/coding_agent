from app.tools.registry import ToolRegistry


class ToolDispatcher:

    def __init__(

        self,

        registry: ToolRegistry,

    ):

        self.registry = registry

    def dispatch(

        self,

        tool_name: str,

    ):

        tool = self.registry.get(tool_name)

        if tool is None:

            raise ValueError(

                f"Unknown tool: {tool_name}"

            )

        return tool