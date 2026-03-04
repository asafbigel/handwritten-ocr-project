import time
import functools
from math_mind.engines.exceptions import RateLimitExceededError

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
                    print(f"Rate limit hit. Retrying {retries}/{max_retries} after {base_delay}s...")
                    time.sleep(base_delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator