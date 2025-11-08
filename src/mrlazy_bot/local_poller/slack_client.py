import logging
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from mrlazy_bot.logging_config import configure_json_logging


logger = logging.getLogger("slack")


class SlackMessenger:
    def __init__(self, bot_token: str):
        self._client = WebClient(token=bot_token)

    def post_thread_message(
        self,
        channel: str,
        thread_ts: str,
        text: str,
    ) -> Optional[str]:
        try:
            resp = self._client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
            return resp.get("ts")
        except SlackApiError as e:
            logger.error("Failed to post Slack message", extra={"error": str(e)})
            return None


