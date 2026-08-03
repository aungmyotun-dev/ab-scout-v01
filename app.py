"""
AB Scout V1

Temporary API Debug

Run:
    python app.py
"""

from pathlib import Path

import pandas as pd

from config import CSV_NAME, OUTPUT_DIR
from core.api_scraper import ApiScraper
from core.browser import BrowserManager
from core.telegram import TelegramNotifier
from utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:

    browser = BrowserManager()

    try:

        browser.start()

        scraper = ApiScraper(browser)

        matches = scraper.scrape()

        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        csv_path = output_dir / CSV_NAME

        df = pd.DataFrame(
            matches,
            columns=[
                "match_id",
                "match_hash",

                "league",
                "country",

                "match_date",
                "match_time",

                "home_team_id",
                "away_team_id",

                "home_team",
                "away_team",

                "status",

                "ah_line",
                "home_ah",
                "away_ah",

                "ou_line",
                "over",
                "under",

                "home_1x2",
                "draw",
                "away_1x2",

                "detail_path",
            ],
        )

        df.to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig",
        )

        logger.info(
            "Saved %d matches.",
            len(df),
        )

        logger.info(
            "CSV: %s",
            csv_path,
        )

        notifier = TelegramNotifier()

        logger.info("Telegram enabled: %s", notifier.enabled())
        logger.info("Telegram token exists: %s", bool(notifier.token))
        logger.info("Telegram chat id: %s", notifier.chat_id)

        if notifier.enabled():

            notifier.send_message(
                "\n".join(
                    [
                        "🤖 AB Scout Completed",
                        "",
                        f"✅ Matches : {len(df)}",
                        "",
                        "📎 CSV attached.",
                    ]
                )
            )

            notifier.send_document(
                str(csv_path),
                caption="AB Scout CSV",
            )


    finally:

        browser.stop()


if __name__ == "__main__":
    main()