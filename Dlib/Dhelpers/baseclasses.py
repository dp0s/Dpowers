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

import collections, traceback, threading, time, weakref

from .arghandling import check_type
from Dhelpers.launcher import launch
from abc import ABC, abstractmethod
from inspect import signature

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


def check_existence_after_creation(obj, frame):
    time.sleep(0.1)
    #while frame.f_lineno == obj.creation_line:
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
    
    def __init__(self, *args, timeout, duration=True, wait = False, **kwargs):
        self.timeout = timeout
        self._timeout_thread = None
        self.active = False
        self.start_flag = threading.Event()
        self.stop_flag = threading.Event()
        self.measure_duration = duration
        self.wait = wait
        self.exitcode = None
        if duration:
            self.starttime = None
            self.endtime = None
        super().__init__(*args,**kwargs)
    
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.start.__signature__ = signature(cls._start_action)
        cls.stop.__signature__ = signature(cls._stop_action)
        

    def _timeout_action(self):
        # if this returns True, then the timeout will not be performed
        pass
    
    def _error_handler(self, exc_type, exc_val, exc_tb):
        # this can return True value to suppress exceptions inside the with
        # statement. by default they are re-raised
        pass
    
    
    @abstractmethod
    def _start_action(self,*args,**kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def _stop_action(self, *args, **kwargs):
        raise NotImplementedError
    
    def start(self, *args, wait=None, **kwargs):
        if self.active:
            raise RuntimeError("TimedObject %s cannot be started as it "
                               "is already active." % str(self))
        self.active = True
        ret = self._start_action(*args,**kwargs)
        if self.measure_duration: self.starttime = time.time()
        if self.timeout:
            self._timeout_thread = launch.thread(self._timeout_stop,
                    initial_time_delay=self.timeout)
        self.start_flag.set()
        self.start_flag.clear()
        if wait is None and self.wait or wait is True: self.join()
        if ret is None: ret = self #usually the case
        return ret
        
    def _timeout_stop(self):
        if self.active:
            if self._timeout_action() is True:
                self._timeout_thread = None
            else:
                self.stop("timeout")
                self._timeout_thread = True
    
    def stop(self, exitcode = None, *args, raise_errors = True, **kwargs):
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
            if self.measure_duration: self.endtime = time.time()
            self.exitcode = exitcode
            ret = self._stop_action(*args,**kwargs)
            self.stop_flag.set()
            self.stop_flag.clear()
            if ret is None and self.measure_duration: return self.duration()
            return ret


    def duration(self):
        if not self.measure_duration: raise ValueError
        if self.starttime is None: return 0
        t = self.endtime if self.endtime else time.time()
        return t-self.starttime



    def __enter__(self):
        return self.start(wait=False)

  
    def __exit__(self, *error_info):
        if self.active: self.stop("__exit__")
        return self._error_handler(*error_info)
    
    def join(self, timeout=None):
        if self.active is not True: return False
        self.stop_flag.wait(timeout)
        return True
        



class AdditionContainerAddend:

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
        
    
    @property
    def members(self):
        return (self,)
       
    

class AdditionContainer:
    
    # must be set in the subclass:
    basic_class = None
    _methods_to_include = {}
    Addend = AdditionContainerAddend
    
    @property
    def members(self):
        return self._members
    
    def __init_subclass__(cls, basic_class=None, ordered=True):
        if basic_class is None:
            raise ValueError("Keyword argument basic_class required.")
        if not issubclass(basic_class, cls.Addend): raise TypeError
        cls.basic_class = basic_class
        cls.ordered=ordered
        basic_class.ContainerClass = cls
        for method_name, error_type in cls._methods_to_include.items():
            if not issubclass(error_type,Exception): raise TypeError
            setattr(cls, method_name, cls._create_combined_method(
                    method_name, error_type))
    
    
    def __init__(self, *args):
        self._members = []
        for arg in args:
            if isinstance(arg, self.__class__):
                self._members += arg._members
            elif isinstance(arg, self.basic_class):
                self._members += [arg]
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
                self._members)
        return True in booleans

    def __enter__(self):
        for m in self._members:
            m.__enter__()
        return self
    
    def __bool__(self):
        x = sum(bool(m) for m in self._members)
        return x > 0

        
    @staticmethod
    def _create_combined_method(method_name, error_type):
        def combined_method(self, *args, **kwargs):
            for member in self._members:
                try:
                    method = getattr(member,method_name)
                except AttributeError:
                    continue
                try:
                    return method(*args, **kwargs)
                except error_type:
                    continue
            raise error_type(f"Arguments {args, kwargs} not allowed for "
                    f"method {method_name} of AdditionObject {self}")
        return combined_method