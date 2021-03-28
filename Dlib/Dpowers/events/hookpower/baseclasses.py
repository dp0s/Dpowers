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
from warnings import warn
from Dhelpers.baseclasses import AdditionContainer, TimedObject
from Dhelpers.container import container
from Dhelpers.arghandling import check_type
from abc import ABC, abstractmethod
import threading, queue, logging, inspect, functools, traceback
from ..event_classes import MouseMoveEvent

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
            # cls is a subclass of CallbackHook
            handler.run_callbacks(event_obj)




class InputEventHandler(ABC):
    
    reinject_implemented = False
    
    def __init__(self, hook_cls=None):
        self.hook_cls = hook_cls
        self.active = False
        self.hook_num = 0
        self.active_hooks = []

    def add_one(self):
        self.hook_num += 1
        if self.hook_num == 1:
            self.start()
            return True

    def remove_one(self):
        self.hook_num -= 1
        if self.hook_num == 0:
            self.stop()
            return True
        
        
    def add_hook(self, hook):
        self.active_hooks.append(hook)
        self.active_hooks.sort(key=lambda s: s.priority)
        self.add_one()

    def remove_hook(self, hook):
        self.active_hooks.remove(hook)
        self.remove_one()
        
        
    def start(self):
        if self.active: raise RuntimeError
        self.active = True
        #self.prepare()
        self.run()
        
    def stop(self):
        if not self.active: raise RuntimeError
        self.active = False
        self.terminate()
            
    @abstractmethod
    def run(self):
        # must be non_blocking
        pass
    
    @abstractmethod
    def terminate(self):
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
                self.stop()
            except Exception:
                pass
            traceback.print_exc()
        

    
    def run_callbacks(self, event_obj):
        if event_obj is None: return
        for hook in self.active_hooks:
            ret = hook.run_callback(event_obj)
            if ret == "block": break
            
    
class CallbackHook(AdditionContainer.Addend, TimedObject):
    
    #these can be overwritten by instance attributes if they depend on
    # instance arguments. However, usually they are set by __init_subclass__
    capturer = None
    collector = None
    
    
    queue_reader = EventQueueReader()
    # this should usually never be overwritten as all subclasses
    # should use a single Thread for executing the callbacks. If a
    # subclass defines a seperate instance of EventQueueReader, its
    # callbacks will be run in a separate thread
    
    def __init_subclass__(cls):
        cls._active_capturers = 0
        cls._active_reinject_func = None
        cls.reinject_active = False
        for handler in (cls.collector, cls.capturer):
            if handler is not None:
                check_type(InputEventHandler, handler)
                if handler.hook_cls is None: handler.hook_cls = cls
                if handler.hook_cls is not cls: raise ValueError
        cls.__init__.__signature__ = inspect.signature(cls.init)



    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs
        self.init(*args, **kwargs)
    
    def init(self, callback_func = False, timeout = 60, *, capture: bool =
            False, reinject_func = None, priority: int  = 0,
            dedicated_thread=False, **custom_kwargs):
        super().__init__(timeout=timeout)
            # this defines the attributes timeout, active
        if callback_func is None:
            callback_func = lambda *args: None
        elif not callable(callback_func) and callback_func is not False:
            raise TypeError("callback_func must be callable, False or None")
        check_type(int, priority)
        check_type(bool, capture)
        self.callback_func = callback_func
        self.priority = priority
        self.reinject_func = reinject_func
        self.capture = capture
        self.custom_kwargs = custom_kwargs
        self.dedicated_thread = dedicated_thread
        if custom_kwargs:
            self.process_custom_kwargs(**custom_kwargs)
            # for the evdev custom hook, this might set the self.capturer and
            # self.collector variables
        if reinject_func is not None:
            if self.collector.reinject_implemented is False:
                raise NotImplementedError(
                    "The following hook implementation does not support "
                    "reinjecting:\n" + str(self.__class__))
            if callback_func is False:
                self.callback_func = lambda *args: None
            self.capture = True
            if not callable(reinject_func):
                self.reinject_func = lambda *args: reinject_func
        if not self.capturer and self.capture is True:
            raise NotImplementedError(
                    "The following hook implementation does not support "
                    "capturing:\n" + str(self.__class__))

        
    def __call__(self, *args, reuse=True, **kwargs):
        """Create a copy, Adding left out arguments.
        For a useful example of successively adding argument see
        Dpowers.events.waiter.Keywaiter class."""
        if not reuse: return self.__class__(*args,**kwargs)
        newargs = list(args)
        for i in range(len(args), len(self._init_args)):
            # this happens if less new args were given than inital args,
            # so we will reuse the old args as much as possible
            newargs.append(self._init_args[i])
        newkwargs = self._init_kwargs.copy()
        newkwargs.update(kwargs)
        return self.__class__(*newargs, **newkwargs)

    def __bool__(self):
        return self.callback_func is not False or self.capture is True

        
    def process_custom_kwargs(self, **kwargs):
        raise NotImplementedError(f"Hook {self} does not accept custom kwargs {kwargs}")

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
            self.capturer.add_one()
        if self.callback_func is not False:
            self.queue_reader.start()  # just in case the queue_reader has
            # somehow been stopped, lets recheck everytime
            self.collector.add_hook(self)

    # stop method is defined in TimedObj Baseclass and will use this:
    def _stop_action(self):
        cls = self.__class__
        if self.reinject_func is not None:
            cls._active_reinject_func = None
        if self.capture:
            cls._active_capturers -= 1
            cls._update_reinject()
            self.capturer.remove_one()
        if self.callback_func is not False:
            self.collector.remove_hook(self)
    
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


    @classmethod
    @abstractmethod
    def _create_event_obj(cls, *args, **kwargs):
        raise NotImplementedError


    def callback_condition(self, event_obj):
        # can be overridden in subclass. event_obj will be adapted for
        # specific instance
        return event_obj
    




