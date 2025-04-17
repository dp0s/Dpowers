#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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
from Dhelpers.launcher import (launch, terminate_process, get_running_process)
import os, multiprocessing, warnings
from .. import ntfy, Dfuncs, Adaptor, adaptionmethod

class IconAdaptor(Adaptor):
    
    @adaptionmethod
    def start(self, IconObject):
        p = self.start.target_with_args()
        # p must be a pid (positive int) or Process object having a .pid
        # attribute. See the get_running_processes function definition
        # this will return a psutil.Process instance
        return get_running_process(p)
    

class IconHandler(IconAdaptor.AdaptiveClass):
    
    def __init__(self):
        super().__init__()
        self._items = []
        self.couple = True
        self.path = os.path.join(os.path.dirname(__file__),"icons","Dicon.png")
        self.tooltip = "Dpowers"
        self.left_click = self.terminate_parent
            #by default a left click terminates this script
        self.child_process = None
        self.last_item = ("Quit", self.terminate_parent)
        self.parent_id = os.getpid()
        self.queue = None
    
    def menuitem(self, text=None, func=None):
        """Adds a new entry to the icon's context menu.

        :param str text: Text of the menu entry. If omitted
            ``func.__name__`` will be used as text
            (underscores are replaced by space).
        :param func: Function to execute when clicking this menu entry.

        """
        
        if not func:
            def default_entry():
                warnings.warn("No action defined.")
            func = default_entry
        if not text: text = func.__name__.replace("_", " ")
        self._items.append((str(text), func))
    
    
    def additem(self, func):
        """A decorator to apply :func:`menuitem` directly onto a function."""
        self.menuitem(func=func)
        return func
    
    def add_default_menuitems(self):
        self.menuitem("Display win info", Dfuncs.display_win_info)
        self.menuitem("Get single key name(s)", Dfuncs.display_key_names)
        self.menuitem("Monitor input events for 10s",
                Dfuncs.monitor_input_events)
        self.menuitem("Toggle notifications", ntfy.toggle_all)
        self.menuitem("Save key stroke pattern", Dfuncs.save_key_replay)
        self.menuitem("Replay last key stroke pattern",
                Dfuncs.replay_pressed_keys)
    
    @property
    def items(self):
        if self.last_item:
            return self._items + [self.last_item]
        else:
            return self._items
    
    def start(self):
        self.child_process = self.adaptor.start(self)
        if self.couple:
            self.couple_process = launch.CoupleProcess(self.child_process)
        if self.queue is not None:
            if not isinstance(self.queue,multiprocessing.queues.Queue):
                raise ValueError
            # this happens if the start method defined a corresponding
            # queue object
            launch.thread(self.run_menu_funcs, initial_time_delay=1)
        
    
    def terminate(self):
        terminate_process(self.child_process)
    
    def terminate_parent(self):
        terminate_process(self.parent_id)
        
    def run_menu_funcs(self):
        while self.child_process.is_running():
            obj = self.queue.get()
            if isinstance(obj,int):
                func = self.items[obj][1]
            elif isinstance(obj,str):
                print(obj)
                for i in self.items:
                    if obj == i[0]:
                        # print("execute: "+str(i[1]))
                        func = i[1]
            else:
                raise TypeError
            launch.thread(func)