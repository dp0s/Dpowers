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
import collections, traceback, threading, time, weakref

from .arghandling import check_type
from .launcher import launch
from abc import ABC, abstractmethod

class KeepInstanceRefs:
    __instance_ref_dict__ = collections.defaultdict(list)
    # this class attribute is a dictionary, supposed to contain one list of
    # instance
    # references for each sub class.
    # {cls1: instance_ref_list1, cls2: instance_ref_list2, etc.}
    # if cls has no instances, simply return an empty list by default.
    
    def __init__(self):
        super().__init__() #remove?
        self.__instance_ref_dict__[self.__class__].append(weakref.ref(self))
        # self.__instance_ref_dict__[self.__class__] is the list containing
        # all instance
        # references for this given
        # sub-class
        # we need a weakref, so that we don't get errors if the instance
        # object is deleted
    
    @classmethod
    def get_instances(cls):
        instance_ref_list = cls.__instance_ref_dict__[cls]
        for inst_ref in instance_ref_list:
            inst = inst_ref()
            if inst is None:
                pass
                # print("deleting",inst)
                # instance_ref_list.remove(inst_ref) #remove dead weakrefs
                # automatically
            else:
                # print("found: ",inst)
                yield inst
          
    @classmethod
    def subclass_from_name(cls, name):
        subclasses = cls.__subclasses__()
        if name in subclasses: return name
        check_type(str, name)
        for subclass in subclasses:
            if subclass.__name__ == name: return subclass
    
    @classmethod
    def instance_num(cls):
        return sum(1 for _ in cls.get_instances())
        # this is equal to the generator's length
    
    
    
    
class UniqueInstances(KeepInstanceRefs):
    
    _error_msg = None
    
    def __init__(self):
        for inst in self.get_instances():
            if self == inst:
                raise MultipleInstanceError(self._error_msg, inst)
        KeepInstanceRefs.__init__(self)
        self._new_instance = True

    @classmethod
    def get_instance(cls, *args, **kwargs):
        try:
            self = cls(*args,**kwargs)
        except MultipleInstanceError as e:
            self = e.existing_inst
            self._new_instance = False
        if not hasattr(self,"_new_instance"): raise AttributeError
        return self
        
        
class MultipleInstanceError(Exception):
    def __init__(self, msg, existing_inst):
        super().__init__(msg)
        self.existing_inst = existing_inst
        
        
        
        
        

class InstanceCreationError(Exception):
    pass

class RememberInstanceCreationInfo:
    def __init__(self):
        for frame, line in traceback.walk_stack(None):
            varnames = frame.f_code.co_varnames
            if varnames is ():
                break
            if frame.f_locals[varnames[0]] not in (self, self.__class__):
                break
                # if the frame is inside a method of this instance,
                # the first argument usually contains either the instance or
                #  its class
                # we want to find the first frame, where this is not the case
        else:
            raise InstanceCreationError("No suitable outer frame found.")
        self.creation_module = frame.f_globals["__name__"]
        self.creation_file, self.creation_line, self.creation_function, \
            self.creation_text = \
            traceback.extract_stack(frame, 1)[0]
        self.creation_name = self.creation_text[
        :self.creation_text.find('=')].strip()
        threading.Thread(target=check_existence_after_creation,
                args=(self, frame)).start()
    
    def __repr__(self):
        try:
            r = super().__repr__()
        except TypeError:
            # this happens if not used as BaseClass, but called directly
            r = object.__repr__(self)
        return r[:-1] + " with creation_name '%s'>" %self.creation_name


# the following is better than a staticmethod, because it allows using the
# the __init__ method of RememberInstanceCreationInfo without subclassing it
def check_existence_after_creation(obj, frame):
    while frame.f_lineno == obj.creation_line:
        time.sleep(0.01)
    # this is executed as soon as the line number changes
    # now we can be sure the instance was actually created
    error = InstanceCreationError(
            "\nCreation name not found in creation frame.\n"
            "creation_file: %s \ncreation_line: %s \n"
            "creation_text: %s\ncreation_name (might be wrong): "
            "%s"%(obj.creation_file, obj.creation_line, obj.creation_text,
            obj.creation_name))
    nameparts = obj.creation_name.split(".")
    try:
        var = frame.f_locals[nameparts[0]]
    except KeyError as k:
        raise error from k
    try:
        for name in nameparts[1:]: var = getattr(var, name)
    except AttributeError as a:
        raise error from a
    if var is not obj: raise error



