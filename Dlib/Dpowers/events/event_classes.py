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
from Dhelpers.baseclasses import AdditionContainer
from Dhelpers.named import NamedObj
from . import hotkeys
from abc import ABC, abstractmethod
from time import sleep




class Event(AdditionContainer.Addend):
    
    def __repr__(self):
        return f"<Event '{self}' of subclass " \
            f"{self.__class__.__module__}.{self.__class__.__name__}>"

    def sending_version(self):
        return self
    
    def hotkey_version(self, rls=False):
        return self



class EventSequence(AdditionContainer, Event, basic_class=Event):
    def __str__(self):
        return StringEvent.sequence_symbol.join(str(m) for m in self.members)
    
    def sending_version(self):
        return self.__class__(*tuple(m.sending_version() for m in self.members))
    
    def hotkey_version(self, rls=False):
        return self.__class__(
                *tuple(m.hotkey_version(rls=rls) for m in self.members))


class EventCombination(Event):
    
    @property
    def members(self):
        return self._members
    
    def __init__(self, *args):
        if len(args) < 2: raise ValueError
        for a in args:
            if not isinstance(a, PressReleaseEvent): raise TypeError
            if a.press is False: raise ValueError
        self._members = args
    
    def __str__(self):
        return StringEvent.combination_symbol.join(str(m) for m in self.members)
    
    def sending_version(self):
        return sum(m for m in self.members) + sum(
                m.reverse() for m in reversed(self.members))
    
    def hotkey_version(self, rls=False):
        ret = sum(m for m in self.members)
        if rls: ret += self.members[-1].reverse()
        return ret




class MouseMoveEvent(Event):
    
    def __init__(self, x, y, relative = False, screen_coordinates=True):
        self.x = x
        self.y = y
        self.relative = relative
        self.abbr = "r" if relative else "a"
    
    def __str__(self):
        return f"(mouse_move,{self.abbr},{self.x},{self.y})"
        



class StringEventUtilitites(ABC):
    
    combination_symbol = "+"
    sequence_symbol = " "
    
    @classmethod
    def split_str(cls,string):
        splitted_string = string.split(cls.sequence_symbol)  # split at space
        # print("splitted", splitted_string)
        corrected_split = []
        skip_next = False
        for n in range(len(splitted_string)):
            if skip_next:
                skip_next = False
                continue
            part = splitted_string[n]
            if part.startswith(cls.combination_symbol):
                corrected_split[-1] += part
            else:
                corrected_split.append(part)
            if part.endswith(cls.combination_symbol):
                corrected_split[-1] += splitted_string[n + 1]
                skip_next = True  # print("corrected",corrected_split)
        # now the corrected split has taken the combinations into account
        for s in corrected_split:
            if cls.combination_symbol in s:
                yield s.split(cls.combination_symbol)
            else:
                yield s
    
    def from_str(cls_or_self, string, hotkey=False, **kwargs):
        events = []
        for entry in cls_or_self.split_str(string):
            if isinstance(entry, str):
                event = cls_or_self._create_from_str(entry, **kwargs)
                events.append(event)
                if hotkey:
                    try:
                        p = event.press
                    except AttributeError:
                        raise ValueError("Option hotkey=True "
                                         f"does not make sense for f{event}.")
                    if not p: raise ValueError(
                            "Hotkey mode enabled. Use option  hotkey=False to "
                            "only send press or release events.")
                    events.append(event.reverse())
            elif isinstance(entry, (tuple, list)):
                t = tuple(cls_or_self._create_from_str(item, **kwargs)  for
                        item in entry)
                events.append(EventCombination(*t))
            else:
                raise TypeError
        if len(events) == 0: return ""
        if len(events) == 1: return events[0]
        return EventSequence(*events)


    @abstractmethod
    def _create_from_str(cls_or_self, s, **kwargs):
        raise NotImplementedError





