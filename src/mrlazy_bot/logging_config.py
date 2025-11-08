import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exc_info"] = self.formatException(record.exc_info)
        for key, value in getattr(record, "__dict__", {}).items():
            if key.startswith("_") or key in ("args", "msg", "levelno", "levelname", "pathname", "filename",
                                              "module", "exc_info", "exc_text", "stack_info", "lineno",
                                              "funcName", "created", "msecs", "relativeCreated", "thread",
                                              "threadName", "processName", "process"):
                continue
            log[key] = value
        return json.dumps(log, ensure_ascii=False)


def configure_json_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(level)

