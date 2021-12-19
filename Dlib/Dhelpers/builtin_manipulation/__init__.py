import functools

def _add_tty_disable_option(func):
    @functools.wraps(func)
    def new_func(*args, disable_if_tty=False, **kwargs):
        if sys.stdout.isatty() and disable_if_tty:
            print("%s was ignored as stdout is a tty"%func.__name__)
            return
        return func(*args, **kwargs)
    return new_func


from .customprint import *
from .error_warning import *