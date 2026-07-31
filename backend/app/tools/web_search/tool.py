from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .provider import BaseSearchProvider
from .ranker import ResultRanker
from .cache import SearchCache
from .models import SearchRequest


class WebSearchTool(BaseTool):

    name = "web_search"

    description = "Search technical resources."

    def __init__(

        self,

        provider: BaseSearchProvider,

    ):

        self.provider = provider

        self.ranker = ResultRanker()

        self.cache = SearchCache()

    async def execute(

        self,

        **kwargs,

    ):

        request = SearchRequest(**kwargs)

        key = request.model_dump_json()

        cached = self.cache.get(key)

        if cached:

            return ToolResult(

                success=True,

                output=cached.model_dump_json(),

            )

        response = await self.provider.search(
            request
        )

        response.results = self.ranker.rank(
            response.results
        )

        self.cache.put(
            key,
            response,
        )

        return ToolResult(

            success=True,

            output=response.model_dump_json(),

        )