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
import inspect
from warnings import warn
from . import NamedKey, keyb, NamedButton
from .event_classes import StringAnalyzer, EventCombination, EventSequence, \
    StringEvent
from .hookpower import HookAdaptor, CallbackHook, KeyhookBase, ButtonhookBase
from Dhelpers.launcher import launch
from Dhelpers.baseclasses import TimedObject, KeepInstanceRefs
from Dhelpers.arghandling import check_type
from Dhelpers.counting import dpress
import collections


class PatternListener:
    
    def __init__(self, buffer = 4):
        self.eventdict = dict()
        self.recent_events = collections.deque()
        self.buffer = buffer
        self.blocked_hks = []
        self.stringevent_analyzer = StringAnalyzer(NamedKey, NamedButton)

    def event(self, k):
        if not self.eventdict: return
        # _print(k)
        self.recent_events.append(k)
        if len(self.recent_events) > self.buffer: self.recent_events.popleft()
        recent_events = self.recent_events.copy()
        for event, action in self.eventdict.items():
            members = event.members
            lm = len(members)
            if lm > len(recent_events): continue
            # if more members are required than actual events passed
            for i in range(-1, -lm - 1, -1):
                if members[i] != recent_events[i]: break
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
                    keyb.send(action[7:], delay=1)
            else:
                keyb.send(action)
        elif callable(action):
            # the following makes sure that the hk_func is accepting 1
            # argument even if the underlying func does not
            try:
                return action(hk)
            except TypeError:
                return action()
        else:
            raise TypeError

    def add_event(self, event, action):
        if event in self.eventdict:
            raise ValueError(f"Tiggerevent {event} defined more than one time.")
        self.eventdict[event] = action

    def add_sequence(self, string, action):
        event = self.stringevent_analyzer.create_from_str(
                string).hotkey_version()
        self.add_event(event, action)

    def add_hotkey(self, string, action, rls=False, block=True):
        event = self.stringevent_analyzer.create_from_str(string)
        if isinstance(event, EventSequence): raise ValueError
        if isinstance(event, StringEvent):
            if not event.press: raise ValueError
            if block: self.blocked_hks.append(event)
            if rls: event += event.reverse()
        elif isinstance(event, EventCombination):
            event = event.hotkey_version(rls=rls)
        else:
            raise TypeError
        self.add_event(event, action)

    # A decorator
    def sequence(self, *strings):
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

    def hotkey_rls(self, *strings, block=True):
        return self.hotkey(*strings, rls=True, block=block)

    def add_triggerdict(self, triggerdict):
        for eventstring, action in triggerdict.items():
            self.add_sequence(eventstring, action)

    

    active_blocks = 0

    @classmethod
    def block(cls):
        cls.active_blocks += 1  # print(cls.active_blocks)

    @classmethod
    def unblock(cls, delay=None):
        if delay:
            launch.thread(cls._unblock, initial_time_delay=delay)
        else:
            cls._unblock()

    @classmethod
    def _unblock(cls):
        cls.active_blocks -= 1
        # print(cls.active_blocks)
        if cls.active_blocks < 0: raise ValueError

    @classmethod
    def paused(cls, timeout=10):
        return PauseObject(timeout, cls)
        # this creates a PauseObject suitable for a with statement
        # usage: with instance.paused():   or    with TriggerManager.paused():



class RegisteredHook(PatternListener):
    
    def __init__(self, buffer, hook_instance, container_triggerman=None):
        super().__init__(buffer)
        check_type(CallbackHook, hook_instance)
        if isinstance(hook_instance, KeyhookBase):
            self.stringevent_analyzer = NamedKey.Event
        elif isinstance(hook_instance, ButtonhookBase):
            self.stringevent_analyzer = NamedButton.Event
        self.hook_instance = hook_instance(self.event)
        self.triggerman_instance = container_triggerman
        
    def event(self, k):
        super().event(k)
        if self.triggerman_instance: self.triggerman_instance.event(k)
        
    def start(self):
        if self.blocked_hks or self.triggerman_instance and \
                self.triggerman_instance.blocked_hks:
            try:
                self.hook_instance = self.hook_instance(reinject_func =
                                self.reinject_func )
            except NotImplementedError:
                if self.blocked_hks: raise
        return self.hook_instance.start()
    
    def stop(self):
        return self.hook_instance.stop()

    def reinject_func(self, event_obj):
        if event_obj in self.blocked_hks: return False
        if self.triggerman_instance and event_obj in \
                self.triggerman_instance.blocked_hks: return False
        return True
        


class TriggerManager(PatternListener,TimedObject, HookAdaptor.AdaptiveClass,
        KeepInstanceRefs):
    
    adaptor = HookAdaptor(group="triggerman", _primary=True)
    
    
    def __init__(self, timeout=60, buffer=4):
        PatternListener.__init__(self,buffer=buffer)
        TimedObject.__init__(self,timeout=timeout)
        KeepInstanceRefs.__init__(self)
        self.registered_hooks = []
        self.was_started = False
        
    @classmethod
    def start_all(cls):
        for inst in cls.get_instances():
            if inst.was_started is False: inst.start()
            
    def add_hook(self, hook_instance, buffer=None,**hook_kwargs):
        timeout = None if self.timeout is None else self.timeout + 5
        hook_instance = hook_instance(timeout=timeout, **hook_kwargs)
        buffer = self.buffer if buffer is None else buffer
        new_registered_hook = RegisteredHook(buffer, hook_instance,
                container_triggerman=self)
        self.registered_hooks.append(new_registered_hook)
        return new_registered_hook
    
    def hook_keys(self, backend=None, **hook_kwargs):
        if backend:
            adaptor = self.adaptor_class(keys=backend)
        else:
            adaptor = self.adaptor
        return self.add_hook(adaptor.keys(),**hook_kwargs)
        
    def hook_buttons(self,backend=None,**hook_kwargs):
        if backend:
            adaptor = self.adaptor_class(buttons=backend)
        else:
            adaptor = self.adaptor
        return self.add_hook(adaptor.buttons(), **hook_kwargs)
    
    def hook_custom(self, backend=None,**hook_kwargs):
        if backend:
            adaptor = self.adaptor_class(custom=backend)
        else:
            adaptor = self.adaptor
        return self.add_hook(adaptor.custom(), **hook_kwargs)
    
    def _start_action(self):
        self.was_started = True
        for rhook in self.registered_hooks: rhook.start()
        
    def _stop_action(self):
        for rhook in self.registered_hooks:
            try:
                rhook.stop()
            except Exception as e:
                warn(e)


    def _timeout_action(self):
        warn("Timeout after %s seconds: Stopping TriggerManager %s." % (
            self.timeout,self))


   
    
    
    
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