class TimedObject(ABC):
    
    def __init__(self, *args, timeout, **kwargs):
        self.timeout = timeout
        self._timeout_thread = None
        self.active = False
        self.start_flag = threading.Event()
        self.stop_flag = threading.Event()
        super().__init__(*args,**kwargs)

    def _timeout_action(self):
        # if this returns True, then the timeout will not be performed
        pass
    
    def _error_handler(self, exc_type, exc_val, exc_tb):
        # this can return True value to suppress exceptions inside the with
        # statement. by default they are re-raised
        pass
    
    
    @abstractmethod
    def _start_action(self):
        pass
    
    @abstractmethod
    def _stop_action(self):
        pass
    
    def start(self):
        if self.active:
            raise RuntimeError("TimedObject %s cannot be started as it "
                               "is already active." % str(self))
        self.active = True
        ret = self._start_action()
        if self.timeout:
            self._timeout_thread = launch.thread(self._timeout_stop,
                    initial_time_delay=self.timeout)
        self.start_flag.set()
        self.start_flag.clear()
        return ret
        
    def _timeout_stop(self):
        if self.active:
            if self._timeout_action() is True:
                self._timeout_thread = None
            else:
                self.stop()
                self._timeout_thread = True
    
    def stop(self, raise_errors = True):
        if not self.active and raise_errors:
            if self._timeout_thread is True:
                    raise TimeoutError("TimedObject %s can not be stopped as it has "
                        "already timed out after %s seconds." % (str(self),
                            str(self.timeout)))
            else:
                raise RuntimeError("TimedObject %s can not be stopped as "
                                   "it is not active."%str(self))
        try:
            self._timeout_thread.cancel()
        except:
            pass
        self._timeout_thread = None
        if self.active:
            self.active = False
            ret = self._stop_action()
            self.stop_flag.set()
            self.stop_flag.clear()
            return ret
    
    def __enter__(self):
        self.start()
        return self
  
    def __exit__(self, *error_info):
        if self.active: self.stop()
        return self._error_handler(*error_info)
    
    def join(self, timeout=None):
        if self.active is not True: return False
        self.stop_flag.wait(timeout)
        return True
        





       
    

class AdditionContainer:
    
    # must be set in the subclass:
    basic_class = None
    
    
    def __init_subclass__(cls, basic_class=None, ordered=True):
        if basic_class is None:
            raise ValueError("Keyword argument basic_class required.")
        if not issubclass(basic_class, cls.Addend): raise TypeError
        cls.basic_class = basic_class
        cls.ordered=ordered
        basic_class.ContainerClass = cls
    
    def __init__(self, *args):
        self.members = []
        for arg in args:
            if isinstance(arg, self.__class__):
                self.members += arg.members
            elif isinstance(arg, self.basic_class):
                self.members += [arg]
            else:
                raise TypeError(arg)
    
    def __add__(self, other):
        if isinstance(other, (self.basic_class, self.__class__)):
            return self.__class__(self, other)
        try:
            return super().__add__(other)
        except AttributeError:
            return NotImplemented

    def __radd__(self, other):
        if other is 0: return self  # necessary for using sum()
        try:
            return super().__radd__(other)
        except AttributeError:
            return NotImplemented

    def __exit__(self, *error_info):
        booleans = tuple(bool(member.__exit__(*error_info)) for member in
                self.members)
        return True in booleans

    def __enter__(self):
        for m in self.members:
            m.__enter__()
        return self
    
    def __bool__(self):
        x = sum(bool(m) for m in self.members)
        return x > 0
    

    class Addend:
    
        ContainerClass = None
    
        def __add__(self, other):
            if isinstance(other,
                    (self.ContainerClass.basic_class, self.ContainerClass)):
                return self.ContainerClass(self, other)
            try:
                return super().__add__(other)
            except AttributeError:
                return NotImplemented
    
        def __radd__(self, other):
            if other is 0: return self  # necessary for using sum()
            try:
                return super().__radd__(other)
            except AttributeError:
                return NotImplemented