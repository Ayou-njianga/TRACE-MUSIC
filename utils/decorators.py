import functools
import logging

def log_exceptions(logger: logging.Logger):
    """
    Decorator used to capture exceptions in methods and
    log them with a stack trace before re-raising.
    """
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.exception("Exception in %s: %s", func.__name__, exc)
                raise
        return wrapper
    return deco
