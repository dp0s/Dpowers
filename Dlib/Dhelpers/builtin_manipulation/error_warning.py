from . import _add_tty_disable_option
import threading, sys, warnings

@_add_tty_disable_option
def execute_after_error(func):
    #    Workaround for `sys.excepthook` thread bug from:
    #    http://bugs.python.org/issue1230540
    #
    #   Call once from the main thread before creating any threads.
    # this is necessary so that the Threading module does not swallow all the
    #  import
    init_original = threading.Thread.__init__
    def init(self, *args, **kwargs):
        init_original(self, *args, **kwargs)
        run_original = self.run
        def run_with_except_hook(*args2, **kwargs2):
            try:
                run_original(*args2, **kwargs2)
            except Exception:
                sys.excepthook(*sys.exc_info())
        self.run = run_with_except_hook
    threading.Thread.__init__ = init
    
    def my_excepthook(error_type, error_message, error_traceback):
        # this function allows to perform an action in case of an exception,
        # before the
        # standard action takes place
        # print(error_traceback.tb_lineno, error_traceback.tb_frame.f_lineno,
        #        error_traceback.tb_frame.f_code.co_filename)
        # last_tb_line = traceback.extract_tb(error_traceback)[-1]
        # printable_traceback = "".join(traceback.format_tb(error_traceback))
        func(error_type, error_message, error_traceback)
        sys.__excepthook__(error_type, error_message, error_traceback)
    
    sys.excepthook = my_excepthook
    return func  # allow use as decorator



_add_tty_disable_option
def execute_after_warnings(func):
    save_showwarning = warnings.showwarning
    def my_showwarning(msg, cat, filename, lineno, *args, **kwargs):
        func(msg, filename, lineno)
        save_showwarning(msg, cat, filename, lineno, *args, **kwargs)
    warnings.showwarning = my_showwarning
