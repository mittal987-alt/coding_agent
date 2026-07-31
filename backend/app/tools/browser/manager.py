from playwright.async_api import async_playwright


class BrowserManager:

    def __init__(self):

        self.playwright = None

        self.browser = None

        self.page = None

    async def start(self):

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True
        )

        self.page = await self.browser.new_page()

    async def stop(self):

        await self.browser.close()

        await self.playwright.stop()