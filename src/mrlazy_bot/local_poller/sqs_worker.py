import asyncio
from contextlib import contextmanager
import logging
import threading
from typing import Any, Dict, Generator, Coroutine

import boto3

from mrlazy_bot import settings
from mrlazy_bot.local_poller.allowlist import CommandAllowlist
from mrlazy_bot.local_poller.command_runner import (
    run_allowed_command_async,
)
from mrlazy_bot.local_poller.slack_client import SlackMessenger
from mrlazy_bot.models import SqsJob, CommandExecutionError


logger = logging.getLogger(__name__)

class SqsWorker:
    def __init__(self, allowlist: CommandAllowlist, slack: SlackMessenger):
        self.slack_service = slack
        self.command_service = allowlist
        self.sqs_client = boto3.client("sqs", region_name=settings.AWS_REGION)
        self._queue_url = settings.SQS_QUEUE_URL or ""
        self._poller_stop_event = threading.Event()

    def _poller_thread(self, loop: asyncio.AbstractEventLoop, task_slots: "asyncio.Queue[Dict[str, Any]]") -> None:
        logger.info("SQS fetcher thread started")
        while not self._poller_stop_event.is_set():
            try:
                logger.info("SQS fetcher thread polling for messages")
                resp = self.sqs_client.receive_message(
                    QueueUrl=self._queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=settings.SQS_LONG_POLL_SECS,
                )
                messages = resp.get("Messages") or []
                for msg in messages:
                    logger.info("SQS fetcher thread received message", extra={"message": msg})
                    sync_await(task_slots.put(msg), loop)
            except Exception as e:
                logger.exception("SQS receive failed")
                # brief backoff
                self._poller_stop_event.wait(1.0)
        logger.info("SQS fetcher thread exiting")

    @contextmanager
    def run_poller(self, loop: asyncio.AbstractEventLoop, task_slots: "asyncio.Queue[Dict[str, Any]]") -> Generator[threading.Thread, None, None]:
        try:
            poller_thread = threading.Thread(
                target=self._poller_thread,
                args=(loop, task_slots),
                daemon=True,
                name="sqs-fetcher",
            )
            poller_thread.start()
            yield poller_thread
        finally:
            self._poller_stop_event.set()
            poller_thread.join(timeout=2.0)

    async def worker_loop(self, task_slots: "asyncio.Queue[Dict[str, Any]]") -> None:
        while True:
            msg = await task_slots.get()
            try:
                job = SqsJob.from_sqs_message(msg)

                allowed_command = self.command_service.get(job.command)
                if not allowed_command:
                    logger.warning("Command is not allowed", extra={"command": job.command})
                    # Do not post to slack, as that could become a DOS vector
                    continue

                self.slack_service.post_job_update(job, f"Started '{job.command}' with args: {' '.join(job.args)}")

                result = await run_allowed_command_async(allowed_command, job.args)

                self.slack_service.post_job_update(job, f"Completed '{job.command}' successfully, output: {result.stdout}")

                self.sqs_client.delete_message(QueueUrl=self._queue_url, ReceiptHandle=msg["ReceiptHandle"])

            except Exception as e:
                logger.exception(f"Command '{job.command}' execution failed")
                if isinstance(e, CommandExecutionError):
                    message = f"Error executing '{job.command}'\nstdout: {e.command_execution_result.stdout}\nstderr: {e.command_execution_result.stderr}"
                elif isinstance(e, asyncio.TimeoutError):
                    message = f"Error executing '{job.command}': timed out"
                else:
                    message = f"Unknown error executing '{job.command}': {e}"
                self.slack_service.post_job_update(job, message)

                # suppress the error, allow the message to retry via SQS visibility timeout expiry
                pass

            finally:
                # always mark the task as done, retry attempts will be handled by SQS visibility timeout expiry
                task_slots.task_done()



def sync_await(coro: Coroutine[Any, Any, Any], loop: asyncio.AbstractEventLoop) -> Any:
    """
    Run a coroutine on the given event loop, and block until it completes.
    """
    fut = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result()

