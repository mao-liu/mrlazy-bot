from typing import Any, Dict, List, Optional, Tuple

from mrlazy_bot.models import SlackEvent

PREFIX = "!mrlazy"


def parse_message(event_payload: Dict[str, Any]) -> Optional[SlackEvent]:
    event = event_payload.get("event") or {}
    if event.get("type") != "message":
        return None
    if event.get("subtype"):
        return None
    text: str = event.get("text") or ""
    if not text.strip().lower().startswith(PREFIX):
        return None
    event_id: str = event_payload.get("event_id") or ""
    event_ts: str = event.get("ts") or ""
    channel: str = event.get("channel") or ""
    user: str = event.get("user") or ""
    thread_ts: Optional[str] = event.get("thread_ts")

    return SlackEvent(
        event_id=event_id,
        event_ts=event_ts,
        channel=channel,
        user=user,
        text=text,
        thread_ts=thread_ts,
    )


def extract_command_and_args(text: str) -> Tuple[str, List[str]]:
    parts = text.strip().split()
    if not parts or parts[0].lower() != PREFIX:
        return "", []
    if len(parts) == 1:
        return "", []
    command = parts[1]
    args = parts[2:] if len(parts) > 2 else []
    return command, args

