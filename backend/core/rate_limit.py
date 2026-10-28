"""Minimal in-process sliding-window rate limiter.

Scope note (stated, not hidden): state lives in each worker process. Under the
shipped 4-worker gunicorn unit the effective ceiling is up to 4x the configured
limit, and it resets when a worker recycles. That is enough to stop casual
abuse of anonymous endpoints; it is not a distributed quota.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException
from starlette.requests import HTTPConnection

_lock = threading.Lock()
_hits: Dict[str, Deque[float]] = defaultdict(deque)


def client_ip(conn: HTTPConnection) -> str:
    """Best-effort client address behind the shipped nginx proxy.

    nginx sets X-Real-IP to $remote_addr, which the client cannot forge
    (unlike the left-most X-Forwarded-For entry).
    """
    real_ip = conn.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return conn.client.host if conn.client else "unknown"


def check_rate_limit(key: str, limit: int, window_seconds: int) -> None:
    """Raise 429 when ``key`` exceeded ``limit`` hits within the window."""
    now = time.monotonic()
    cutoff = now - window_seconds
    with _lock:
        bucket = _hits[key]
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            retry_after = max(1, int(bucket[0] + window_seconds - now))
            raise HTTPException(
                status_code=429,
                detail={"code": "RATE_LIMITED", "message": "Too many requests. Try again later."},
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)


def reset_rate_limits() -> None:
    """Test helper."""
    with _lock:
        _hits.clear()


def per_client_limit(scope: str, limit: int, window_seconds: int):
    """FastAPI dependency factory: ``limit`` requests per client per window."""

    async def _dependency(request: HTTPConnection) -> None:
        check_rate_limit(f"{scope}:{client_ip(request)}", limit, window_seconds)

    _dependency.__name__ = f"rate_limit_{scope.replace('-', '_')}"
    return _dependency
