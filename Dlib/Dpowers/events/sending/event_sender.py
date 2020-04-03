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
from abc import ABC, abstractmethod
from Dhelpers.all import AdditionContainer
from ..event_classes import EventSequence, EventCombination, StringAnalyzer, split_str
from .. import hotkeys
import time


class EventSender(AdditionContainer.Addend,ABC):
    
    only_defined_names = False  #the name definitions come from the
                # underlying StringEventCreator
    hotkey_enabled_default = False
    default_delay = None
    
    def text(self, string, **kwargs):
        raise NotImplementedError

    @hotkeys.add_pause_option(True)
    def press(self, *names, delay=None):
        delay = self.default_delay if delay is None else delay
        for k in names:
            self._press(k)
            if delay: time.sleep(delay/1000)

    @abstractmethod
    def _press(self, name):
        raise NotImplementedError
    

       
    
    def send_eventstring(self, string, delay=None):
        #self.send_event(self.StringEventCreator.from_str(string, hotkey=hotkey,
        #        only_defined_names=self.only_defined_names), **kwargs)
        for entry in split_str(string):
            if isinstance(entry, str):
                self.press(entry, delay=delay)
            else:
                raise TypeError
            
                
            
        
    @property
    def StringEventCreator(self):
        return self.NamedClass.Event

    @hotkeys.add_pause_option(True)
    def send_event(self, *events, **kwargs):
        for event in events:
            if isinstance(event, EventSequence):
                self.send_event(*event.members, **kwargs)
            elif isinstance(event, EventCombination):
                self.send_event(event.convert(),**kwargs)
            else:
                try:
                    self._send_event(event,**kwargs)
                    #print("event send", event)
                except TypeError:
                    raise TypeError(f"event argument {event} not allowed for "
                    f"send_event method of object {self}.")
                
    @abstractmethod
    def _send_event(self, event,**kwargs):
        raise NotImplementedError
    
    _starting_symbol = "<"
    _ending_symbol = ">"
    _combination = _ending_symbol + _starting_symbol
    
    @hotkeys.add_pause_option(True)
    def send(self, s, hotkey=None, **kwargs):
        """
        Send a chain of characters or keys.
        Use <key> to denote special keys or <key1+key2> for combinations.
        If not paired, < and > are interpreted normally.
        Use <><something> to send literal <something>
        <key  press> and <key rls> will only send _press/release events.
        <key1+key2 _press/rls> is also possible.
        <key x> will send the key x times.
        Example: keyb.send(<ctrl+v> or keyb.send(<ctrl  press>v<ctrl rls>))
        """
        while True:
            s0, s1, s2 = s.partition(self._starting_symbol)
            if s0 != "": self.text(s0, **kwargs)
            if s2 == "": break
            if s2.startswith(self._combination):
                # if <>< is typed, send a single < and search if any more <
                # are present
                self.text(self._starting_symbol,**kwargs)
                s = s2[2:]
            else:
                t0, t1, t2 = s2.partition(self._ending_symbol)
                if t1 == "":
                    # this happens if ">" was not found so that < is not closed.
                    self.text(self._starting_symbol + t0,**kwargs)
                    break
                elif t0 != "":
                    self.send_eventstring(t0, hotkey=hotkey, **kwargs)
                if t2 == "": break
                s = t2
                

class PressReleaseSender(EventSender):
    
    hotkey_enabled_default = True
    
    def send_eventstring(self, string, hotkey=True, delay=None):
        if hotkey is None: hotkey=self.hotkey_enabled_default
        for entry in split_str(string):
            if isinstance(entry, str):
                if hotkey:
                    self.tap(entry,delay=delay)
                else:
                    self.press(entry,delay=delay)
            elif isinstance(entry, tuple):
                self.comb(*entry,delay=delay)

    @abstractmethod
    def _rls(self, name):
        raise NotImplementedError

    
    
    @hotkeys.add_pause_option(True)
    def rls(self, *names, delay=None):
        delay = self.default_delay if delay is None else delay
        for k in reversed(names):
            self._rls(k)
            if delay: time.sleep(delay/1000)
    
    
    def _send_event(self, event, delay=None, reverse_press=False,
            autorelease=False):
        if isinstance(event, self.NamedClass.Event):
            if event.press and not reverse_press or not event.press and reverse_press:
                self.press(event.name, delay=delay)
                if autorelease: self.rls(event.name, delay=delay)
            else:
                self.rls(event.name, delay=delay)
        else:
            raise TypeError


    @hotkeys.add_pause_option(True)
    def tap(self, *keynames, duration=10, delay=None):
        for k in keynames:
            try:
                self.press(k, delay=duration)
            finally:
                self.rls(k, delay=delay)
            
            
    @hotkeys.add_pause_option(True)
    def comb(self, *keynames, delay=None):
        try:
            self.press(*keynames, delay=delay)
        finally:
            self.rls(*keynames, delay=delay)
        
        
        
class CleverEventSender(AdditionContainer, EventSender, basic_class
            =EventSender):
        
    
    def __init__(self, *args):
        super().__init__(*args)
        EventCreators = tuple(m.StringEventCreator for m in self.members)
        self._StringEventCreator = StringAnalyzer(*EventCreators)
        
    @property
    def StringEventCreator(self):
        return self._StringEventCreator
    
    def _send_event(self, event, **kwargs):
        for member in self.members:
            try:
                return member._send_event(event, **kwargs)
            except TypeError:
                continue
        raise TypeError(f"event {event} not allowed for any EventSender in "
        f"{self.members} of {self}.")
            
    def __call__(self, *args, **kwargs):
        return self.send_event(*args,**kwargs)
    
    
    @hotkeys.add_pause_option(True)
    def text(self, string, **kwargs):
        for member in self.members:
            try:
                member.text(string, **kwargs)
                return
            except NotImplementedError:
                continue
        raise NotImplementedError(f"text method not defined for any "
            f"EventSender in {self.members} of {self}.")
        
    
    
    
    
