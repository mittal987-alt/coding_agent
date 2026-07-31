class ScreenshotService:

    def __init__(self, page):

        self.page = page

    async def save(

        self,

        path,

    ):

        await self.page.screenshot(

            path=path,

            full_page=True,

        )