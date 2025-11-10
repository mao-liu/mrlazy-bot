import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from mrlazy_bot import settings
from mrlazy_bot.models import SqsJob


logger = logging.getLogger("slack")


class SlackMessenger:
    def __init__(self, bot_token: str):
        self._client = WebClient(token=bot_token)

    def _post_thread_message(
        self,
        channel: str,
        thread_ts: str,
        text: str,
    ) -> str | None:
        if len(text) > settings.OUTPUT_MAX_CHARS:
            text = text[:settings.OUTPUT_MAX_CHARS] + "..."

        try:
            resp = self._client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
            return resp.get("ts")
        except SlackApiError as e:
            logger.error("Failed to post Slack message", extra={"error": str(e)})
            return None

    def post_job_update(self, job: SqsJob, text: str) -> str | None:
        if len(text) > settings.OUTPUT_MAX_CHARS:
            text = text[:settings.OUTPUT_MAX_CHARS] + "..."

        return self._post_thread_message(job.channel, job.thread_ts or job.event_ts, text)


