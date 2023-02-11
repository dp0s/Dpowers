#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
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
from Dhelpers.container import container
from Dhelpers.builtin_manipulation import execute_after_print,\
    execute_after_warnings, execute_after_error, always_print_traceback
#the last two print functions should be imported via the Dfuncs module
from Dhelpers.arghandling import PositiveInt
from .winapps import pythoneditor

from .events import KeyboardAdaptor, MouseAdaptor, KeyWaiter, HookAdaptor, CombinedSender
from . import dlg, ntfy, clip, Win, launch
from .windowpower import WindowObject

# =======================================================================
# SENDWAIT function
# =======================================================================

keyb = KeyboardAdaptor(group="Dfuncs",_primary_name="keyb")
mouse = MouseAdaptor(group="Dfuncs", _primary_name="mouse")
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

def notify_about_error(hotkey=None, timeout=10):
    @execute_after_error
    def error_notification(error_type, error_message, error_traceback):
        source_msg = ""
        if hotkey: source_msg += f"Press {hotkey} to see."
        ntfy(f"{error_type.__name__}: {error_message}", timeout, source_msg)
        def analyze_error():
            options = traceback.format_tb(error_traceback)
            text = f"{error_type}\n{error_message}\n\nTraeback:\n"
            result = dlg.choose(options, options[-1], text=text, width=1000,
                    height=1000)
            if result:
                i = options.index(result)
                fs = traceback.extract_tb(error_traceback, i + 1)[i]
                pythoneditor.jump_to_line(fs[0], fs[1])
        container.set_temp_store_key("exec_func",analyze_error, timeout)



def notify_about_warnings(hotkey=None,timeout=10):
    @execute_after_warnings
    def post_notifcation(msg,file,line):
        source_msg = f"Printed on line {line} in: {file}."
        if hotkey: source_msg+= f" Press {hotkey} to see."
        ntfy(f"Warning: {msg}", timeout, source_msg)
        container.set_temp_store_key("exec_func", functools.partial(
                pythoneditor.jump_to_line,file, line), timeout)
        

def notify_about_print(hotkey=None, timeout=5):
    @execute_after_print
    def ntfy_after_print(*args, sep=" ", end="\n", notify=True, **ignore):
        if not notify: return
        file, line, func, text = traceback.extract_stack(limit=3)[-3]
        # there must be at least three frames: this one, _custom_print,
        # call of print func
        # we want to access the call of the print_func, so we use [-3]
        print_message = sep.join([str(arg) for arg in args])
        if end != "\n": print_message += end
        source_msg = f"Printed on line {line} in: {file}."
        if hotkey: source_msg += f" Press {hotkey} to see."
        ntfy(print_message, timeout, source_msg)
        container.set_temp_store_key("exec_func", functools.partial(
                pythoneditor.jump_to_line, file, line), timeout*2)



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


saved_patterns = []
    
def save_key_replay():
    k = KeyWaiter(maxtime=600,endevents=("Esc",))
    ntfy("Saving pressed keys",10, "Abort by pressing Esc")
    saved_patterns.append(k)
    k.start()
    ntfy("Stop saving pressed keys")

def replay_pressed_keys():
    k = saved_patterns[-1]
    ntfy("Press ShiftL to start")
    if KeyWaiter.wait_for_key("ShiftL"):
        ntfy("reinjecting")
        k.reinject()
        ntfy("reinjecting done")