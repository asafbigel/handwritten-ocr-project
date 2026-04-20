import time
import functools
import logging
from math_mind.engines.exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)

def with_retry(max_retries: int = 3, base_delay: float = 60.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except RateLimitExceededError as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    current_delay = base_delay * (2 ** retries) + random.uniform(0, 1))
                    logger.warning(
                        f"Rate limit hit in '{func.__name__}'. "
                        f"Retrying {retries+1}/{max_retries} after {current_delay}s..."
                    )
                    time.sleep(current_delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator
