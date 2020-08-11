from functools import wraps 
import logging 

logger = logging.getLogger('main_logger')

from . import others_help

def main_logger(module_name):
    """
    Decorator that provides action logging, exception handling, and exception logging 
    Accepts module_name param
    Returns decorator 
    """
    def decorator(func): 
        @wraps(func)
        def wrapper(*args, **kwargs): 
            try: 
                logger.info(f'{module_name} {func.__name__} executing.')

                return func(*args, **kwargs)
 
            except Exception: 
                others_help.alert_error() 
                logger.exception(f'{module_name} {func.__name__}() exception.')
        
        return wrapper
    return decorator 