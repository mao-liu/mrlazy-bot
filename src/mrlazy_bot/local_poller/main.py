import asyncio
import logging
import threading
from typing import Any, Dict

from mrlazy_bot.logging_config import configure_json_logging
from mrlazy_bot.local_poller.allowlist import CommandAllowlist
from mrlazy_bot.local_poller.sqs_worker import SqsWorker
from mrlazy_bot.local_poller.slack_client import SlackMessenger
from mrlazy_bot import settings

logger = logging.getLogger(__name__)


async def async_main() -> None:
    if not settings.SQS_QUEUE_URL:
        logger.error("SQS_QUEUE_URL is not set")
        return
    if not settings.SLACK_BOT_TOKEN:
        logger.error("SLACK_BOT_TOKEN is not set")
        return

    allowlist = CommandAllowlist.load_from_yaml(settings.COMMANDS_ALLOWLIST_PATH)
    slack = SlackMessenger(settings.SLACK_BOT_TOKEN)
    sqs_worker = SqsWorker(allowlist, slack)
    logger.info(
        "Starting async poller",
        extra={"queue": settings.SQS_QUEUE_URL},
    )

    loop = asyncio.get_running_loop()
    task_slots: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue(maxsize=settings.MAX_CONCURRENT_COMMANDS)

    with sqs_worker.run_poller(loop, task_slots):
        worker_loops = [
            asyncio.create_task(sqs_worker.worker_loop(task_slots))
            for _ in range(settings.MAX_CONCURRENT_COMMANDS)
        ]
        logger.info(
            "Async workers started",
            extra={
                "concurrency": settings.MAX_CONCURRENT_COMMANDS,
                "long_poll_secs": settings.SQS_LONG_POLL_SECS,
            },
        )
        try:
            await asyncio.gather(*worker_loops)
        except asyncio.CancelledError:
            pass


def main() -> None:
    # Preserve external entrypoint that expects a sync function
    asyncio.run(async_main())


if __name__ == "__main__":
    main()