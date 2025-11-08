from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json



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

    @classmethod
    def from_sqs_message(cls, message: Dict[str, Any]) -> "SqsJob":
        body = message.get("Body") or "{}"
        payload: Dict[str, Any] = json.loads(body)
        return SqsJob(**payload)

@dataclass
class CommandExecutionResult:
    exit_code: int
    stdout: str
    stderr: str

    def raise_for_status(self) -> None:
        if self.exit_code != 0:
            raise CommandExecutionError(command_execution_result=self)


class CommandExecutionError(Exception):
    def __init__(self, *args, command_execution_result: CommandExecutionResult, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_execution_result = command_execution_result
