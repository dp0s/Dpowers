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
from abc import ABC, abstractmethod
from Dhelpers.all import AdditionContainer
from .event_classes import EventSequence, KeybuttonCombination, StringAnalyzer
from . import hotkeys



class EventSenderBase(AdditionContainer.Addend,ABC):
    
    @abstractmethod
    def _send_event(self, event,**kwargs):
        raise NotImplementedError
    
    def text(self, string, **kwargs):
        raise NotImplementedError
    
    @hotkeys.add_pause_option(True)
    def send_event(self, *events, **kwargs):
        for event in events:
            if isinstance(event, EventSequence):
                self.send_event(*event.members, **kwargs)
            elif isinstance(event, KeybuttonCombination):
                self.send_event(event.convert(),**kwargs)
            else:
                try:
                    self._send_event(event,**kwargs)
                    #print("event send", event)
                except TypeError:
                    raise TypeError(f"event argument {event} not allowed for "
                    f"send_event method of object {self}.")
       
    @hotkeys.add_pause_option(True)
    def send_eventstring(self, string, hotkey=False, **kwargs):
        self.send_event(self.StringEventCreator.from_str(string, hotkey=hotkey),
                **kwargs)
    
    @property
    def StringEventCreator(self):
        return self.NamedClass.Event


    
    _starting_symbol = "<"
    _ending_symbol = ">"
    _combination = _ending_symbol + _starting_symbol
    
    @hotkeys.add_pause_option(True)
    def send(self, x, hotkey=True, **kwargs):
        """
        Send a chain of characters or keys.
        Use <key> to denote special keys or <key1+key2> for combinations.
        If not paired, < and > are interpreted normally.
        Use <><something> to send literal <something>
        <key  press> and <key rls> will only send _press/release events.
        <key1+key2 _press/rls> is also possible.
        <key x> will send the key x times.
        Example: keyb.send(<ctrl+v> or keyb.send(<ctrl  press>v<ctrl
        rls>))
        """
        while True:
            x0, x1, x2 = x.partition(self._starting_symbol)
            if x0 != "": self.text(x0, **kwargs)
            if x2 == "": break
            if x2.startswith(self._combination):
                # if <>< is typed, send a single < and search if any more <
                # are present
                self.text(self._starting_symbol,**kwargs)
                x = x2[2:]
            else:
                y0, y1, y2 = x2.partition(self._ending_symbol)
                if y1 == "":
                    # this happens if ">" was not found so that < is not closed.
                    self.text(self._starting_symbol + y0,**kwargs)
                    break
                elif y0 != "":
                    self.send_eventstring(y0, hotkey=hotkey, **kwargs)
                if y2 == "": break
                x = y2
        
        
class EventSender(AdditionContainer, EventSenderBase, basic_class
            =EventSenderBase):
        
    
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
                member._send_event(event, **kwargs)
                return
            except TypeError:
                continue
        raise TypeError
            
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
        raise NotImplementedError
        
    
    
    
    
