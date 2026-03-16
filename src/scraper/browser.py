"""Browser manager for handling Playwright browser instances"""

from playwright.async_api import async_playwright


class BrowserManager:

    _browser = None
    _playwright = None

    async def get_browser(self):

        if self._browser is None:

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True
            )

        return self._browser


browser_manager = BrowserManager()
