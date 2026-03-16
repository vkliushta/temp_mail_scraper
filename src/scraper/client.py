"""Client for interacting with temp mail service"""

from playwright.async_api import TimeoutError

from src.app.settings import Config
from src.scraper.browser import browser_manager


class TempMailClient:

    async def open_page(self):

        browser = await browser_manager.get_browser()

        page = await browser.new_page()

        try:
            await page.goto(Config.TEMP_MAIL_URL, timeout=15000)
        except TimeoutError:
            await page.close()
            raise RuntimeError("Temp mail page timeout")

        return page

    async def get_email(self):

        page = await self.open_page()

        email = await page.locator("#eposta_adres").get_attribute("value")

        await page.close()

        return email

    async def refresh_email(self):

        page = await self.open_page()

        await page.click(".yoket-link")

        email = await page.locator("#eposta_adres").get_attribute("value")

        await page.close()

        return email