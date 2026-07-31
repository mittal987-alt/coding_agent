class PageActions:

    def __init__(self, page):

        self.page = page

    async def open(self, url):

        await self.page.goto(url)

    async def click(self, selector):

        await self.page.click(selector)

    async def fill(

        self,

        selector,

        text,

    ):

        await self.page.fill(

            selector,

            text,

        )

    async def content(self):

        return await self.page.content()