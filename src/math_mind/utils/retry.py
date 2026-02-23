import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def with_retry(
    max_attempts: int = 4,
    base_delay: float = 2.0,
    backoff: float = 2.0,
    retriable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator factory: exponential-backoff retry.

    Catches *retriable_exceptions*; re-raises on the final attempt.
    Designed to wrap both plain functions and bound methods.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retriable_exceptions as exc:
                    if attempt == max_attempts:
                        raise
                    print(
                        f"[Retry] {func.__name__} attempt {attempt}/{max_attempts - 1} "
                        f"failed: {exc!r}. Retrying in {delay:.1f}s…"
                    )
                    time.sleep(delay)
                    delay *= backoff
            raise RuntimeError("Unreachable")  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator
