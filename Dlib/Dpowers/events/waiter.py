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
from . import HookAdaptor, CallbackHook, hotkeys, KeyboardAdaptor, \
    MouseAdaptor
from Dhelpers.all import check_type, launch, TimedObject
import time
from .. import NotificationAdaptor



class Waiter(TimedObject):
    ntfy = NotificationAdaptor(group="waiter", _primary=True)
    
    def __init__(self, callback_hook=None, maxlen = None, maxtime = 20, *,
            endevents=(), cond_func=None, eventmap=None,
            wait=True, capture=False, notify=True):
        super().__init__(timeout=maxtime, wait=wait)
        check_type(CallbackHook, callback_hook)
        if callback_hook: raise ValueError(f"Arguments of callback hook "
            f"{callback_hook} were already set.")
        self.maxlen = maxlen
        self.maxtime = maxtime
        if type(endevents) not in (list, tuple): endevents = [endevents]
        self.endevents =endevents
        self.eventmap = eventmap
        self.wait = wait
        self.capture = capture
        if cond_func and not callable(cond_func):
            raise ValueError(f"KeyWaiter cond_func {cond_func} is not callable")
        self.cond_func = cond_func
        timeout = maxtime + 5 if maxtime else None
        self.callback_hook = callback_hook(self.called, timeout,
                capture=self.capture)
        
        self.num = 0
        self.events = []
        if self.eventmap: self.events_mapped = []
        self.notify = notify
    
    def _start_action(self):
        if self.notify:  self.ntfy("Waiter active", 0.5,
                        f"maxlen:{self.maxlen}, maxtime:{self.maxtime}")
        self.callback_hook.start()
        time.sleep(0.1)
        # this time is needed for the hook manager to initialize
    
    def _stop_action(self):
        self.callback_hook.stop()

    def called(self, event):
        self.events.append(event)
        self.num += 1
        event_mapped = None
        if self.eventmap:
            try:
                event_mapped = self.eventmap[event]
            except KeyError:
                # if no entry found, omit it and do not count event
                self.num -= 1
            else:
                self.events_mapped.append(event_mapped)
        exitcode = self.event_condition(event, event_mapped)
        if exitcode is not None: self.stop(exitcode)
    
    
    def event_condition(self, event, ev_mapped):
        if self.maxlen and self.num >= self.maxlen:
            return "maxlen"
        if event in self.endevents or ev_mapped in self.endevents:
            return "endevent"
        f = self.cond_func
        if f:
            try:
                argcount = f.__code__.co_argcount
                if argcount == 0:
                    return f()
                elif argcount == 1:
                    return f(self)
                elif argcount == 2:
                    return f(self, event)
                elif argcount == 3:
                    return f(self, event, ev_mapped)
                else:
                    raise SyntaxError
            except Exception as e:
                self.stop(e)
                raise

    
    @classmethod
    def get1(cls, callback_hook, maxtime =2, wait = True, **options):
        if wait is not True:
            raise Exception("ERROR: get1 a arg 'wait' must be true")
        get1 = cls(callback_hook, maxlen=1, maxtime = maxtime, wait=True,
                **options).start()
        if get1.exitcode == "maxlen":
            return get1.events[0]
        if get1.exitcode != "timeout": raise RuntimeError
        
    # def reinject(self, delay=10, autorelease=False, reverse=False):
    #     delay = delay/1000
    #     if self.exitcode == "active": raise ValueError
    #     for event in self.events:
    #         event.reinject(autorelease, reverse=reverse)
    #         time.sleep(delay)
        
        
