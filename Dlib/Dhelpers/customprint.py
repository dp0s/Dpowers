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
import builtins, inspect, traceback
from .container import container

# =======================================================================
# Alternating the builtin print function
# =======================================================================
# =======================================================================

# save the standard print function to _print:
if not inspect.isbuiltin(print):
    raise Exception("built in print function has already been changed.")
if hasattr(builtins, "_print"):
    if not builtins._print is builtins.print:
        raise Exception("_print already defined but is not the original print "
                        "function.")
else:
    builtins._print = builtins.print
    
container.execute_after_print = []

def find_original_print_func():
    if inspect.isbuiltin(builtins._print):
        return builtins._print
    elif inspect.isbuiltin(builtins.print):
        return builtins.print
    else:
        raise NameError("original print function not found.")

def restore_print_func():
    builtins.print = find_original_print_func()
    container.execute_after_print = []
    
    
class print_func_replaced:
    def __init__(self, temporary_print_func=None):
        self.temp_print = find_original_print_func() if temporary_print_func \
                                    is None else temporary_print_func
    def __enter__(self):
        self.saved = builtins.print, container.execute_after_print
        builtins.print = self.temp_print
        return self.saved[0]
    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.print, container.execute_after_print = self.saved

def execute_after_print(func):
    original_print = find_original_print_func()
    if not callable(func):
        raise TypeError
    if hasattr(container, "execute_after_print"):
        if func in container.execute_after_print:
            raise ValueError("function %s is already executed after print.")
        container.execute_after_print += [func]
    else:
        container.execute_after_print = [func]
    def _custom_print(*args, **kwargs):
        print_kwargs = {k: v for k, v in kwargs.items() if
            k in ("sep", "end", "file", "flush")}
        # this is necessary if additional kwargs are passed to custom_print
        original_print(*args, **print_kwargs)
        for fun in container.execute_after_print:
            fun(*args, **kwargs)
    builtins.print = _custom_print
    traceback.print = original_print  # this avoids problems with showing
    # errors


def print_last_traceback(*ignore, tb_lines=1, print_traceback=True, end="\n",
        **ignore_too):
    if not print_traceback:
        return
    original_print = find_original_print_func()
    frame = inspect.currentframe().f_back
    called_by_print = (frame.f_code.co_name == "_custom_print")
    if called_by_print:
        frame = frame.f_back
        tb_lines = container.default_tb_lines_to_print
    stack = traceback.extract_stack(frame, tb_lines)
    if called_by_print:
        file = stack[-1][0]
        if "IPython" in file and file.endswith(
                ("interactiveshell.py", "displayhook.py")):
            return
        if not end.endswith("\n"):
            original_print()  # create line between print output and traceback
    for line in traceback.format_list(stack):
        if line.endswith("\n"):
            line = line[:-1]
        original_print(line)
    original_print()  # to create a newline at the very end

def always_print_traceback(default_tb_lines=1):
    container.default_tb_lines_to_print = default_tb_lines
    execute_after_print(print_last_traceback)
