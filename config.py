"""
Application configuration.
"""

BASE_URL = "https://beta.asianbookie.net/en/upcoming"

DETAIL_BASE = (
    "https://beta.asianbookie.net/en/matches/odds/"
)

import os
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

SLOW_MO = 100

TIMEOUT = 30000

OUTPUT_DIR = "output"

CSV_NAME = "asianbookie_matches.csv"

# ------------------------
# Telegram
# ------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")