class StringEvent(Event, StringEventUtilitites, str):

    __slots__ = ["name","given_name","named_instance"]

    NamedClass = None  # must be set by __init_subclass__ method of
                       # NamedKeyButton subclass
    allowed_names = () # set allowed_names even without use of NamedClass
    

    def __new__(cls, name="", *, only_defined_names=False):
        given_name = name
        named_instance = None
        if isinstance(name,int): name = str(name)
        if name != "":
            if cls.NamedClass:
                try:
                    # print(name, named_instance)
                    named_instance = cls.NamedClass.instance(name)
                except KeyError:
                    if not cls.allowed_names and only_defined_names:
                        raise NameError(f"name '{name}' not allowed for "
                        f"{cls}")
                else:
                    name = named_instance.name
            if not named_instance:
                if name not in cls.allowed_names:
                    if cls.allowed_names and only_defined_names:
                        raise NameError(f"name '{name}' not allowed for "
                        f"{cls}")
                    if name.isnumeric(): name = f"[{name}]"
        self = str.__new__(cls, name)
        self.name = name
        self.named_instance = named_instance
        self.given_name = given_name
        assert str(self) == name
        return self
    
    @classmethod
    def _args_from_str(cls, s):
        # OVERRIDE THIS!
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        return (s,)
    
    
    @classmethod
    def _create_from_str(cls, s, **kwargs):
        # don't override
        return cls(*cls._args_from_str(s),**kwargs)
    
    from_str = classmethod(StringEventUtilitites.from_str)



    # problem with redefining __eq__ and dicts/set __hash__ comparison
    # __hash__ method is needed for checking "self in dict" or "self in set"
    # however, as each name_string of the NamedKey has a unique hash,
    # and the __contains__ method of set and dict is only checking for hash equality,
    # (while __eq__-equality is checked only after hash equality)
    # we would need to provide several hash values for each keyvent object, which is impossible
    # workarounds:
    # 1. self in NamedKey.standardize(dict/set)
    #    this only checks for stnd name of self.
    #    the search inside the dict is using hashes and thus is quick
    #    however, standardization needs to be done beforehand
    # 2. custom methods defined below.
    
    
    def eq(self,other):
        if isinstance(other,int): other=f"[{other}]"
        if isinstance(other, str):
            if self.named_instance:
                return self.named_instance == other
            else:
                return super().__eq__(other)
        raise NotImplementedError

    def isin(self, *others):
        if len(others) == 0:
            raise SyntaxError
        elif len(others) == 1:
            others = others[0]
        for item in iter(others):
            if self.eq(item): return True
        return False

    def get_from(self,dic,return_if_not_found=None):
        try:
            c=dic.NamedClass_for_this_dict
            # this attribute only exists if dic is of type StandardizingDictClass
        except AttributeError:
            pass
        else:
            if c == self.NamedClass:
                # in this case, the dic is already standardized,
                # so we can use a normal hash comparison
                return dic.get(self, return_if_not_found)
        # this is what usually happens
        for key in iter(dic):
            if self.eq(key): return dic[key]
        return return_if_not_found
    
    
    

class PressReleaseEvent(StringEvent):
    __slots__ = ["press"]
    
    def __new__(cls, name="", press=True, write_rls=True, only_defined_names=False):
        assert press in (True, False, None)
        self = StringEvent.__new__(cls, name, only_defined_names=only_defined_names)
        if press is False and write_rls:
            self2 = str.__new__(cls, self.name + "_rls")
            for attr in StringEvent.__slots__:
                setattr(self2,attr,getattr(self,attr))
            self = self2
        self.press=press
        return self

    @classmethod
    def _args_from_str(cls, s):
        rls = s.endswith("_rls")
        if rls: s = s[:-4]
        return super()._args_from_str(s) + (not rls,)

    def strip_rls(self, raise_error=True):
        if not self: return self
        if raise_error and self.press: raise ValueError
        if self.named_instance:
            return self.named_instance.release_event_without_rls
        else:
            return self.__class__(name=self.name,press=False,write_rls=False)
    
    def reverse(self):
        if self.named_instance:
            if self.press:
                return self.named_instance.release_event
            else:
                return self.named_instance.press_event
        else:
            return self.__class__(name=self.name, press=not self.press)

    
    
    
class Keyvent(PressReleaseEvent):
    pass


class Buttonevent(PressReleaseEvent):
    
    __slots__ = ["x", "y"]
    
    def __new__(cls, *args, x=None, y=None,**kwargs):
        self= super().__new__(cls,*args,**kwargs)
        self.x=x
        self.y=y
        return self









class StringAnalyzer(StringEventUtilitites):
    
    #inherits method from_str!
    
    def __init__(self, *event_classes):
        self.event_classes = []
        for cls in event_classes:
            if issubclass(cls, NamedObj): cls = cls.Event
            if not issubclass(cls, StringEvent): raise TypeError
            if cls is EventSequence: raise TypeError
            self.event_classes.append(cls)
    
    

    def _create_from_str(self, s, only_defined_names=False):
        for cls in self.event_classes:
            try:
                return cls._create_from_str(s, only_defined_names=True)
            except NameError:
                continue
        if only_defined_names:
            raise NameError(f"String '{s}' could not be matched to any "
            f"event class in {self.event_classes} of {self}.")
        else:
            return self.event_classes[0]._create_from_str(s,
                    only_defined_names=False)



class EventObjectSender(ABC):
    
    default_delay=None
    
    @abstractmethod
    def _send_event(self, event, **kwargs):
        raise NotImplementedError
    
    @hotkeys.add_pause_option(True)
    def send_event(self, *events, delay=None,**kwargs):
        delay = self.default_delay if delay is None else delay
        for event in events:
            if isinstance(event, EventSequence):
                self.send_event(*event.members, **kwargs)
            elif isinstance(event, EventCombination):
                self.send_event(event.sending_version(), **kwargs)
            else:
                try:
                    name = event.name
                except AttributeError:
                    pass
                else:
                    if name.startswith("[") and name.endswith("]"):
                        name = name[1:-1]
                        event.name = name
                try:
                    self._send_event(event, **kwargs)
                except TypeError:
                    raise TypeError(f"event argument {event} not allowed for "
                                    f"send_event method of object {self}.")
                if delay: sleep(delay/1000)