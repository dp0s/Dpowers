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
from Dhelpers.arghandling import check_type
from ..event_classes import StringEvent, EventSequence, EventCombination
from .. import Adaptor, adaptionmethod, AdaptionError, Layout
import functools, time, warnings

sleep = time.sleep
ShiftedKey = Layout.ShiftedKey



def _doc(middle):
    return "*Class attribute.* Default time (in milliseconds) to wait between" \
           f" sending {middle}. You can set a custom value to this attribute"\
            " for the whole class or for a single instance."

def default_delay_doc(obj_name):
    print(_doc(f"several {obj_name} in a row"))

def default_duration_doc(obj_name):
    print(_doc(f"press and release event of the same {obj_name}"))



class EventObjectSenderMixin:
    default_delay = None
    
    def _send_event(self, event, **kwargs):
        raise NotImplementedError
    
    def send_event(self, *events, delay=None, **kwargs):
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
                
                
                

class Sender(AdditionContainer.Addend):
    
    #only_defined_names = False
    default_delay = None  # must be set in subclass
    custom_text_method = True
    
    def get_backend_name(self, name):
        return name
    
    def press(self, *names, delay=None):
        if delay is None: delay = self.default_delay
        for k in names:
            self._press(k)
            if delay: time.sleep(delay/1000)
        
        
    def _press(self, name, send_infos=(), expand_shifted = False):
        send_infos = list(send_infos) #creates an independent copy
        backend_name = self.get_backend_name(name)
        if isinstance(backend_name, ShiftedKey):
            if expand_shifted:
                for bn in self._expand_shifted(backend_name):
                    self._press_action(bn)
                    send_infos.append((bn, self))
                return send_infos
            else:
                backend_name = [backend_name.keyname]
        self._press_action(backend_name)
        send_infos.append((backend_name, self))
        return send_infos

    def _press_action(self, name):
        raise NotImplementedError

    def text(self, text, delay=None, custom=None, **kwargs):
        if delay is None: delay = self.default_delay
        if custom is None: custom = self.custom_text_method
        for character in text:
            if custom:
                try:
                    self._text_action(character, **kwargs)
                    if delay: time.sleep(delay/1000)
                except NotImplementedError:
                    custom = False
            if not custom:
                self.tap(character, delay=delay, duration=10)
                

    def _text_action(self, character, **kwargs):
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

    def rls(self, *names, delay=None):
        if delay is None: delay = self.default_delay
        for k in reversed(names):
            self._rls(k)
            if delay: time.sleep(delay/1000)
            
    def _rls(self, name):
        backend_name = self.get_backend_name(name)
        if isinstance(backend_name, ShiftedKey):
                backend_name = backend_name.keyname
        self._rls_action(backend_name)
    
    def _rls_action(self, name):
        raise NotImplementedError
    
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
            
            
    def comb(self, *names, delay=None, duration=None, expand_shifted=False):
        if delay is None: delay = self.default_delay
        if duration is None: duration = self.default_duration
        delay = delay/1000
        duration = duration / 1000
        send_infos = []
        try:
            for name in names:
                send_infos = self._press(name, send_infos, expand_shifted)
                sleep(delay)
            sleep(duration)
        finally:
            e = None
            for name, sender_inst in reversed(send_infos):
                try:
                    sender_inst._rls_action(name)
                except Exception as e:
                    continue
                else:
                    sleep(delay)
            if e: raise e

    def tap(self, *names, delay=None, duration=None, repeat=1):
        for _ in range(repeat):
            for n in names:
                PressReleaseSender.comb(self,n, delay=delay,
                        duration=duration, expand_shifted=True)

    @functools.wraps(Sender.press)
    def pressed(self, *names, **kwargs):
        return PressedContext(self, *names, **kwargs)


class PressedContext:
    
    def __init__(self, sender_instance, *names, delay=None):
        self.sender_instance = sender_instance
        self.names = names
        if not delay: delay = sender_instance.default_delay
        self.delay = delay/1000
        self.send_infos = []
    
    def __enter__(self):
        for name in self.names:
            self.send_infos = self.sender_instance._press(name, self.send_infos)
            sleep(self.delay)
        return self.sender_instance
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        #if exc_type == AdaptionError: return  # just raise this error directly
        e = None
        for name, sender_inst in reversed(self.send_infos):
            try:
                sender_inst._rls_action(name)
            except Exception as e:
                continue
            else:
                sleep(self.delay)
        if e:
            if exc_type == type(e): return  # only reraise press error
            raise



