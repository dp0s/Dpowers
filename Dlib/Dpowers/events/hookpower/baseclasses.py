#
#
# Copyright (c) 2020-2023 DPS, dps@my.mail.de
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
from warnings import warn
from Dhelpers.baseclasses import AdditionContainer, TimedObject
from Dhelpers.container import container
from Dhelpers.arghandling import check_type
from abc import ABC, abstractmethod
import threading, queue, logging, inspect, functools, traceback
from ..event_classes import MouseMoveEvent
from Dhelpers.named import NamedObj

class CallbackRunnerThread(threading.Thread):
    pass

class EventQueueThread(threading.Thread):
    pass


class EventQueueReader:
    def __init__(self):
        # create useless dead thread just to make all the attributes available:
        self.callback_runner_thread = EventQueueThread()
        self.event_queue = queue.Queue()
    
    def start(self):
        if not self.callback_runner_thread.is_alive():
            self.callback_runner_thread = EventQueueThread(
                    target=self.run_callbacks)
            self.callback_runner_thread.start()
            return self.callback_runner_thread
    
    def run_callbacks(self):
        while True:
            handler, event_obj = self.event_queue.get()
            handler.run_callbacks(event_obj)




class InputEventHandler(ABC):
    
    # base class to create Capturer and Collector classes
    
    reinject_implemented = False
    capture_allowed = True  #need to be manually activated
    collect_allowed = True  #need to be manually activated
    
    def __init__(self, hook_cls=None):
        self.hook_cls = hook_cls  #this attribute can be left None as it will
        # usually be defined by __init_subclass__ method of CallbackHook class
        self.collect_active = False
        self.capture_active = False
        self.active_hooks = []
        self.cap_num = 0


    def add_hook(self, hook):
        ah = self.active_hooks
        ah.append(hook)
        ah.sort(key=lambda s: s.priority)
        if len(ah) == 1:
            if self.collect_active: raise RuntimeError
            self.collect_active = True
            self.start_collecting()
            return True

    def remove_hook(self, hook):
        self.active_hooks.remove(hook)
        if len(self.active_hooks) == 0:
            if not self.collect_active: raise RuntimeError
            self.collect_active = False
            self.stop_collecting()
            return True
    
    def add_capturer(self):
        self.cap_num += 1
        if self.cap_num == 1:
            if self.capture_active: raise RuntimeError
            self.capture_active = True
            self.start_capturing()
            return True

    def remove_capturer(self):
        self.cap_num -= 1
        if self.cap_num == 0:
            if not self.capture_active: raise RuntimeError
            self.capture_active = False
            self.stop_capturing()
            return True
        
        
    def start_collecting(self):
        # must be non_blocking
        raise NotImplementedError
        
    def stop_collecting(self):
        pass


    def start_capturing(self):
        # must be non_blocking
        raise NotImplementedError

    def stop_capturing(self):
        pass
        
    
    def queue_event(self, *args, **kwargs):
        try:
            cls = self.hook_cls
            event_obj = cls._create_event_obj(*args, **kwargs)
            if cls.reinject_active:
                ret = cls._active_reinject_func(event_obj)
                #print(ret, cls._active_reinject_func)
                if ret is None: raise ValueError
            else:
                ret = None
            cls.queue_reader.event_queue.put((self,event_obj))
            return ret
        except Exception as e:
            warn(f"\nEmergency stop {self.hook_cls}.\n{repr(e)}")
            try:
                self.hook_cls.capturer.stop()
            except Exception:
                pass
            try:
                self.stop_collecting()
            except Exception:
                pass
            try:
                self.stop_capturing()
            except Exception:
                pass
            traceback.print_exc()
    
    def run_callbacks(self, event_obj):
        if event_obj is None: return
        for hook in self.active_hooks:
            ret = hook.run_callback(event_obj)
            if ret == "block": break
            
            
    
    

