import time
from functools import wraps

def retry_decorator(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < retries:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator
