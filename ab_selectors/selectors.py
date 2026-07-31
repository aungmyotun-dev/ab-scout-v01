"""
Central selector registry for the AB Scout scraper.

Selectors only.
No Playwright logic.
"""


class MatchSelectors:
    """Today's match list selectors."""

    # Root
    MATCH_SECTION = "#today-matches"

    # One match card
    MATCH_CARD = ".gradient-border"

    # Match information
    MATCH_TIME = (
        "p.text-xs.font-semibold.uppercase.whitespace-nowrap"
    )

    TEAM_NAME = "span.truncate"

    # Odds
    ODDS_SWIPER = ".swiper"

    ODDS_SLIDE = ".swiper-slide"

    MARKET_TITLE = "p.text-xs.font-semibold.uppercase"

    LINE = "p.text-xs.font-normal.leading-none"

    ODDS = (
        "p.text-xs.font-semibold.line-height, "
        "p.text-xs.font-semibold.leading-4"
    )