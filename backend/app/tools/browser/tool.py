from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .manager import BrowserManager
from .page import PageActions
from .screenshots import ScreenshotService
from .models import BrowserRequest


class BrowserTool(BaseTool):

    name = "browser"

    description = "Interact with web pages using Playwright."

    def __init__(self):

        self.manager = BrowserManager()

    async def execute(

        self,

        **kwargs,

    ):

        request = BrowserRequest(**kwargs)

        await self.manager.start()

        page = PageActions(

            self.manager.page

        )

        screenshots = ScreenshotService(

            self.manager.page

        )

        try:

            if request.action == "open":

                await page.open(request.url)

                result = ToolResult(

                    success=True,

                    output="Page opened.",

                )

            elif request.action == "content":

                html = await page.content()

                result = ToolResult(

                    success=True,

                    output=html,

                )

            elif request.action == "screenshot":

                await screenshots.save(

                    request.path,

                )

                result = ToolResult(

                    success=True,

                    output=request.path,

                )

            else:

                raise NotImplementedError(
                    request.action
                )

        finally:

            await self.manager.stop()

        return result