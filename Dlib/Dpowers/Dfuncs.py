#
#
# Copyright (c) 2020 DPS, dps@my.mail.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
import time, os, sys, threading, traceback, warnings, functools
from Dhelpers.all import container, launch, execute_after_print, PositiveInt,\
    restore_print_func, always_print_traceback
    #the last two print functions can be imported via the Dfuncs module
    
from .events import KeyboardAdaptor, MouseAdaptor, KeyWaiter, HookAdaptor, CombinedSender
from . import dlg, ntfy, clip, Win
from .windowpower import WindowObject

# =======================================================================
# SENDWAIT function
# =======================================================================

keyb = KeyboardAdaptor(group="Dfuncs",_primary=True)
mouse = MouseAdaptor(group="Dfuncs", _primary=True)
event_sender = CombinedSender(keyb,mouse)

class SendwaitError(Exception):
    pass
        

def nfsendwait(*args, **kwargs):
    """function shortcut to enable notifications"""
    return sendwait(*args, nfOn=True, notifytime=20, **kwargs)


def sendwait(mandatory, *optional, winwaittime=10, notifytime=5,
        continueOnError=False, nfOn=False, delay=None):
    """A multi-purpose function to quickly pass a chain of commands:
    The default symbol "→" is used to escape special command tags.
    Functions see code.
    """
    
    def report(a, b):
        if nfOn:
            ntfy(a, notifytime, b)
    
    args = (mandatory,) + optional
    
    for i in range(len(args)):
        ai = args[i]
        # notify(str(ai))
        error = None
        
        if isinstance(ai, (int, float)):
            report("sleeping", ai)
            time.sleep(ai)
        
        elif isinstance(ai, str):
            report("Sending keys:", ai)
            event_sender.send(ai)
        
        elif isinstance(ai, WindowObject):
            report("Waiting for Window to exist and activate:", ai)
            found_win = ai.wait_exist_activate(timeout=winwaittime)
            if found_win:
                report("Found active window:", ai)
            else:
                error = "Window did not exist after winwaittime"
        else:
            try:
                event_sender.send_event(ai)
            except TypeError:
                pass
            else:
                report(f"Sending event:", ai)
            try:
                pid = ai.pid
            except AttributeError:
                error = "Wrong argument type for startwait command."
            else:
                if isinstance(pid, PositiveInt):
                    report("Waiting for Window to exist and activate:",
                            "pid={pid}\nProcessObject='{ai}'".format_map(
                                    locals()))
                    found_win = Win(pid=pid).wait_exist(timeout=winwaittime)
                    if found_win:
                        report(f"Found active window: pid"
                            f"={pid}\nProcessObject='{ai}'")
                    else:
                        error = "Window did not exist after winwaittime"
                else:
                    error = "Wrong argument type for startwait command."
        
        # checking if there was an error:
        if error is not None:
            if continueOnError:
                # Change the behavior if startwait encounters an error.
                # Default= Notify and Exit
                return error
            else:
                raise SendwaitError(f"Argument {i} gave the following error: "
                    f"{error}")
        if delay: time.sleep(delay)
    # after looping over all arguments:
    return True



# ========================================================
### Catching messages to additionally show a notification
# ========================================================


def _not_if_tty(func):
    @functools.wraps(func)
    def new_func(*args, even_if_tty=False, **kwargs):
        if sys.stdout.isatty() and not even_if_tty:
            return "%s was ignored as stdout is a tty"%func.__name__
        return func(*args, **kwargs)
    return new_func

@_not_if_tty
def notify_about_errors(timeout=10):
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
        printable_traceback = "".join(traceback.format_tb(error_traceback))
        info = "%s:\n%s\n\nTraceback:\n%s"%(
            error_type.__name__, error_message, printable_traceback)
        container.set_temp_store_key("error_info", info, timeout)
        ntfy(error_type.__name__ + " occured in TriggerEngine.", timeout,
                str(error_message) + "\nPress F12 to see traceback.")
        sys.__excepthook__(error_type, error_message, traceback)
    
    sys.excepthook = my_excepthook

@_not_if_tty
def notify_about_warnings(timeout=10):
    save_showwarning = warnings.showwarning
    def my_showwarning(msg, cat, filename, lineno, *args, **kwargs):
        ntfy("Warning", timeout,
                "file: %s \nline: %s\n%s"%(filename, str(lineno), msg))
        save_showwarning(msg, cat, filename, lineno, *args, **kwargs)
    warnings.showwarning = my_showwarning


@_not_if_tty
def notify_about_print(timeout=5):
    def ntfy_after_print(*args, sep=" ", end="\n", notify=True, **ignore):
        if not notify: return
        file, line, func, text = traceback.extract_stack(limit=3)[-3]
        # there must be at least three frames: this one, _custom_print,
        # call of print func
        # we want to access the call of the print_func, so we use [-3]
        print_message = sep.join([str(arg) for arg in args])
        if end != "\n": print_message += end
        ntfy(print_message, timeout, "Printed on line %s in:\n%s"%(line, file))
    execute_after_print(ntfy_after_print)
    



# ===============================================================

def display_sorted_dict(dic, name=""):
    f = ""
    for i in sorted(dic):
        #    notify(i)
        f += i + "\t"*(3 + (i[0].upper() == "L") - len(i)//4) + "-> " + dic[
            i] + "\n"
        # notify(i)
    launch.get("echo", f, "|", "zenity", "--text-info")

extdict = {"jpeg": "jpg", "tiff": "tif"}


class FilePathParts:
    def __init__(self, file_path):
        self.path = file_path.rstrip("/")
        self.dir, self.base = os.path.split(self.path)
        self.name, self.ext = os.path.splitext(self.base)
        if self.ext == "":
            if os.path.isdir(self.path):
                self.ext = "dir"
        a = self.ext.lower()
        self.ext_norm = extdict.get(a,
                a)  # replace extension by version in extdict if present


# =============================================================================
#     Displaying window information and putting it to clipboard
# =============================================================================

def display_win_info():
    ntfy("Click on a window", 3)
    
    x = Win(loc="SELECT").all_info()
    winprops = x[:3] + ((x[1], x[2]),) + x[3:]
    
    show = [str(winprops[0]) + " [ID]", str(winprops[1]) + " [TITLE]",
        str(winprops[2]) + " [CLASS]", str(winprops[3]),
        str(winprops[4]) + " [PID]",
        str(winprops[5]) + " [GEOMETRY] (x,y,width,height)"]
    
    ret = dlg.choose(show, default=3, title="Window information",
            text="Save to clipboard:", width=700)
    
    if ret is not None:
        for i in range(len(show)):
            # dlg.msg(str(ret)+"\n"+str(show[i]))
            if ret == show[i]:
                clip.fill(winprops[i], notify=True)
                break


# =============================================================================
#     Display key names
# =============================================================================
def display_key_names():
    y = KeyWaiter.get1key()
    x = tuple(y.named_instance.names)
    time.sleep(0.1)
    if dlg.quest("Dpowers key name(s):\n{x}\n\nSave first(=standard) name to "
                 "clipboard?".format_map(locals()),title="Get key names"):
        clip.fill(x[0], notify=True)
        
def monitor_input_events(timeout=10, implementation=None,**hookkwargs):
    if implementation:
        this_hook=HookAdaptor(implementation)
    else:
        this_hook=HookAdaptor(group="keywait")
    ntfy("Showing all input events for %s seconds." % timeout)
    with this_hook.keyboard_mouse(functools.partial(ntfy,timeout=1), **hookkwargs):
        time.sleep(timeout)
    ntfy("Done showing input events.")