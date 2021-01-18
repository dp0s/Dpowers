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
from .event_classes import StringAnalyzer, EventCombination, EventSequence, \
    StringEvent
from .hookpower import HookAdaptor
from Dhelpers.all import launch, TimedObject, dpress, check_type
import collections


class TriggerManager(TimedObject, HookAdaptor.coupled_class()):
    
    adaptor = HookAdaptor(group="triggerman", _primary=True)
    
    def __init__(self, hook_adaptor=None, timeout=60, hook_buttons=False,
            buffer=2, **custom_key_kwargs):
        super().__init__(timeout=timeout)
        self.eventdict = dict()
        self.blocked_hks = []
        if hook_adaptor is not None: self.adaptor = hook_adaptor
        check_type(HookAdaptor, self.adaptor)
        self.k_old = ""
        self.hm= None
        self.recent_events = collections.deque()
        self.buffer = buffer
        self.hook_buttons = hook_buttons
        if hook_buttons:
            self.stringevent_analyzer = StringAnalyzer(NamedKey, NamedButton)
        else:
            self.stringevent_analyzer = NamedKey.Event
        self.key_kwargs = custom_key_kwargs
       
    def _start_action(self):
        timeout = self.timeout + 5 if self.timeout else None
        if self.blocked_hks:
            reinject_func = self.reinject_func
        else:
            reinject_func = None
        self.hm = self.adaptor.keys(self.event, timeout=timeout,
                reinject_func=reinject_func, **self.key_kwargs)
        if self.hook_buttons:
            self.hm += self.adaptor.buttons(self.event, timeout=timeout)
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
        #print(k)
        self.recent_events.append(k)
        if len(self.recent_events) > self.buffer: self.recent_events.popleft()
        recent_events = self.recent_events.copy()
        for event,action in self.eventdict.items():
            members = event.members
            for i in range(1,min(len(members),len(recent_events))+1):
                #_print(i, recent_events)
                if members[-i] != recent_events[-i]: break
            else:
                launch.thread(self.runscript, action, event)
                # this means that for each member event, the suiting recent
                # event has been found
                self.recent_events.clear()
  
    def runscript(self, action, hk):
        if self.active_blocks: return
        # print(hk_func)
        # print(hk,hk_func,type(hk_func))
        if type(action) is str:
            if action.startswith("[dkeys]"):
                if dpress(hk, 0.15):
                    keyb.send("<BackSpace>"*2 + action[7:], delay=1)
            else:
                keyb.send(action)
        elif callable(action):
            # the following makes sure that the hk_func is accepting 1
            # argument even if the underlying func does not
            if action.__code__.co_argcount == 1:
                return action(hk)
            else:
                return action()
        else:
            raise TypeError
        
    def add_event(self, event, action):
        if event in self.eventdict:
            raise ValueError(f"Tiggerevent {event} defined more than one time.")
        self.eventdict[event] = action
    
    def add_sequence(self, string, action):
        event = self.stringevent_analyzer.from_str(string).hotkey_version()
        self.add_event(event, action)
    
    def add_hotkey(self, string, action, rls=False, block=True):
        event = self.stringevent_analyzer.from_str(string)
        if isinstance(event,EventSequence): raise ValueError
        if isinstance(event,StringEvent):
            if not event.press: raise ValueError
            if block: self.blocked_hks.append(event)
            if rls: event += event.reverse()
        elif isinstance(event,EventCombination):
            event = event.hotkey_version(rls=rls)
        else:
            raise TypeError
        self.add_event(event, action)

    # A decorator
    def triggersequence(self, *strings):
        def decorator(decorated_func):
            for string in strings: self.add_sequence(string, decorated_func)
            return decorated_func
        return decorator

    # A decorator
    def hotkey(self, *strings, rls=False, block=True):
        def decorator(decorated_func):
            for string in strings:
                self.add_hotkey(string, decorated_func, rls=rls, block=block)
            return decorated_func
        return decorator
    
    def hotkey_rls(self,*strings, block=True):
        return self.hotkey(*strings,rls=True,block=block)
    
    def add_triggerdict(self, triggerdict):
        for eventstring, action in triggerdict.items():
            self.add_sequence(eventstring,action)



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