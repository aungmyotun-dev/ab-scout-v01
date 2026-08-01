"""
Browser manager.

Owns only the Playwright lifecycle.
"""

from playwright.sync_api import sync_playwright

from config import HEADLESS, SLOW_MO, TIMEOUT
from utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self) -> None:
        if self.page is not None:
            return
        
        logger.info("Starting browser...")

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO,
        )

        self.context = self.browser.new_context()

        self.page = self.context.new_page()

        self.page.set_default_timeout(TIMEOUT)

        logger.info("Browser started.")

    def open(self, url: str) -> None:

        logger.info("Opening %s", url)

        self.page.goto(
            url,
            wait_until="load",
        )

        # Allow SPA to finish bootstrapping
        self.page.wait_for_timeout(8000)

        current_url = self.page.url
        title = self.page.title()

        logger.info("Current URL: %s", current_url)
        logger.info("Page title: %s", title)

        #
        # Detect Cloudflare / challenge pages.
        #
        if title.strip().lower() == "just a moment...".lower():

            screenshot = "output/cloudflare_blocked.png"
            html = "output/cloudflare_blocked.html"

            self.page.screenshot(
                path=screenshot,
                full_page=True,
            )

            with open(html, "w", encoding="utf-8") as f:
                f.write(self.page.content())

            raise RuntimeError(
                f"Blocked by Cloudflare. "
                f"Screenshot: {screenshot}, HTML: {html}"
            )
        
    def stop(self) -> None:
        logger.info("Closing browser...")

        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

        logger.info("Browser closed.")

    def get_cookies(self) -> dict:

        cookies = self.context.cookies()

        return {
        c["name"]: c["value"]
            for c in cookies
        }