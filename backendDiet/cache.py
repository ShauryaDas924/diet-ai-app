# backend/cache.py
from __future__ import annotations

import time
import threading
from typing import Any, Optional


# -----------------------------
# Simple thread-safe in-memory cache
# -----------------------------

_CACHE: dict[str, tuple[Any, float]] = {}
_LOCK = threading.Lock()


def get(key: str) -> Optional[Any]:
    """
    Get a cached value if present and not expired.
    """
    now = time.time()

    with _LOCK:
        item = _CACHE.get(key)
        if not item:
            return None

        value, expires_at = item
        if expires_at < now:
            # Expired — remove
            _CACHE.pop(key, None)
            return None

        return value


def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """
    Set a cached value with a TTL (seconds).
    """
    expires_at = time.time() + ttl_seconds

    with _LOCK:
        _CACHE[key] = (value, expires_at)


def delete(key: str) -> None:
    """
    Remove a cache entry manually.
    """
    with _LOCK:
        _CACHE.pop(key, None)


def clear() -> None:
    """
    Clear entire cache (useful for tests).
    """
    with _LOCK:
        _CACHE.clear()


def size() -> int:
    """
    Number of active (non-expired) cache entries.
    """
    now = time.time()
    with _LOCK:
        expired = [k for k, (_, exp) in _CACHE.items() if exp < now]
        for k in expired:
            _CACHE.pop(k, None)
        return len(_CACHE)
