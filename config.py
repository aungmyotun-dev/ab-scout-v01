"""
Application configuration.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import os

BASE_URL = "https://beta.asianbookie.net/en/upcoming"

DETAIL_BASE = (
    "https://beta.asianbookie.net/en/matches/odds/"
)

HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

SLOW_MO = 100

TIMEOUT = 30000

OUTPUT_DIR = "output"

CSV_NAME = (
    f"asianbookie_matches_"
    f"{datetime.now(ZoneInfo('Asia/Yangon')).strftime('%Y-%m-%d-%H-%M')}.csv"
)

# ------------------------
# Telegram
# ------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")