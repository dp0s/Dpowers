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
from abc import ABC, abstractmethod
from Dhelpers.baseclasses import AdditionContainer
from Dhelpers.arghandling import check_type
from ..event_classes import StringEvent, EventObjectSender
from .. import hotkeys, Adaptor, adaptionmethod, AdaptionError
import time, functools

def _doc(middle):
    return "*Class attribute.* Default time (in milliseconds) to wait between" \
           f" sending {middle}. You can set a custom value to this attribute"\
            " for the whole class or for a single instance."

def default_delay_doc(obj_name):
    print(_doc(f"several {obj_name} in a row"))

def default_duration_doc(obj_name):
    print(_doc(f"press and release event of the same {obj_name}"))

class Sender(AdditionContainer.Addend,ABC):
    
    #only_defined_names = False
    default_delay = None  # must be set in subclass
    custom_text_method = True
    
    @abstractmethod
    def _press(self, name):
        raise NotImplementedError

    def press(self, *names, delay=None):
        if delay is None: delay = self.default_delay
        for k in names:
            self._press(k)
            if delay: time.sleep(delay/1000)

    def text(self, text, delay=None, custom=None, **kwargs):
        if delay is None: delay = self.default_delay
        if custom is None: custom = self.custom_text_method
        for character in text:
            if custom:
                try:
                    self._text(character, **kwargs)
                    if delay: time.sleep(delay/1000)
                except NotImplementedError:
                    custom = False
            if not custom:
                self.tap(character, delay=delay, duration=10)
                

    def _text(self, character, **kwargs):
        raise NotImplementedError
    
    def tap(self, character, delay=None, duration=None):
        # defined for compatability
        # duration attribute is ignored because no rls defined
        self.press(character, delay=delay)
    
    def send_eventstring(self, string, auto_rls=True, delay=None):
        #auto_rls attribute is ignored because no rls defined
        for entry in StringEvent.split_str(string):
            if isinstance(entry, str):
                self.press(entry, delay=delay)
            else:
                raise TypeError
        
    _starting_symbol = "<"
    _ending_symbol = ">"
    
    
    def send(self, s, auto_rls=True, delay=None, **text_kwargs):
        text_kwargs["delay"] = delay
        _combination = self._ending_symbol + self._starting_symbol
        while True:
            s0, s1, s2 = s.partition(self._starting_symbol)
            if s0 != "": self.text(s0, **text_kwargs)
            if s2 == "": break
            if s2.startswith(_combination):
                # if <>< is typed, send a single < and search if any more <
                # are present
                self.text(self._starting_symbol,**text_kwargs)
                s = s2[2:]
            else:
                t0, t1, t2 = s2.partition(self._ending_symbol)
                if t1 == "":
                    # this happens if ">" was not found so that < is not closed.
                    self.text(self._starting_symbol + t0, **text_kwargs)
                    break
                elif t0 != "":
                    self.send_eventstring(t0, auto_rls=auto_rls, delay=delay)
                if t2 == "": break
                s = t2



class PressReleaseSender(Sender):
    
    default_duration = None

    @abstractmethod
    def _rls(self, name):
        raise NotImplementedError

    @hotkeys.add_pause_option(True)
    def rls(self, *names, delay=None):
        if delay is None: delay = self.default_delay
        for k in reversed(names):
            self._rls(k)
            if delay: time.sleep(delay/1000)
    
    def send_eventstring(self, string, auto_rls=True, delay=None):
        for entry in StringEvent.split_str(string):
            if isinstance(entry, str):
                if entry.endswith("_rls"):
                    if auto_rls: raise ValueError
                    self.rls(entry[:-4],delay=delay)
                elif auto_rls:
                    self.tap(entry, delay=delay)
                else:
                    self.press(entry,delay=delay)
            elif isinstance(entry, (list,tuple)):
                self.comb(*entry, delay=delay)
            else:
                raise TypeError(entry)
            
    @functools.wraps(Sender.press)
    def pressed(self, *names, delay=None):
        return PressedContext(self, *names, delay=delay)

    def tap(self, *keynames, delay=None, duration=None, repeat=1):
        if delay is None: delay = self.default_delay
        if duration is None: duration = self.default_duration
        for _ in range(repeat):
            for k in keynames:
                with self.pressed(k, delay=delay): time.sleep(duration/1000)
            
            
    @hotkeys.add_pause_option(True)
    def comb(self, *keynames, delay=None, duration=None):
        if delay is None: delay = self.default_delay
        if duration is None: duration = self.default_duration
        with self.pressed(*keynames, delay=delay):
            time.sleep(duration/1000)



class PressedContext:
    
    def __init__(self, sender_instance, *names, delay=None):
        self.sender_instance = sender_instance
        self.names = names
        self.delay = delay
    
    def __enter__(self):
        self.sender_instance.press(*self.names, delay=self.delay)
        return self.sender_instance
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        #if exc_type == AdaptionError: return  # just raise this error directly
        try:
            self.sender_instance.rls(*self.names, delay=self.delay)
            # try to rls the keys
        except Exception as e:
            if exc_type == type(e): return  # only reraise press error
            raise



