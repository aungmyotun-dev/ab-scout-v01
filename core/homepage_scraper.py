from playwright.sync_api import Locator

from utils.logger import get_logger

logger = get_logger(__name__)


class MatchScraper:

    def __init__(self, browser):

        self.browser = browser
        self.page = browser.page

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _clean(lines: list[str]) -> list[str]:

        output = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            output.append(line)

        return output

    # --------------------------------------------------

    @staticmethod
    def _is_league_header(text: str) -> bool:

        lines = [
            x.strip()
            for x in text.splitlines()
            if x.strip()
        ]

        if len(lines) != 2:
            return False

        return True

    # --------------------------------------------------

    @staticmethod
    def _parse_match(lines: list[str]) -> dict:

        row = {
            "league": "",
            "country": "",

            "match_time": "",

            "home_team": "",
            "away_team": "",

            "ah_line": "",
            "home_ah_odds": "",
            "away_ah_odds": "",

            "ou_line": "",
            "over_odds": "",
            "under_odds": "",

            "home_1x2": "",
            "draw_odds": "",
            "away_1x2": "",
        }

        if len(lines) < 20:
            return row

        row["match_time"] = lines[0]

        row["home_team"] = lines[1]
        row["away_team"] = lines[2]

        # -------------------------
        # AH
        # -------------------------

        try:

            ah = lines.index("AH")

            row["ah_line"] = lines[ah + 1]

            row["home_ah_odds"] = lines[ah + 2]

            row["away_ah_odds"] = lines[ah + 4]

        except Exception:
            pass

        # -------------------------
        # O/U
        # -------------------------

        try:

            ou = lines.index("O/U")

            row["ou_line"] = (
                lines[ou + 1]
                .replace("o", "")
                .replace("O", "")
                .strip()
            )

            row["over_odds"] = lines[ou + 2]

            row["under_odds"] = lines[ou + 4]

        except Exception:
            pass

        # -------------------------
        # 1X2
        # -------------------------

        try:

            one = lines.index("1")

            row["home_1x2"] = lines[one + 1]

            x = lines.index("X")

            row["draw_odds"] = lines[x + 1]

            two = lines.index("2")

            row["away_1x2"] = lines[two + 1]

        except Exception:
            pass

        return row

    # --------------------------------------------------
    # Main Scraper
    # --------------------------------------------------

    def scrape(self) -> list[dict]:
        print("Title:", self.page.title())
        print(
            "cards:",
            self.page.locator(".gradient-border").count()
        )

        self.page.wait_for_selector(
            ".gradient-border",
            timeout=15000,
        )

        self.page.wait_for_timeout(3000)

        cards: Locator = self.page.locator(
            ".gradient-border"
        )

        logger.info(
            "Found %d cards.",
            cards.count(),
        )

        results = []

        current_league = ""
        current_country = ""

        for i in range(cards.count()):

            try:

                text = cards.nth(i).inner_text()

            except Exception:

                continue

            lines = self._clean(
                text.splitlines()
            )

            if not lines:
                continue

            print("=" * 60)
            print(f"CARD {i}")
            print(text[:500])
            if i >= 15:
                break


            # ------------------------------------
            # League Header
            # ------------------------------------

            if self._is_league_header(text):

                current_league = lines[0]
                current_country = lines[1]

                continue

            # ------------------------------------
            # Ignore empty cards
            # ------------------------------------

            if "Details >" not in text:
                continue

            row = self._parse_match(lines)

            row["league"] = current_league
            row["country"] = current_country

            if (
                row["home_team"]
                and row["away_team"]
            ):
                results.append(row)

        logger.info(
            "Collected %d matches.",
            len(results),
        )

        return results