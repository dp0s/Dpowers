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
from Dhelpers.named import NamedObj
from .event_classes import Buttonevent, Keyvent, PressReleaseEvent
import re

class NamedKeyButton(NamedObj):
    Event = None
    __slots__ = ["press_event", "release_event", "release_event_without_rls"]
    
    def __init_subclass__(cls, event_baseclass="inherit"):
        super().__init_subclass__()
        if event_baseclass == "inherit": event_baseclass = cls.Event
            #inherit Event's baseclass from parent's event baseclass
        if not issubclass(event_baseclass, PressReleaseEvent): raise TypeError
        ev = type(f"{cls.__name__}.Event", (event_baseclass,),{})
            # create a new event baseclass just for this NamedClass
        ev.__module__=cls.__module__
        ev.NamedClass = cls
        cls.Event = ev
    
    def __init__(self, *names):
        super().__init__(*names)
        # create all the corresponding events already to save time later
        self.press_event = self.Event(self.name, press=True)
        self.release_event = self.Event(self.name, press=False)
        self.release_event_without_rls = self.Event(self.name,
                press=False, write_rls=False)
    
    def get_event(self, press, write_rls=True):
        if press: return self.press_event
        if not write_rls:
            if press: raise ValueError
            return self.release_event_without_rls
        return self.release_event
    
    
    @classmethod
    def from_string(cls, string):
        event = 0
        for s in string.split(" "):
            if s.endswith("_rls"):
                e = cls.Event(s[:-4], press=False, NamedClass=cls)
            else:
                e = cls.Event(s, press=True, NamedClass=cls)
            event += e
        return event
    
    
    @classmethod
    def _check_if_name_is_allowed(cls, name):
        if isinstance(name, str) and len(name) > 1:
            for s in (" ", "+", "[", "]", "_rls", "<", ">"):
                if s in name: raise NameError(
                        "Keyname: " + str(name) + "\nKey class: " + str(
                                cls) + "\nThe string %s is not allowed."%s)
        return True
    
    @classmethod
    def analyze_string(cls, string, applied_func):
        if len(string) <= 1:
            return applied_func(string)
        splitted_name = re.split("([ +])", string)  # splits at + and space
        if len(splitted_name) == 1:
            return applied_func(string)
        output = ""
        for item in splitted_name:
            add_later = ""
            if item in (" ", "+", ""):
                output += item
                continue
            if item.endswith("_rls"):
                item = item[:-4]
                add_later = "_rls"
            if item.startswith("[") and item.endswith("]"):
                number = item[1:-1]
                if not number.isdecimal():
                    raise TypeError(
                            "Non decimal string enclosed in []:   " + number)
                output += "[%s]"%applied_func(number)
            else:
                output += applied_func(item)
            output += add_later
        return output



class NamedKey(NamedKeyButton, event_baseclass=Keyvent):
    pass


class NamedButton(NamedKeyButton, event_baseclass=Buttonevent):
    
    def get_event(self, press, write_rls=True, x=None, y=None):
        event = super().get_event(press, write_rls)
        event.x=x
        event.y=y
        
        
