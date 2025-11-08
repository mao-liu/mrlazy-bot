from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SlackEvent:
    event_id: str
    event_ts: str
    channel: str
    user: str
    text: str
    thread_ts: Optional[str] = None


@dataclass
class SqsJob:
    event_id: str
    request_id: str
    event_ts: str
    channel: str
    user: str
    text: str
    command: str
    args: List[str] = field(default_factory=list)
    thread_ts: Optional[str] = None
    raw_event: Optional[Dict] = None