class Missing: pass
    
    
class CallbackHook(AdditionContainer.Addend, TimedObject):
    
    # usually set by __init_subclass__ or subclass attribute. In these cases,
    # there is at most one handler instance for each subclass.
    # They can optionally be set for a particular Hook instance, in which
    # case this instance has it's own handler available (CustomHook subclass
    # uses this for evdev)
    handler = None
    
    @property
    def capture_allowed(self):
        return self.handler.capture_allowed
        
    @property
    def collect_allowed(self):
        return self.handler.collect_allowed
    
    
    queue_reader = EventQueueReader()
    # this should usually never be overwritten as all subclasses
    # should use a single Thread for executing the callbacks. If a
    # subclass defines a seperate instance of EventQueueReader, its
    # callbacks will be run in a separate thread
    
    def __init_subclass__(cls):
        cls._active_capturers = 0
        cls._active_reinject_func = None
        cls.reinject_active = False
        handler = cls.handler
        if handler is not None:
            check_type(InputEventHandler, handler)
            if handler.hook_cls is None: handler.hook_cls = cls
            if handler.hook_cls is not cls: raise ValueError
        cls.__init__.__signature__ = inspect.signature(cls.init)



    def __init__(self, *args, **kwargs):
        self._init_kwargs = self._swallow_args(*args,**kwargs)
        self.init(**self._init_kwargs)
    
    @staticmethod
    def _swallow_args(callback_func=Missing,timeout=Missing, **kwargs):
        # btw: makes sure that no positional arg is also specified in kwargs
        if callback_func is not Missing: kwargs["callback_func"]=callback_func
        if timeout is not Missing: kwargs["timeout"] = timeout
        return kwargs
    
    def init(self, callback_func = False, timeout = 60, *, capture: bool =
            False, reinject_func = None, priority: int  = 0,
            dedicated_thread=False, **custom_kwargs):
        super().__init__(timeout=timeout)
            # this defines the attributes timeout, active
        if callback_func is None:
            callback_func = lambda *args: None
        elif not callable(callback_func) and callback_func is not False:
            raise TypeError("callback_func must be callable, False or None")
        else:
            argcount = callback_func
        check_type(int, priority)
        check_type(bool, capture)
        self.callback_func = callback_func
        self.priority = priority
        self.reinject_func = reinject_func
        self.capture = capture
        self.custom_kwargs = custom_kwargs
        self.dedicated_thread = dedicated_thread
        self.process_custom_kwargs(**custom_kwargs)
        if self.callback_func and not self.collect_allowed: raise ValueError
        if reinject_func is not None:
            if self.handler.reinject_implemented is False:
                raise NotImplementedError(
                    "The following hook implementation does not support "
                    "reinjecting:\n" + str(self.__class__))
            if callback_func is False:
                self.callback_func = lambda *args: None
            self.capture = True
            if not callable(reinject_func):
                self.reinject_func = lambda *args: reinject_func
        if self.capture is True and not self.capture_allowed:
            raise NotImplementedError(
                    "The following hook implementation does not support "
                    "capturing:\n" + str(self.__class__))
    
    def __call__(self, *args, _reuse=True, **kwargs):
        """Create a copy, Adding left out arguments.
        For a useful example of successively adding argument see
        Dpowers.events.waiter.Keywaiter class."""
        if not _reuse: return self.__class__(*args,**kwargs)
        newkwargs = self._init_kwargs.copy()
            #this includes initial *args and **kwargs values
        newkwargs.update(self._swallow_args(*args, **kwargs))
            #this will overwrite inital *args and **kwargs value
        return self.__class__(**newkwargs)

    def __bool__(self):
        return self.callback_func is not False or self.capture is True

        
    def process_custom_kwargs(self, **kwargs):
        if not kwargs: return
        raise NotImplementedError(f"Hook {self} does not accept custom kwargs.")


    # this method is called from cls.collector instance to run the callbacks
    def run_callback(self, event_obj):
        if self.callback_func is None: return
        event_obj = self.callback_condition(event_obj)
        if event_obj is None: return
        # logging.info("calling function %s with argument %s.",
        #       self.callback_func, event_obj)
        if self.dedicated_thread:
            CallbackRunnerThread(target=self.callback_func,
                    args=(event_obj,)).start()
        else:
            ret = self.callback_func(event_obj)
            # this is where the callback is actually executed. Can
            # take some while
            if ret == "stop": self.stop()
            return ret
    
    #start method is defined in TimedObj Baseclass and will use this:
    def _start_action(self):
        cls = self.__class__
        if self.reinject_func is not None:
            if cls._active_reinject_func is None:
                cls._active_reinject_func = self.reinject_func
            else:
                raise RuntimeError("Multiple reinject functions set for the "
                        "same hook class:\n" + str(cls))
        if self.capture:
            cls._active_capturers += 1
            cls._update_reinject()
            self.handler.add_capturer()
        if self.callback_func is not False:
            self.queue_reader.start()  # just in case the queue_reader has
            # somehow been stopped, lets recheck everytime
            self.handler.add_hook(self)

    # stop method is defined in TimedObj Baseclass and will use this:
    def _stop_action(self):
        cls = self.__class__
        if self.reinject_func is not None:
            cls._active_reinject_func = None
        if self.capture:
            cls._active_capturers -= 1
            cls._update_reinject()
            self.handler.remove_capturer()
        if self.callback_func is not False:
            self.handler.remove_hook(self)
    
    def _timeout_action(self):
        warn("Timeout after %s seconds: Stopping hook %s." % (
            self.timeout,self))
        
    @classmethod
    def _update_reinject(cls):
        cls.reinject_active = cls._active_reinject_func is not None and \
                              cls._active_capturers == 1


    # @classmethod
    # def queue_event(cls, *args, **kwargs):
    #     event_obj = cls._create_event_obj(*args, **kwargs)
    #     if cls.reinject_active:
    #         ret = cls._active_reinject_func(event_obj)
    #         if ret is None: raise ValueError
    #     else:
    #         ret = None
    #     cls.queue_reader.event_queue.put((cls, event_obj))
    #     return ret

    

    # @classmethod
    # def _run_callbacks(cls, event_obj):
    #     if event_obj is None: return
    #     for self in cls.active_callbacks:
    #         if self.callback_func is None or not self.callback_condition(
    #                 event_obj): continue
    #         logging.info("calling function %s with argument %s.",
    #                 self.callback_func, event_obj)
    #         ret = self.callback_func(event_obj)
    #         # this is where the callback is actually executed. Can
    #         # take some while.
    #         if ret == "block": break
    #         if ret == "stop": self.stop()


    # the following method is called by the cls.collector instance to create
    # event objects.
    @classmethod
    @abstractmethod
    def _create_event_obj(cls, *args, **kwargs):
        raise NotImplementedError


    def callback_condition(self, event_obj):
        # can be overridden in subclass.
        return event_obj


