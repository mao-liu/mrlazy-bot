import hashlib
import hmac
import time
from typing import Mapping


class SlackVerificationError(Exception):
    pass


def verify_slack_signature(
    headers: Mapping[str, str],
    body: str,
    signing_secret: str,
    tolerance_seconds: int = 300,
) -> None:
    timestamp = headers.get("X-Slack-Request-Timestamp") or headers.get("x-slack-request-timestamp")
    signature = headers.get("X-Slack-Signature") or headers.get("x-slack-signature")
    if not timestamp or not signature:
        raise SlackVerificationError("Missing Slack signature headers")
    try:
        ts = int(timestamp)
    except ValueError:
        raise SlackVerificationError("Invalid timestamp")
    if abs(int(time.time()) - ts) > tolerance_seconds:
        raise SlackVerificationError("Timestamp outside tolerance")
    basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    computed = "v0=" + hmac.new(
        signing_secret.encode("utf-8"), basestring, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(computed, signature):
        raise SlackVerificationError("Invalid signature")

