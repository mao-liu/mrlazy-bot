import hashlib
import hmac
import time

from mrlazy_bot.lambda_app.slack_verification import verify_slack_signature


def test_verify_signature_ok():
    secret = "test_secret"
    ts = str(int(time.time()))
    body = '{"type":"event_callback"}'
    basestring = f"v0:{ts}:{body}".encode("utf-8")
    signature = "v0=" + hmac.new(secret.encode("utf-8"), basestring, hashlib.sha256).hexdigest()
    headers = {
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": signature,
    }
    verify_slack_signature(headers, body, secret, tolerance_seconds=60)


