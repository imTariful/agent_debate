import json
from datetime import datetime, timezone
import os


class LoggerNode:
    def __init__(self, path):
        self.path = path
        # ensure directory exists
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _timestamp(self):
        # Use timezone-aware UTC timestamps
        return datetime.now(timezone.utc).isoformat()

    def log_event(self, event: dict):
        entry = {
            "ts": self._timestamp(),
            **event,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
