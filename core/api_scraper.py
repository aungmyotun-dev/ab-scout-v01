"""
AsianBookie API Scraper
Reads upcoming matches directly from the MessagePack API.
"""

from datetime import datetime

import msgpack

from config import BASE_URL

from utils.logger import get_logger

logger = get_logger(__name__)

from constants import *


class ApiScraper:

    def __init__(self, browser):
        self.browser = browser
        self.page = browser.page

    def scrape(self) -> list[dict]:

        logger.info("Capturing API responses...")

        upcoming_response, match_response = self._capture_response()

        logger.info("Decoding MessagePack...")

        upcoming_data = self._decode(upcoming_response)
        match_data = self._decode(match_response)

        logger.info("Upcoming rows : %d", len(upcoming_data))
        logger.info("Match rows    : %d", len(match_data))

        match_lookup = self._build_match_lookup(match_data)
        league_lookup = self._build_league_lookup(upcoming_data)

        return self._parse(
            upcoming_data,
            match_lookup,
            league_lookup,
        )

    def _decode(self, response):

        if response is None:
            raise RuntimeError("Missing API response.")

        return msgpack.unpackb(
            response.body(),
            raw=False,
        )

    def _capture_response(self):

        upcoming = None
        match_candidates = []

        def handler(response):

            nonlocal upcoming

            url = response.url

            if "/api/poll/upcoming" in url:
                upcoming = response
                return

            if "/api/poll/match?" in url:

                body = response.body()

                logger.info(
                    "MATCH API #%d : %d bytes",
                    len(match_candidates) + 1,
                    len(body),
                )

                match_candidates.append(
                    {
                        "response": response,
                        "url": url,
                        "size": len(body),
                    }
                )

        self.page.on("response", handler)

        try:
            self.browser.open(BASE_URL)
            self.page.wait_for_timeout(5000)

        finally:
            self.page.remove_listener("response", handler)

        if upcoming is None:
            raise RuntimeError("Upcoming API was not captured.")

        if not match_candidates:
            raise RuntimeError("Match API was not captured.")

        logger.info(
            "Captured %d Match API responses.",
            len(match_candidates),
        )

        for i, item in enumerate(match_candidates, start=1):
            logger.info(
                "Candidate %d : %d bytes : %s",
                i,
                item["size"],
                item["url"],
            )

        #
        # Temporary deterministic selection.
        #
        match = match_candidates[0]["response"]

        logger.info(
            "Selected Match API : Candidate #1",
        )

        return upcoming, match

    def _build_match_lookup(self, match_data):

        lookup = {}
        seen_hashes = set()

        for row in match_data:

            if not isinstance(row, list):
                continue

            if len(row) < 32:
                continue

            match_hash = row[1]

            if not isinstance(match_hash, str):
                continue

            if match_hash in seen_hashes:
                continue

            seen_hashes.add(match_hash)
            lookup[match_hash] = row

        logger.info(
            "Match lookup : %d",
            len(lookup),
        )

        return lookup

    def _build_league_lookup(self, upcoming_data):

        lookup = {}

        for row in upcoming_data:

            if not isinstance(row, list):
                continue

            if len(row) < 4:
                continue

            code = row[1]

            if not isinstance(code, str):
                continue

            if not code.endswith("odds"):
                continue

            lookup[code] = {
                "league": row[2],
                "country": row[3],
            }

        logger.info(
            "League map : %d",
            len(lookup),
        )

        return lookup

    def _parse(
        self,
        upcoming_data,
        match_lookup,
        league_lookup,
    ) -> list[dict]:

        matches = []

        current_league = ""
        current_country = ""

        for row in upcoming_data:

            # League section
            if self._is_league_row(row):

                current_league, current_country = (
                    self._update_current_league(
                        row,
                        league_lookup,
                    )
                )

                continue

            # Match section
            if not self._is_match_row(row):
                continue

            match_row = self._get_match_row(
                row,
                match_lookup,
            )

            if match_row is None:
                continue

            matches.append(
                self._parse_match(
                    row,
                    match_row,
                    current_league,
                    current_country,
                )
            )

        logger.info(
            "Collected %d API matches.",
            len(matches),
        )

        return matches

    def _is_league_row(self, row):

        if not isinstance(row, list):
            return False

        if len(row) != 2:
            return False

        if row[0] != "_s":
            return False

        if not isinstance(row[1], str):
            return False

        return row[1].startswith("MATCHES_")

    def _update_current_league(
        self,
        row,
        league_lookup,
    ):

        code = row[1].replace(
            "MATCHES_",
            "",
        )

        info = league_lookup.get(code)

        if info is None:
            return "", ""

        return (
            info["league"],
            info["country"],
        )

    def _is_match_row(self, row):

        if not isinstance(row, list):
            return False

        if len(row) < 50:
            return False

        if not isinstance(row[UP_MATCH_HASH], str):
            return False

        if len(row[UP_MATCH_HASH]) != 32:
            return False

        if not isinstance(row[UP_HOME_TEAM], str):
            return False

        if not isinstance(row[UP_AWAY_TEAM], str):
            return False

        return True

    def _get_match_row(
        self,
        upcoming_row,
        match_lookup,
    ):

        return match_lookup.get(
            upcoming_row[UP_MATCH_HASH]
        )

    def _format_timestamp(
        self,
        timestamp: int,
        fmt: str,
    ) -> str:

        return datetime.fromtimestamp(
            timestamp / 1000
        ).strftime(fmt)

    def _parse_match(
        self,
        upcoming,
        match,
        league,
        country,
    ) -> dict:

        return {

            # ---------------------------------
            # Identity
            # ---------------------------------

            "match_id": match[MT_MATCH_ID],
            "match_hash": upcoming[UP_MATCH_HASH],

            # ---------------------------------
            # Competition
            # ---------------------------------

            "league": league,
            "country": country,

            # ---------------------------------
            # Date / Time
            # ---------------------------------

            "match_date": self._format_timestamp(
                upcoming[UP_MATCH_DATE],
                "%d %b %Y",
            ),

            "match_time": self._format_timestamp(
                upcoming[UP_MATCH_TIME],
                "%d %b %H:%M",
            ),

            # ---------------------------------
            # Teams
            # ---------------------------------

            "home_team_id": upcoming[UP_HOME_TEAM_ID],
            "away_team_id": upcoming[UP_AWAY_TEAM_ID],

            "home_team": upcoming[UP_HOME_TEAM],
            "away_team": upcoming[UP_AWAY_TEAM],

            # ---------------------------------
            # Status
            # ---------------------------------

            "status": match[MT_STATUS],

            # ---------------------------------
            # Asian Handicap
            # ---------------------------------

            "ah_line": match[MT_AH_LINE],
            "home_ah": match[MT_HOME_AH],
            "away_ah": match[MT_AWAY_AH],

            # ---------------------------------
            # Over / Under
            # ---------------------------------

            "ou_line": match[MT_OU_LINE],
            "over": match[MT_OVER],
            "under": match[MT_UNDER_OPEN],

            # ---------------------------------
            # 1X2
            # ---------------------------------

            "home_1x2": match[MT_HOME_1X2],
            "draw": match[MT_DRAW],
            "away_1x2": match[MT_AWAY_1X2],

            # ---------------------------------
            # URL
            # ---------------------------------

            "detail_path": upcoming[UP_DETAIL_PATH],
        }

    def _should_keep_match(
        self,
        upcoming_row,
        match_row,
    ) -> bool:
        """
        Decide whether this match belongs on the AB Today Board.

        Business rules live ONLY in this function.
        """

        return True
