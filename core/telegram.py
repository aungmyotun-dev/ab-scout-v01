"""
Telegram notification helper.
"""

from pathlib import Path

import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

from utils.logger import get_logger

logger = get_logger(__name__)


class TelegramNotifier:

    def __init__(self):

        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def enabled(self) -> bool:

        return bool(
            self.token and
            self.chat_id
        )

    def send_message(
        self,
        text: str,
    ) -> None:

        if not self.enabled():
            logger.warning(
                "Telegram is not configured."
            )
            return

        url = (
            f"https://api.telegram.org/bot"
            f"{self.token}/sendMessage"
        )

        response = requests.post(
            url,
            data={
                "chat_id": self.chat_id,
                "text": text,
            },
            timeout=30,
        )

        response.raise_for_status()

    def send_document(
        self,
        file_path: str,
        caption: str = "",
    ) -> None:

        if not self.enabled():
            logger.warning(
                "Telegram is not configured."
            )
            return

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(path)

        url = (
            f"https://api.telegram.org/bot"
            f"{self.token}/sendDocument"
        )

        with path.open("rb") as f:

            response = requests.post(
                url,
                data={
                    "chat_id": self.chat_id,
                    "caption": caption,
                },
                files={
                    "document": f,
                },
                timeout=60,
            )

        response.raise_for_status()

        logger.info(
            "Telegram notification sent."
        )