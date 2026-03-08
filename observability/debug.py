from functools import wraps
import time as _time

def log_tool_call(logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = _time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (_time.time() - start) * 1000
                logger.info('tool_call', tool=func.__name__, duration_ms=duration_ms, status='success')
                return result
            except Exception as e:
                duration_ms = (_time.time() - start) * 1000
                logger.info('tool_call', tool=func.__name__, duration_ms=duration_ms, status='error', error=str(e))
                raise
        return wrapper
    return decorator
