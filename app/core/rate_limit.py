from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class InMemoryRateLimiter:
    """Small, process-local sliding-window limiter for public endpoints."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = monotonic()
        cutoff = now - self.window_seconds

        with self.lock:
            recent_requests = self.requests[key]
            while recent_requests and recent_requests[0] <= cutoff:
                recent_requests.popleft()

            if len(recent_requests) >= self.limit:
                return False

            recent_requests.append(now)
            return True