class AdaptiveMixin(Adaptor):
    baseclass = True
    NamedClass = None
    #stand_dicts = defaultdict(lambda : defaultdict(lambda : list()))
    
    @property
    def Event(self):
        return self.NamedClass.Event
    
    @adaptionmethod("press", require=True)
    def _press(self, name, apply_map = True):
        if apply_map:
            try:
                name = self._press.standardizing_dict.apply(name)
            except AttributeError:
                name = self._press.standardizing_dict.get(name,name)
        try:
            return self._press.target(name)
        except Exception as e:
            if isinstance(e,self._press_errortype): raise NameError(name) from e
            raise
    
    @_press.target_modifier
    def _press_tm(self, target, amethod):
        self._press_errortype = self._get_errortype(target)
        self._create_standardizing_dict(amethod)
        return target
    
    def _get_errortype(self,target):
        try:
            target("ASFASDFASDFASxcvjxcjsjsj23")
        except Exception as e:
            return type(e)
        raise RuntimeError("Name 'ASFASDFASDFASxcvjxcjsjsj23' is allowed!?")
    
    def _create_standardizing_dict(self,  amethod):
        #this should be executed when amethod is adapted, when NamedClass
        # changes or when name_translation changes
        target_space = amethod.target_space
        try:
            names = target_space.names
        except AttributeError:
            names = {}
        if self.NamedClass:
            stand_dict = self.NamedClass.StandardizingDict(names)
        else:
            stand_dict = names
        if not self.name_translation:
            try:
                self.name_translation = self.universal_name_translations[target_space]
            except KeyError:
                pass
        if self.name_translation:
            old_dict = stand_dict.copy()
            for key,val in self.name_translation.items():
                try:
                    val2 = old_dict[val]
                except KeyError:
                    pass
                else:
                    stand_dict[key] = val2
        #check_type(self.NamedClass.StandardizingDict, stand_dict)
        amethod.standardizing_dict = stand_dict

    
    def _update_stand_dicts(self):
        for n in ("_press", "_rls"):
            try:
                amethod = getattr(self, n)
            except AttributeError:
                continue
            if amethod.target in (None,NotImplemented): continue
            self._create_standardizing_dict(amethod)

    name_translation = None
    universal_name_translations = dict()
    
    
    def set_name_translation(self, val, universal=False):
        check_type(dict,val)
        self.name_translation = val
        self._update_stand_dicts()
        if universal:
            target_space1 = self._press.target_space
            try:
                target_space2 = self._rls.target_space
            except AttributeError:
                target_space2 = None
            if target_space1 and target_space2:
                assert target_space1 == target_space2
            target_space = target_space1 if target_space1 else target_space2
            if not target_space: raise ValueError
            self.universal_name_translations[target_space] = val
            for instance in self.get_instances():
                if instance is self: continue
                instance._update_stand_dicts()
            
            
    



class AdaptiveSender(AdaptiveMixin, Sender):
    baseclass = True


#we don't inherit from AdaptiveSender directly
# because that would give an undesired method resolution order.
@AdaptiveSender.register
class AdaptivePressReleaseSender(AdaptiveMixin, PressReleaseSender,
        EventObjectSender):
    baseclass = True
    
    @adaptionmethod("rls", require=True)
    def _rls(self, name, apply_map=True):
        if apply_map:
            try:
                name = self._rls.standardizing_dict.apply(name)
            except AttributeError:
                name = self._rls.standardizing_dict.get(name, name)
        try:
            return self._rls.target(name)
        except Exception as e:
            if isinstance(e, self._rls_errortype):
                raise NameError(name) from e
            raise
    
    @_rls.target_modifier
    def _rls_tm(self, target, amethod):
        self._rls_errortype = self._get_errortype(target)
        self._create_standardizing_dict(amethod)
        return target

    #_press_rls_standdict = None # default_value
    
    # def _create_standardizing_dict(self, amethod):
    #     super()._create_standardizing_dict(amethod)
    #     # now detect if standardizing_dicts are the same
    #     # this will be important for Pressed ContextManager
    #     try:
    #         d1 = self._press.standardizing_dict
    #         d2 = self._rls.standardizing_dict
    #     except AttributeError:
    #         pass
    #     else:
    #         if d1==d2:
    #             self._press_rls_standdict = d1
    #             return
    #     self._press_rls_standdict = False
        


    def _send_event(self, event, reverse_press=False, autorelease=False):
        if not isinstance(event, self.Event): raise TypeError
        if event.press and not reverse_press or not event.press and reverse_press:
            self.press(event.name)
            if autorelease: self.rls(event.name)
        else:
            self.rls(event.name)
        
    

class CombinedSender(AdditionContainer, PressReleaseSender,
        EventObjectSender, basic_class=Sender):
    
    
    
    def __init__(self, *args):
        super().__init__(*args)
        self.default_delay = self._members[0].default_delay
        self.default_duration = self._members[0].default_duration
        
    @AdditionContainer.create_combined_method(NameError)
    def _press(self, name):
        pass

    @AdditionContainer.create_combined_method(NameError)
    def _rls(self, name):
        pass
    
    @AdditionContainer.create_combined_method(TypeError)
    def _send_event(self, event, **kwargs):
        pass
    
    @AdditionContainer.create_combined_method(NotImplementedError)
    def _text(self, character, **kwargs):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.send(*args,**kwargs)

    # useful methods:
    # -- send_event: This will call EventObjectSender.send_event and then
    # iterate over all members' _send_event methods until no TypeError is raised
    # -- press and rls will iterate over _press and _rls
    # -- text will call super().text which will iterate over _text
    # -- send. This will automatically call prs, rls, text and thus iterate
    #       as well
    
    
    
    