class PressReleaseHook(CallbackHook):
    
    NamedClass = None # set by target modifier of HookAdaptor
    
    
    #needs to be overwritten in subclass:
    currently_pressed = None
    name_translation_dicts = None
    _active_dict = None
    

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.currently_pressed = set()
        if hasattr(cls, "name_translation_dict"):
            if len(cls.name_translation_dicts) != 0: raise AttributeError
            cls.name_translation_dicts = [cls.name_translation_dict]
        else:
            cls.name_translation_dicts = []

    def init(self, *args, press=True, release = True, write_rls=True, **kwargs):
        CallbackHook.init(self,*args, **kwargs)
        self.press = press
        self.release = release
        self.multipress = True
        self.write_rls=write_rls
        
    @classmethod
    def update_active_dict(cls):
        #this has to be called after cls.NamedClass has been set
        for i in range(len(cls.name_translation_dicts)):
            dic = cls.name_translation_dicts[i]
            StandardizingDict = cls.NamedClass.StandardizingDict
            if not isinstance(dic, StandardizingDict):
                check_type(dict,dic)
                cls.name_translation_dicts[i] = StandardizingDict(dic)
        coll = cls.collector
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
        cls._active_dict = final_dict #this is used each time a key is pressed. It
                 # is not standardizing to save time.
        
        
    def _stop_action(self):
        super()._stop_action()
        if not self.collector.active_hooks:
            self.__class__.currently_pressed = set()


    @classmethod
    def _create_event_obj(cls, name, press, **kwargs):
        effective = cls._active_dict.get(name,name)
        if isinstance(effective, cls.NamedClass):
            event_obj = effective.get_event(press, **kwargs)
        else:
            event_obj = cls.NamedClass.Event(effective, press=press,
                    **kwargs)
        #print(event_obj, event_obj.named_instance, event_obj.press)
        if not event_obj.named_instance:
            if not (event_obj.startswith("[")):
                warn("hook of type" + str(
                        cls) + "got unknown key/button name:  " + event_obj)
                if not event_obj.endswith("_rls"):
                    i = event_obj.lower()
                    container.set_temp_store_key("F12_send",
                            i + " = NamedKey('" + i + "')")
        return event_obj
    
    
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
        PressReleaseHook.init(self,*args, **kwargs)
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
        elif event_obj.press is False:
            cls.currently_pressed.remove(info)
        return event_obj


class ButtonhookBase(PressReleaseHook):
    pass


class CursorhookBase(CallbackHook):
    @classmethod
    def _create_event_obj(cls, *args,**kwargs):
        return MouseMoveEvent(*args, **kwargs)


class CustomhookBase(CallbackHook):
    
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