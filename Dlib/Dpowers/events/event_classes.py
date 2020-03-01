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
from Dhelpers.all import AdditionContainer, check_type, NamedObj


combination_symbol = "+"
sequence_symbol = " "

def _from_str(cls_or_self, string, hotkey=False):
    splitted_string = string.split(sequence_symbol)  # split at space
    #print("splitted", splitted_string)
    corrected_split = []
    skip_next = False
    for n in range(len(splitted_string)):
        if skip_next:
            skip_next = False
            continue
        part = splitted_string[n]
        if part.startswith(combination_symbol):
            corrected_split[-1] += part
        else:
            corrected_split.append(part)
        if part.endswith(combination_symbol):
            corrected_split[-1] += splitted_string[n + 1]
            skip_next=True
        #print("corrected",corrected_split)
    # now the corrected split has taken the combinations into account
    events = []
    for s in corrected_split:
        if combination_symbol in s:
            t = tuple(cls_or_self._create_from_str(name) for name in s.split(
                    combination_symbol))
            events.append(KeybuttonCombination(*t))
        else:
            event = cls_or_self._create_from_str(s)
            events.append(event)
            if hotkey:
                if not event.press:raise ValueError("Hotkey mode enabled. "
             "Use option hotkey=False to only send press or release events.")
                events.append(event.reverse())
    if len(events) == 0: return StringEvent()
    if len(events) == 1: return events[0]
    #print(splitted_string, corrected_split)
    return EventSequence(*events)




class Event(AdditionContainer.Addend):
    
    def __repr__(self):
        return f"<Event '{self}' of subclass " \
            f"{self.__class__.__module__}.{self.__class__.__name__}>"


class EventSequence(AdditionContainer, Event, basic_class=Event):
    def __str__(self):
        return sequence_symbol.join(str(m) for m in self.members)
    



class MouseMoveEvent(Event):
    
    def __init__(self, x, y, relative = False, screen_coordinates=True):
        self.x = x
        self.y = y
        self.relative = relative
        self.abbr = "r" if relative else "a"
    
    def __str__(self):
        return f"(mouse_move,{self.abbr},{self.x},{self.y})"
        



class StringEvent(Event, str):
    
    # hooked_by = None  # set by collecting hook class
    # inject_args = None  # set by collecting hook class
    #
    # def reinject(self, reverse=False):
    #     try:
    #         self.hooked_by.collector.inject(*self.inject_args,
    #                 reverse=reverse)
    #     except AttributeError:
    #         return False
    #     else:
    #         return True
    
    from_str = classmethod(_from_str)
    
    @classmethod
    def _create_from_str(cls, string, raise_error=False):
        return cls(string)


class KeybuttonEvent(StringEvent):
    
    __slots__ = ["name", "named_instance", "press"]
    
    NamedClass=None #must be set by __init_subclass__ method of NamedKeyButton
    # subclass
    
    # def reinject(self, autorelease=False, reverse=False):
    #     success = super().reinject(reverse=reverse)
    #     if autorelease and success and (self.press and not reverse or not
    #     self.press and reverse):
    #         if autorelease is True: autorelease=5
    #         time.sleep(autorelease/1000)
    #         super().reinject(reverse=not reverse)
    

    def __new__(cls, name="", press=True, write_rls=True, raise_error=False):
        named_instance = None
        if name != "":
            try:
                #print(name, named_instance)
                named_instance = cls.NamedClass.instance(name)
            except KeyError as k:
                if raise_error: raise ValueError from k
                name = f"[{name}]"
            else:
                name = named_instance.name
        else:
            press = None
        string = name
        if press is False and write_rls: string += "_rls"
        self=super().__new__(cls,string)
        self.name = name
        self.named_instance = named_instance
        self.press=press
        return self
    
    @classmethod
    def _create_from_str(cls, string, raise_error=False):
        rls = string.endswith("_rls")
        if rls: string = string[:-4]
        if string.startswith("[") and string.endswith("]"):
            string = string[1:-1]
        return cls(string,press=not rls, raise_error=raise_error)



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

    def strip_rls(self, raise_error=True):
        if raise_error and self.press: raise ValueError
        if self.named_instance:
            ret = self.named_instance.release_event_without_rls
        else:
            ret = self.__class__(name=self.name,press=False,write_rls=False)
        return ret
    
    def reverse(self):
        if self.named_instance:
            if self.press:
                ret = self.named_instance.release_event
            else:
                ret = self.named_instance.press_event
        else:
            ret = self.__class__(name=self.name, press=not self.press)
        return ret

    def eq(self,other):
        if isinstance(other,int): other=f"[{other}]"
        if isinstance(other, str):
            if self.NamedClass:
                return super().__eq__(self.NamedClass.standardize(other))
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
            if c== self.NamedClass:
                # in this case, the dic is already standardized,
                # so we can use a normal hash comparison
                return dic.get(self, return_if_not_found)
        # this is what usually happens
        for key in iter(dic):
            if self.eq(key):
                return dic[key]
        return return_if_not_found
    
    
class Keyvent(KeybuttonEvent):
    pass


class Buttonevent(KeybuttonEvent):
    
    __slots__ = ["x", "y"]
    
    def __new__(cls, *args, x=None, y=None,**kwargs):
        self= super().__new__(cls,*args,**kwargs)
        self.x=x
        self.y=y
        return self




    
    
class KeybuttonCombination(Event):
    
    def __init__(self, *args):
        if len(args) < 2: raise ValueError
        for a in args:
            if not isinstance(a, KeybuttonEvent): raise TypeError
            if not a.press: raise ValueError
        self.members = args
    
    def __str__(self):
        return combination_symbol.join(str(m) for m in self.members)
    
    def convert(self):
       return sum(m for m in self.members) + sum(m.reverse() for m in
           reversed(self.members))




class StringAnalyzer:
    def __init__(self, *event_classes):
        self.event_classes = []
        for cls in event_classes:
            if issubclass(cls, NamedObj): cls = cls.Event
            if not issubclass(cls, StringEvent): raise TypeError
            if cls is EventSequence: raise TypeError
            self.event_classes.append(cls)
    
    __call__ = _from_str   #not a classmethod! So the first argument of the
            # _from_str function is not cls but actually self
    from_str = _from_str
    
    def _create_from_str(self, s):
        for cls in self.event_classes:
            try:
                return cls._create_from_str(s, raise_error=True)
            except ValueError:
                continue
        raise ValueError
        