"""
AsianBookie Detail Scraper
"""

import msgpack

from utils.logger import get_logger

logger = get_logger(__name__)


class DetailScraper:

    def __init__(self, browser):

        self.browser = browser
        self.page = browser.page

    def scrape(self, url):

        response = self._capture(url)

        return msgpack.unpackb(
            response.body(),
            raw=False,
        )

    def _capture(self, url):

        with self.page.expect_response(
            lambda r: "/api/poll/home-match-detail" in r.url
        ) as resp:

            self.browser.open(url)

        response = resp.value

        logger.info(
            "Captured DETAIL : %s",
            response.url,
        )

        return response