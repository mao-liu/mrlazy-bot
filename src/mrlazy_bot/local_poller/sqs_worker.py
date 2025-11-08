import json
import logging
import os
import threading
import time
from typing import Any, Dict, Optional

import boto3

from mrlazy_bot.models import SqsJob
from mrlazy_bot.local_poller.allowlist import CommandAllowlist
from mrlazy_bot.local_poller.command_runner import CommandExecutionError, run_allowed_command
from mrlazy_bot.local_poller.slack_client import SlackMessenger
from mrlazy_bot import settings


logger = logging.getLogger("sqs_worker")


class VisibilityExtender(threading.Thread):
    def __init__(self, sqs_client, queue_url: str, receipt_handle: str, interval: int, visibility: int):
        super().__init__(daemon=True)
        self._sqs = sqs_client
        self._queue_url = queue_url
        self._receipt_handle = receipt_handle
        self._interval = interval
        self._visibility = visibility
        self._stopped = threading.Event()

    def run(self) -> None:
        while not self._stopped.wait(self._interval):
            try:
                self._sqs.change_message_visibility(
                    QueueUrl=self._queue_url,
                    ReceiptHandle=self._receipt_handle,
                    VisibilityTimeout=self._visibility,
                )
            except Exception as e:
                logger.warning("Failed to extend visibility", extra={"error": str(e)})

    def stop(self) -> None:
        self._stopped.set()


class SqsWorker:
    def __init__(self, allowlist: CommandAllowlist, slack: SlackMessenger):
        self._sqs = boto3.client("sqs", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        self._queue_url = settings.SQS_QUEUE_URL or ""
        self._allowlist = allowlist
        self._slack = slack

    def _truncate(self, text: str) -> str:
        limit = settings.OUTPUT_MAX_CHARS
        if len(text) <= limit:
            return text
        head = text[: limit - 1000]
        tail = text[-1000:]
        return head + "\n...\n" + tail

    def _process_job(self, job: SqsJob) -> bool:
        allowed = self._allowlist.get(job.command)
        if not allowed:
            self._slack.post_thread_message(
                job.channel,
                job.thread_ts or job.event_ts,
                f"Command '{job.command}' is not allowed.",
            )
            return True  # drop
        self._slack.post_thread_message(
            job.channel,
            job.thread_ts or job.event_ts,
            f"Started '{job.command}' with args: {' '.join(job.args)}",
        )
        try:
            code, out, err = run_allowed_command(allowed, job.args, settings.COMMAND_TIMEOUT_SECS)
            status = "succeeded" if code == 0 else f"failed (exit {code})"
            message = f"Completed '{job.command}' {status}.\n"
            if out.strip():
                message += f"\nstdout:\n```\n{self._truncate(out)}\n```"
            if err.strip():
                message += f"\nstderr:\n```\n{self._truncate(err)}\n```"
            self._slack.post_thread_message(job.channel, job.thread_ts or job.event_ts, message)
            return True
        except CommandExecutionError as e:
            self._slack.post_thread_message(
                job.channel,
                job.thread_ts or job.event_ts,
                f"Error executing '{job.command}': {e}",
            )
            return True

    def receive_and_process_once(self) -> None:
        resp = self._sqs.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=20,
            VisibilityTimeout=min(max(settings.COMMAND_TIMEOUT_SECS, 60), 3600),
        )
        for msg in resp.get("Messages", []) or []:
            receipt = msg["ReceiptHandle"]
            body = msg.get("Body") or "{}"
            try:
                payload: Dict[str, Any] = json.loads(body)
                job = SqsJob(**payload)
            except Exception as e:
                logger.error("Invalid message body; deleting", extra={"error": str(e)})
                self._sqs.delete_message(QueueUrl=self._queue_url, ReceiptHandle=receipt)
                continue
            extender = VisibilityExtender(
                self._sqs,
                self._queue_url,
                receipt_handle=receipt,
                interval=30,
                visibility=min(max(settings.COMMAND_TIMEOUT_SECS, 60), 3600),
            )
            extender.start()
            try:
                success = self._process_job(job)
                if success:
                    self._sqs.delete_message(QueueUrl=self._queue_url, ReceiptHandle=receipt)
                else:
                    # let it retry (idempotent assumption)
                    pass
            finally:
                extender.stop()


