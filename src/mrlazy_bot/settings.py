import os
from typing import Optional


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def get_int(name: str, default: int) -> int:
    val = get_env(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def get_bool(name: str, default: bool) -> bool:
    val = get_env(name)
    if val is None:
        return default
    lowered = val.lower()
    if lowered in ("1", "true", "t", "yes", "y", "on"):
        return True
    if lowered in ("0", "false", "f", "no", "n", "off"):
        return False
    return default


# Common
AWS_REGION = get_env("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = get_env("SQS_QUEUE_URL")

# Lambda only
SLACK_SIGNING_SECRET = get_env("SLACK_SIGNING_SECRET")

# Local poller only
SLACK_BOT_TOKEN = get_env("SLACK_BOT_TOKEN")
COMMANDS_ALLOWLIST_PATH = get_env("COMMANDS_ALLOWLIST_PATH", "./config/commands.example.yaml")
COMMAND_TIMEOUT_SECS = get_int("COMMAND_TIMEOUT_SECS", 1800)
OUTPUT_MAX_CHARS = get_int("OUTPUT_MAX_CHARS", 3000)

