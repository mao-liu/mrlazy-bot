import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(thread)d:%(threadName)s] %(message)s %(extra)s'
)

def get_env(name: str) -> str | None:
    return os.environ.get(name)


def get_int_env(name: str, default: int) -> int:
    try:
        return int(get_env(name))
    except ValueError:
        return default


# Common
AWS_REGION = get_env("AWS_REGION")
SQS_QUEUE_URL = get_env("SQS_QUEUE_URL")

# Lambda only
SLACK_SIGNING_SECRET = get_env("SLACK_SIGNING_SECRET")

# Local poller only
SLACK_BOT_TOKEN = get_env("SLACK_BOT_TOKEN")
COMMANDS_ALLOWLIST_PATH = get_env("COMMANDS_ALLOWLIST_PATH")
OUTPUT_MAX_CHARS = get_int_env("OUTPUT_MAX_CHARS", 3000)
MAX_CONCURRENT_COMMANDS = get_int_env("MAX_CONCURRENT_COMMANDS", 4)
SQS_LONG_POLL_SECS = get_int_env("SQS_LONG_POLL_SECS", 20)

