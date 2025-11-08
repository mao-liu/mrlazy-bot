import time
from typing import Dict, Optional, Tuple


class InMemoryDedupe:
    def __init__(self, ttl_seconds: int = 600, max_size: int = 1024):
        self._ttl = ttl_seconds
        self._max = max_size
        self._store: Dict[str, float] = {}

    def seen(self, key: str) -> bool:
        now = time.time()
        # cleanup expired
        to_delete = [k for k, ts in self._store.items() if now - ts > self._ttl]
        for k in to_delete:
            self._store.pop(k, None)
        if key in self._store:
            return True
        if len(self._store) >= self._max:
            # drop oldest
            oldest = min(self._store.items(), key=lambda kv: kv[1])[0]
            self._store.pop(oldest, None)
        self._store[key] = now
        return False


