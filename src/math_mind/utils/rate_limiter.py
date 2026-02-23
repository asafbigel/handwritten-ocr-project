import time
from collections import deque


class RateLimiter:
    """
    Proactive sliding-window rate limiter.

    Blocks (with a status message) *before* sending a request if the
    RPM or RPD budget is exhausted, preventing 429 errors.
    """

    def __init__(self, rpm: int, rpd: int) -> None:
        self.rpm = rpm
        self.rpd = rpd
        self._minute_window: deque[float] = deque()
        self._day_count = 0
        self._day_start = time.monotonic()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _clean_minute_window(self) -> None:
        now = time.monotonic()
        while self._minute_window and now - self._minute_window[0] > 60.0:
            self._minute_window.popleft()

    def _reset_day_if_needed(self) -> None:
        if time.monotonic() - self._day_start >= 86_400.0:
            self._day_count = 0
            self._day_start = time.monotonic()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(self) -> None:
        """Block until a request slot is available, then claim it."""
        self._reset_day_if_needed()

        while True:
            self._clean_minute_window()

            if self._day_count >= self.rpd:
                remaining = 86_400.0 - (time.monotonic() - self._day_start)
                wait = min(remaining, 60.0)
                print(f"[RateLimiter] Daily limit ({self.rpd} rpd) reached. "
                      f"Waiting {wait:.0f}s…")
                time.sleep(wait)
                self._reset_day_if_needed()
                continue

            if len(self._minute_window) >= self.rpm:
                wait = 60.0 - (time.monotonic() - self._minute_window[0]) + 0.1
                if wait > 0:
                    print(f"[RateLimiter] RPM limit ({self.rpm} rpm) reached. "
                          f"Waiting {wait:.1f}s…")
                    time.sleep(wait)
                self._clean_minute_window()
                continue

            break

        self._minute_window.append(time.monotonic())
        self._day_count += 1
