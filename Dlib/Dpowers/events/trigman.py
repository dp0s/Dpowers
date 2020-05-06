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
from warnings import warn
from . import NamedKey, keyb, NamedButton
from .hookpower import HookAdaptor
from Dhelpers.all import launch, TimedObject, dpress
from .event_classes import StringAnalyzer


class TriggerManager(TimedObject):
    
    triggermanhook = HookAdaptor(group="triggerman", _primary=True)
    
    def __init__(self, hook_adaptor=None, timeout=60, hook_mouse=False):
        super().__init__(timeout=timeout)
        self.eventdict = dict()
        self.blocked_hks = []
        if hook_adaptor is None: hook_adaptor = self.triggermanhook
        if not isinstance(hook_adaptor, HookAdaptor): raise TypeError
        self.hook_adaptor = hook_adaptor
        self.k_old = ""
        self.hm= None
        self.hook_mouse = hook_mouse
        if hook_mouse:
            self.stringevent_analyzer = StringAnalyzer(NamedKey, NamedButton)
        else:
            self.stringevent_analyzer = NamedKey.Event
       
    def _start_action(self):
        timeout = self.timeout + 5 if self.timeout else None
        if self.blocked_hks:
            reinject_func = self.reinject_func
        else:
            reinject_func = None
        self.hm = self.hook_adaptor.keys(self.event, timeout=timeout,
                reinject_func=reinject_func)
        if self.hook_mouse:
            self.hm += self.hook_adaptor.buttons(self.event, timeout=timeout)
        return self.hm.start()
    
    def reinject_func(self, event_obj):
        if event_obj in self.blocked_hks: return False
        return True
        
    def _stop_action(self):
        return self.hm.stop()
    
    def _timeout_action(self):
        warn("Timeout after %s seconds: Stopping TriggerManager %s." % (
            self.timeout,self))
    
    def event(self, k):
        #_print(k)
        for hk in (k, self.k_old + k):
            # checking whether a single or 2 button hotkey is triggered.
            if hk in self.eventdict:
                launch.thread(self.runscript, hk)
                self.k_old = ""  # resetting the key history if a hotkey was
                # triggered
                break
        else:
            self.k_old = k
  
    def runscript(self, hk):
        if self.active_blocks: return
        hk_func = self.eventdict[hk]
        # print(hk_func)
        # print(hk,hk_func,type(hk_func))
        if type(hk_func) is str:
            if hk_func.startswith("[dkeys]"):
                if dpress(hk, 0.15):
                    keyb.send("<BackSpace>"*2 + hk_func[7:], delay=1)
            else:
                keyb.send(hk_func)
        elif callable(hk_func):
            # the following makes sure that the hk_func is accepting 1
            # argument even if the underlying func does not
            if hk_func.__code__.co_argcount == 1:
                return hk_func(hk)
            else:
                return hk_func()
        else:
            raise TypeError

    # A decorator for adding a function hotkey
    def trigger_on(self, *strings, block=False):
        def func(decorated_func):
            for string in strings:
                # add the function to be triggered by the appropriate hotkeys
                event = self.stringevent_analyzer.from_str(string).sending_version()
                if event in self.eventdict:
                    raise ValueError(
                            f"Tiggerevent {event} defined more than one time.")
                self.eventdict[event] = func
                if " " in string:
                    self.blocked_hks += string.split(" ")
                else:
                    self.blocked_hks.append(string)
            return decorated_func
        return func

    active_blocks = 0

    @classmethod
    def block(cls):
        cls.active_blocks += 1
        #print(cls.active_blocks)
        
    @classmethod
    def unblock(cls, delay=None):
        if delay:
            launch.thread(cls._unblock, initial_time_delay=delay)
        else:
            cls._unblock()

    @classmethod
    def _unblock(cls):
        cls.active_blocks -= 1
        #print(cls.active_blocks)
        if cls.active_blocks < 0: raise ValueError

    @classmethod
    def paused(cls, timeout=10):
        return PauseObject(timeout, cls)
    # this creates a PauseObject suitable for a with statement
    # usage: with instance.paused():   or    with TriggerManager.paused():
    
    
    
class PauseObject(TimedObject):
    def __init__(self, timeout, cls):
        super().__init__(timeout=timeout)
        self.cls = cls
    
    def _start_action(self):
        self.cls.block()
        
    def _stop_action(self):
        self.cls.unblock(delay=0.1)
        # delaying the unblock is necessary because when the user types,
        # the key up events are often catched without intention otherwise