class NamedHook(CallbackHook):
    NamedClass = None   #set by target_modifier of HookAdaptor
    EventClass = None
    name_translation_dicts = None
    #name_translation_dict = None
    _active_dict = {}
    
    
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        if hasattr(cls, "name_translation_dict"):
            if len(cls.name_translation_dicts) != 0: raise AttributeError
            cls.name_translation_dicts = [cls.name_translation_dict]
        else:
            cls.name_translation_dicts = []

    @classmethod
    def update_active_dict(cls):
        # this has to be called after cls.NamedClass has been set
        for i in range(len(cls.name_translation_dicts)):
            dic = cls.name_translation_dicts[i]
            StandardizingDict = cls.NamedClass.StandardizingDict
            if not isinstance(dic, StandardizingDict):
                check_type(dict, dic)
                cls.name_translation_dicts[i] = StandardizingDict(dic)
        coll = cls.handler
        if coll is None: return
        check_type(InputEventHandler, coll)
        try:
            final_dict = coll.name_dict.copy()
        except AttributeError:
            final_dict = {}
        if hasattr(coll, "names"):
            for n in coll.names:
                if n not in final_dict: final_dict[n] = n
    
        for a, b in final_dict.items():
            for dic in cls.name_translation_dicts:
                try:
                    b = dic[b]
                except KeyError:
                    pass
            try:
                final_dict[a] = cls.NamedClass.instance(b)
            except KeyError:
                final_dict[a] = b
        cls._active_dict = final_dict  # this is used each time a key is
        # pressed. It  # is not standardizing to save time.
        
        
    @classmethod
    def _create_event_obj(cls, name, **kwargs):
        effective = cls._active_dict.get(name, name)
        NamedCl = cls.NamedClass
        if NamedCl is None:
            return cls.EventClass(effective, **kwargs)
        else:
            try:
                EventCl = NamedCl.Event
            except AttributeError:
                EventCl = cls.EventClass
            else:
                if cls.EventClass is not None: assert cls.EventClass is EventCl
                if isinstance(effective, NamedCl) and hasattr(effective,
                        "get_event"):
                    return effective.get_event(**kwargs)
            event_obj = EventCl(effective, **kwargs)
            # print(event_obj, event_obj.named_instance, event_obj.press)
            if not event_obj.named_instance:
                if not (event_obj.startswith("[")):
                    warn("hook of type" + str(
                            cls) + "got unknown key/button name:  " + event_obj)
                    if not event_obj.endswith("_rls"):
                        i = event_obj.lower()
                        container.set_temp_store_key("F12_send",
                                i + " = NamedKey('" + i + "')")
            return event_obj



