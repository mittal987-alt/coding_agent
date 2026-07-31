from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .models import DocumentationRequest
from .retriever import DocumentationRetriever


class DocumentationTool(BaseTool):

    name = "documentation"

    description = "Retrieve official technical documentation."

    def __init__(

        self,

        registry,

    ):

        self.registry = registry

        self.retriever = DocumentationRetriever()

    async def execute(

        self,

        **kwargs,

    ):

        request = DocumentationRequest(

            **kwargs

        )

        provider = self.registry.get(

            request.provider

        )

        docs = await self.retriever.retrieve(

            provider,

            request.query,

        )

        return ToolResult(

            success=True,

            output=docs.model_dump_json(),

        )