from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Entry:
    value: Any
    expires_at: float


class TTLCache:
    """Simple in-memory TTL cache suitable for process-local caching."""

    def __init__(self, ttl_seconds: float = 600.0, max_size: int = 2048) -> None:
        self.ttl = float(ttl_seconds)
        self.max_size = int(max_size)
        self._data: dict[Any, _Entry] = {}

    def _purge(self) -> None:
        now = time.time()
        keys = [k for k, v in self._data.items() if v.expires_at <= now]
        for k in keys:
            self._data.pop(k, None)
        # size-based purge (simple FIFO by dict order)
        if len(self._data) > self.max_size:
            overflow = len(self._data) - self.max_size
            for k in list(self._data.keys())[:overflow]:
                self._data.pop(k, None)

    def get(self, key: Any) -> Any | None:
        self._purge()
        ent = self._data.get(key)
        if not ent:
            return None
        if ent.expires_at <= time.time():
            self._data.pop(key, None)
            return None
        return ent.value

    def set(self, key: Any, value: Any) -> None:
        self._purge()
        self._data[key] = _Entry(value=value, expires_at=time.time() + self.ttl)


# shared instance for Arshin lookups
arshin_cache = TTLCache(ttl_seconds=900.0, max_size=4096)

