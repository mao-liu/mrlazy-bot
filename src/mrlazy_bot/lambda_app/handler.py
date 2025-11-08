import json
import logging
from typing import Any, Dict

from mrlazy_bot.lambda_app.event_parser import extract_command_and_args, parse_message
from mrlazy_bot.lambda_app.slack_verification import SlackVerificationError, verify_slack_signature
from mrlazy_bot.lambda_app.sqs_client import enqueue_job
from mrlazy_bot.logging_config import configure_json_logging
from mrlazy_bot.models import SqsJob
from mrlazy_bot import settings


configure_json_logging()
logger = logging.getLogger("lambda")


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # API Gateway (HTTP API or REST) proxy format
    body = event.get("body") or ""
    headers = event.get("headers") or {}

    # Slack URL verification challenge
    try:
        payload = json.loads(body or "{}")
    except json.JSONDecodeError:
        payload = {}
    if payload.get("type") == "url_verification" and "challenge" in payload:
        return _response(200, {"challenge": payload["challenge"]})

    # Verify signature for all other requests
    try:
        if not settings.SLACK_SIGNING_SECRET:
            logger.warning("SLACK_SIGNING_SECRET not set; rejecting request")
            return _response(401, {"ok": False})
        verify_slack_signature(headers, body, settings.SLACK_SIGNING_SECRET)
    except SlackVerificationError as e:
        logger.info("Signature verification failed", extra={"reason": str(e)})
        return _response(401, {"ok": False})

    # Accept only message events with prefix
    slack_event = parse_message(payload)
    if not slack_event:
        return _response(200, {"ok": True})  # noop to avoid Slack retries

    command, args = extract_command_and_args(slack_event.text)
    job = SqsJob(
        event_id=slack_event.event_id,
        request_id=getattr(context, "aws_request_id", ""),
        event_ts=slack_event.event_ts,
        channel=slack_event.channel,
        user=slack_event.user,
        text=slack_event.text,
        command=command,
        args=args,
        thread_ts=slack_event.thread_ts or slack_event.event_ts,
        raw_event=payload,
    )

    if not settings.SQS_QUEUE_URL:
        logger.error("SQS_QUEUE_URL not set; cannot enqueue")
        return _response(500, {"ok": False})
    enqueue_job(settings.SQS_QUEUE_URL, job.__dict__)
    logger.info("Enqueued job", extra={"event_id": job.event_id, "command": job.command})
    return _response(200, {"ok": True})