class PressReleaseHook(NamedHook):
    
    currently_pressed = None
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.currently_pressed = set()
        

    def init(self, *args, press=True, release = True, write_rls=True, **kwargs):
        super().init(*args, **kwargs)
        self.press = press
        self.release = release
        self.multipress = True
        self.write_rls=write_rls
        
    
    def _stop_action(self):
        super()._stop_action()
        if not self.handler.active_hooks:
            self.__class__.currently_pressed = set()


    @classmethod
    def _create_event_obj(cls, name, press, **kwargs):
        return super()._create_event_obj(name,press=press, **kwargs)
    
    
    def callback_condition(self, event_obj):
        if event_obj.press is True:
            if not self.multipress and event_obj.multipress: return
            if self.press: return event_obj
        elif event_obj.press is False:
            if self.release:
                if self.write_rls: return event_obj
                return event_obj.strip_rls()
        else:
            return event_obj  #this happens for scroll events



class KeyhookBase(PressReleaseHook):
    
    
    def init(self, *args, allow_multipress=False, **kwargs):
        super().init(*args, **kwargs)
        if allow_multipress and not self.press: raise ValueError
        self.multipress = allow_multipress
        
    @classmethod
    def _create_event_obj(cls, name, *args, press, **kwargs):
        event_obj = super()._create_event_obj(name, *args, press=press,
                **kwargs)
        info=event_obj.name
        if event_obj.press is True:
            if info in cls.currently_pressed:
                event_obj.multipress = True
            else:
                event_obj.multipress = False
                cls.currently_pressed.add(info)
        else:
            try:
                cls.currently_pressed.remove(info)
            except KeyError:
                pass
        return event_obj


class ButtonhookBase(PressReleaseHook):
    pass


class CursorhookBase(CallbackHook):
    @classmethod
    def _create_event_obj(cls, *args,**kwargs):
        return MouseMoveEvent(*args, **kwargs)


class DefaulthookBase(CallbackHook):
    
    @classmethod
    def _create_event_obj(cls, *args):
        return args




@CallbackHook.register  #ABC classes allow registering as virtual subclass
class HookContainer(AdditionContainer, basic_class=CallbackHook, ordered=False):
    """
    This class shall synchronize the use of several hooks if you add them.
    """
    
    def __init__(self, *args):
        super().__init__(*args)
        self._members = list(m() for m in self._members)
        #this will creat a copy of all hook instances so that the
        # HookContainer Version is independent from the basic version

    def start(self):
        return tuple(m.start() for m in self._members)
    
    def stop(self):
        errors = []
        for m in self._members:
            try:
                m.stop()
            except RuntimeError as e:
                errors += [e]
        if errors:
            raise RuntimeError(str(errors))
        
    
    def join(self):
        return tuple(m.join() for m in self._members)
    
    @functools.wraps(CallbackHook.__call__)
    def __call__(self, *args, **kwargs):
        return self.__class__(*tuple(m(*args, **kwargs) for m in self._members))