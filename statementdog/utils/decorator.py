import time
import logging
from functools import wraps

logger = logging.getLogger()


def calc_time(log_level=logging.DEBUG):
    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            logger.log(
                log_level, f"{func.__name__}: {round(time.time() - start, 3)}s"
            )
            return ret

        return inner

    return wrap