class KeyWaiter(Waiter):
    
    hook = HookAdaptor(group="keywait", _primary=True)
    keyb = KeyboardAdaptor(group="keywait",_primary=True)
    mouse = MouseAdaptor(group="keywait", _primary=True)
    hotstring_keyb = KeyboardAdaptor(group="hotstring")

    def __init__(self, *args, eventmap=None, keys=True,  buttons=False,
            press=True, release=False, write_rls=True, join_events=False, **kwargs):
        
        if release and write_rls and eventmap:
            eventmap.update({i + "_rls": j + "_rls" for i, j in eventmap.items()})
        if not release and not press:
            raise ValueError("KeyWaiter: key ups and down events are both disabled")
        self.join_events = join_events
        if join_events:
            self.joined_events = ""
            self.joined_events_mapped = ""
            
        hook_creator = sender = 0
        if keys:
            hook_creator += self.hook.keys()
            sender += self.keyb
        if buttons:
            hook_creator += self.hook.buttons()
            sender += self.mouse
        callback_hook = hook_creator(press=press, release=release,
                write_rls=write_rls)
        self.sender = sender
        self.press = press
        self.release = release
        self.write_rls = write_rls
        self.keys = keys
        self.buttons = buttons
        super().__init__(callback_hook, *args, eventmap=eventmap, **kwargs)
    
    def event_condition(self, event, ev_mapped):
        if self.join_events:
            self.joined_events += event
            if ev_mapped: self.joined_events_mapped += ev_mapped
        return super().event_condition(event, ev_mapped)
    
    
    def reinject(self, delay=10):
        #_print(self.events, self.keyb.name_translation)
        reverse_press = False
        if self.press and self.release: autorelease = False
        elif self.press and not self.release: autorelease = True
        elif not self.press and self.release:
            autorelease = True
            reverse_press = True
        else: raise ValueError
        self.sender.send_event(*self.events, delay=delay,
                autorelease =autorelease, reverse_press= reverse_press)

    @classmethod
    def get1key(cls, maxtime = 2, wait = True, press=True, release=True,
            capture=True, **options):
        if wait is not True:
            raise Exception("ERROR: get1 keyword arg 'wait' must be true")
        with hotkeys.paused(3):
            get1 = cls(maxlen=1, maxtime=maxtime, wait=True, press=press,
                    release = release, capture=capture,**options).start()
        if get1.exitcode == "maxlen":
            key = get1.events[0]
            if not press and not key.press and not options.get("write_rls",
                    False):
                # if only release events are collected, and if write_rls was
                # not explicitly set to True, remove the _rls tag by default
                key = key.strip_rls()
        elif get1.exitcode == "timeout":
            key = cls.hook.NamedKeyClass.Event() #return empty event
        else:
            raise RuntimeError
        return key


    @classmethod
    def hotstring(cls, string_dict, send=True, undo=True, undo_additional=0,
            endevents = (), limit_allowed_keys: list = False, eventmap=None):
        
        if limit_allowed_keys:
            limit_allowed_keys += [i + "_rls" for i in limit_allowed_keys]
        elif endevents == ():
            endevents = ("Tab", "Return", "Space", "Backspace")
        patterns = tuple(string_dict.keys())
        def checkinp(self, k, k_mapped):
            if limit_allowed_keys:
                if self.eventmap and k_mapped not in limit_allowed_keys:
                    return f"forbidden key {k_mapped}"
                if not self.eventmap and k not in limit_allowed_keys:
                    return f"forbidden key {k}"
            y = self.joined_events_mapped if self.eventmap else self.joined_events
            if y in patterns: return "hit"
    
        with hotkeys.paused(15):
            inp = cls(20, 5, endevents=endevents,eventmap=eventmap,
                    cond_func=checkinp, press=False, release=True,
                    write_rls=False, capture=False, join_events=True).start()
        if inp.exitcode == "hit":
            if undo:
                cls.hotstring_keyb.send("<BackSpace>"*(inp.num +
                                                      undo_additional))
            if send:
                if eventmap:
                    cls.hotstring_keyb.send(string_dict[
                        inp.joined_events_mapped])
                else:
                    cls.hotstring_keyb.send(string_dict[inp.joined_events])
        return inp