class AdaptiveSender(Sender, Adaptor):
    baseclass = True
    NamedClass = None
    #stand_dicts = defaultdict(lambda : defaultdict(lambda : list()))
    translation_dict = None
    default_translations = {}
    _effective_dict = {}
    
    @property
    def Event(self):
        return self.NamedClass.Event
    
    
    def get_backend_name(self, name):
        try:
            return self._effective_dict.apply(name)
        except AttributeError:
            return self._effective_dict.get(name, name)
        

    @adaptionmethod("press", require=True)
    def _press_action(self, name):
        try:
            return self._press_action.target(name)
        except Exception as e:
            if isinstance(e,self._press_errortype): raise NameError(name) from e
            raise
    
    @_press_action.target_modifier
    def _press_tm(self, target):
        self._press_errortype = self._get_errortype(target)
        self.create_effective_dict(transfer=True)
        return target


    names = _press_action.adaptive_property("names", default={},
            ty=(dict, list, tuple))
    
    def _get_errortype(self,target):
        try:
            target("ASFASDFASDFASxcvjxcjsjsj23")
        except Exception as e:
            return type(e)
        raise RuntimeError("Name 'ASFASDFASDFASxcvjxcjsjsj23' is allowed!?")

    
    def set_translation_dict(self, dic, make_default=False):
        check_type(dict, dic)
        self.translation_dict = dic
        self.create_effective_dict(make_default=make_default)
    
    def _get_default_inst(self, target_space):
        enforced_inst = self.default_translations.get(target_space)
        if enforced_inst:
            assert isinstance(enforced_inst, self.__class__)
            assert enforced_inst._press_action.target_space is target_space
        return enforced_inst
    
    def create_effective_dict(self, make_default=False, transfer=False):
        ts = self._press_action.target_space
        if ts is None:
            if make_default: raise ValueError("Option make_default=True used, "
                  f"but no backend chosen yet for {self}." )
            return False
        enforced_inst = None
        if transfer: enforced_inst = self._get_default_inst(ts)
        self._create_effective_dict(ts, enforced_inst=enforced_inst)
        if make_default:
            # set this instance to be the default reference for this backend
            self.default_translations[ts] = self
            for instance in self.get_instances():
                if instance is not self and \
                        instance._press_action.target_space is ts:
                    instance.create_effective_dict(transfer=True)
    
    
    def _create_effective_dict(self, target_space, enforced_inst=None):
        #this should be executed:
        # - when amethod is adapted (i.e. target space changes)
        # - when NamedClass changes
        # - when name_translation changes
        # - when new enforced inst is set
        # stan dict format:
        #       NamedKey : Object to send to backend
        # translation_dict_format:
        #     user_input_name : remapped_name (may be ShiftedKey instance)
        #     (both sides of this are usually standardized automatically)
        names = self.names
        if self.NamedClass:
            stand_dict = self.NamedClass.StandardizingDict(names)
        else:
            stand_dict = names
        
        if enforced_inst: self.translation_dict = enforced_inst.translation_dict
            
        if self.translation_dict:
            copy = stand_dict.copy()  # copy is standardizing dict too
            for key, remapped in self.translation_dict.items():
                stand_dict[key] = self._process_trans_item(remapped, copy)
                
        self._effective_dict = stand_dict
        
    
    def _process_trans_item(self, remapped, copy):
        try:
            return copy[remapped]  # check if standardized(remapped) is among
            # the backend names defined in self.names (copy is standardized
            # copy of it)
        except KeyError:
            return remapped #this is not standardized
            # this is just in case if the backend accepts keys not
            # defined in self.names
            
            
            
class AdaptivePressReleaseSender(PressReleaseSender, AdaptiveSender,
        EventObjectSenderMixin):
    baseclass = True



    @adaptionmethod("rls", require=True)
    def _rls_action(self, name):
        try:
            return self._rls_action.target(name)
        except Exception as e:
            if isinstance(e, self._rls_errortype):
                raise NameError(name) from e
            raise
    
    @_rls_action.target_modifier
    def _rls_tm(self, target):
        self._rls_errortype = self._get_errortype(target)
        self.create_effective_dict()
        return target


    def _send_event(self, event, reverse_press=False, autorelease=False):
        if not isinstance(event, self.Event): raise TypeError
        if event.press and not reverse_press or not event.press and reverse_press:
            self.press(event.name)
            if autorelease: self.rls(event.name)
        else:
            self.rls(event.name)
            
        
class AdaptivePRSenderShifted(AdaptivePressReleaseSender):
    baseclass = True
    
    use_shifted = AdaptiveSender._press_action.adaptive_property("use_shifted",
            False, ty=bool)
    
    def _process_trans_item(self, remapped, copy):
        sup = super()._process_trans_item
        if isinstance(remapped, ShiftedKey):
            # extract the keyname from the ShiftedKey object and compose it
            # again afterwards
            if not self.use_shifted:
                warnings.warn(f"Found ShiftedKey {remapped} although attribute"
                  f" use_shifted of {self} is set to {self.use_shifted}.")
            backend_obj = sup(remapped.keyname, copy)
            return ShiftedKey(backend_obj, num=remapped.num)
        else:
            return sup(remapped, copy)
    
    def _create_effective_dict(self, *args, **kwargs):
        super()._create_effective_dict(*args,**kwargs)
        self.shift_obj = self.get_backend_name("shift")
        self.atr_gr_obj = self.get_backend_name("altgr")
        
    def _expand_shifted(self, obj):
        if not isinstance(obj,Layout.ShiftedKey): return [obj]
        ret = []
        if obj.num in (1,3): ret.append(self.shift_obj)
        if obj.num >= 2: ret.append(self.atr_gr_obj)
        ret.append(obj.keyname)
        return ret
    
    def _effective_dict_expanded(self):
        return {i : self._expand_shifted(j) for i,j in \
                self._effective_dict.items(prefer_single=True)}



    
class CombinedSender(AdditionContainer, PressReleaseSender,
        EventObjectSenderMixin, basic_class=Sender):
    
    def __init__(self, *args):
        super().__init__(*args)
        self.default_delay = self._members[0].default_delay
        self.default_duration = self._members[0].default_duration
        
    @AdditionContainer.create_try_error_method(NameError)
    def _press(self, name):
        pass

    @AdditionContainer.create_try_error_method(NameError)
    def _rls(self, name):
        pass
    
    @AdditionContainer.create_try_error_method(TypeError)
    def _send_event(self, event, **kwargs):
        pass
    
    @AdditionContainer.create_try_error_method(NotImplementedError)
    def _text_action(self, character, **kwargs):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.send(*args,**kwargs)

    # useful methods:
    # -- send_event: This will call EventObjectSender.send_event and then
    # iterate over all members' _send_event methods until no TypeError is raised
    # -- press and rls will iterate over _press_action and _rls_action
    # -- text will call super().text which will iterate over _text
    # -- send. This will automatically call prs, rls, text and thus iterate
    #       as well
    
    
    
    
