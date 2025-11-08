import logging
import time

from mrlazy_bot.logging_config import configure_json_logging
from mrlazy_bot.local_poller.allowlist import CommandAllowlist
from mrlazy_bot.local_poller.sqs_worker import SqsWorker
from mrlazy_bot.local_poller.slack_client import SlackMessenger
from mrlazy_bot import settings


def main() -> None:
    configure_json_logging()
    logger = logging.getLogger("poller")
    if not settings.SQS_QUEUE_URL:
        logger.error("SQS_QUEUE_URL is not set")
        return
    if not settings.SLACK_BOT_TOKEN:
        logger.error("SLACK_BOT_TOKEN is not set")
        return
    allowlist = CommandAllowlist.load_from_yaml(settings.COMMANDS_ALLOWLIST_PATH)
    slack = SlackMessenger(settings.SLACK_BOT_TOKEN)
    worker = SqsWorker(allowlist, slack)
    logger.info("Starting poll loop", extra={"queue": settings.SQS_QUEUE_URL})
    while True:
        worker.receive_and_process_once()
        # brief pause to allow CTRL+C responsiveness between long polls
        time.sleep(0.2)


if __name__ == "__main__":
    main()


