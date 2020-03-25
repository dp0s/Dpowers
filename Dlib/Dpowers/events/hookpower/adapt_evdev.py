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

from evdev.ecodes import (EV_KEY, EV_ABS, EV_SYN, EV_MSC, KEY, BTN,
    EV_LED, EV_REL, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_X, ABS_Y,
    REL_X, REL_Y)
from evdev_prepared import uinput, dev_updater

from .baseclasses import (InputEventHandler, KeyhookBase, ButtonhookBase,
    CursorhookBase, CustomhookBase)
from abc import abstractmethod





class EvdevHandler(InputEventHandler):
    
    devupdater = dev_updater.EvdevDeviceUpdater(activate_looper=True)
    # this class will also use the CollactableInputDevice class and the
    # EvdevInputLooper class in the background
    uinput = uinput.global_uinput
    uinput.start()
    
    def __init__(self, hook_cls=None, *, category=None, name=None, path=None,
            selection_func=None):
        super().__init__(hook_cls)
        self.category = category
        self.name = name
        self.path = path
        self.selection_func = selection_func
        self.matched_devs = []
        self.devupdater.change_actions.append(self.dev_change_action)
        
    def properties(self):
        return self.category, self.name, self.path, self.selection_func
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.properties() == other.properties()
        elif isinstance(other, (tuple,list)) and len(other)==4:
            return self.properties() == other
        return NotImplemented
    
    def dev_is_selected(self, dev):
        if self.selection_func is not None:
            return self.selection_func(dev.category, dev.name, dev.path)
        if dev.category == "uinput" and self.category != "uinput":
            return False
        if self.category is not None and dev.category != self.category:
            return False
        if self.name is not None and self.name not in dev.name:
            return False
        if self.path is not None and self.path not in dev.path:
            return False
        return True
    
    def matching_devs(self):
        return tuple(dev for dev in self.devupdater.all_devs
            if self.dev_is_selected(dev))

    def dev_change_action(self, found_new, lost_devs):
        # this way, the EvdevHandler will automatically register newly
        # appearing devs and release disappearing devs
        if not self.active: return
        for dev in lost_devs:
            if dev in self.matched_devs:
                self.stop_dev(dev)
                self.matched_devs.remove(dev)
        for dev in found_new:
            if self.dev_is_selected(dev):
                self.start_dev(dev)
                self.matched_devs.append(dev)
    
    def run(self):
        self.matched_devs = self.matching_devs()
        #print(self.matched_devs)
        for dev in self.matched_devs: self.start_dev(dev)
            
    
    def terminate(self):
        for dev in self.matched_devs: self.stop_dev(dev)
        self.matched_devs = []
        
    @abstractmethod
    def start_dev(self, dev):
        pass
    
    @abstractmethod
    def stop_dev(self, dev):
        pass
        
class Capturer(EvdevHandler):
    
    def start_dev(self, dev):
        dev.grab(grabber=self)

    def stop_dev(self, dev):
        dev.ungrab(grabber=self)



class Collector(EvdevHandler):
    
    def start_dev(self, dev):
        dev.collect(collector=self)

    def stop_dev(self, dev):
        dev.uncollect(collector=self)
        
    def process_event(self, ty, co ,val, dev):
        self.queue_event((ty,co,val), dev)
        
        
        
class KeyCollector(Collector):
    
    reinject_implemented = True
    
    
    name_dict = {}
    for a, b in KEY.items():
        if isinstance(b, list): b = b[0]
        b = b[4:].lower()
        name_dict[a] = b
            
    def process_event(self,ty,co,val, dev):
        if ty == EV_KEY:
            press = bool(val != 0)  # val==0 means that it was released, val==1 or
            # val==2 means it is pressed
            if self.queue_event(co, press=press) is True:
                self.uinput.write(ty, co, val)
        elif ty not in (EV_SYN, EV_MSC, EV_LED):
            raise TypeError("Wrong event type: ", ty, co , val)

class ButtonCollector(Collector):
    
    name_dict = {}
    for a, b in BTN.items():
        if isinstance(b, list): b = b[0]
        b = b[4:].lower()
        name_dict[a] = b

    def process_event(self, ty, co, val, dev):
        #print(ty,co,val)
        if ty == EV_KEY:
            press = bool(val != 0)  # val==0 means that it was released, val==1 or
            # val==2 means it is pressed
            self.queue_event(co, press=press)
        elif ty not in (EV_SYN, EV_MSC, EV_ABS, EV_REL):
            _print("Wrong event type: ", ty, co ,val)


class CursorCollector(Collector):
    
    

    def __init__(self, hook_cls=None, *, category=None, name=None, path=None,
            selection_func=None):
        super().__init__(hook_cls, category=category, name=name, path=path,
                selection_func=selection_func)
        self.saved_vals = {}
        
    def _intelligent_collect(self, co ,co_x, co_y, val, **kwargs):
        if co == co_x:
            try:
                pos_old = self.saved_vals.pop(co_y)
            except KeyError:
                self.saved_vals[co_x] = val
            else:
                self.queue_event(val, pos_old, **kwargs)
                return True
        elif co == co_y:
            try:
                pos_old = self.saved_vals.pop(co_x)
            except KeyError:
                self.saved_vals[co_y] = val
            else:
                self.queue_event(pos_old, val, **kwargs)
                return True
            
    def process_event(self, ty, co, val, dev):
        # print(ty,co,val)
        if ty == EV_KEY:
            pass
        elif ty == EV_ABS:
            self._intelligent_collect(co, ABS_X, ABS_Y, val,
                    screen_coordinates=False)
        elif ty == EV_REL:
            self._intelligent_collect(co,REL_X, REL_Y, val, relative=True,
                    screen_coordinates=False)
        elif ty not in (EV_SYN, EV_MSC):
            _print("Wrong event type: ", ty, co, val)
        
    # def void(self):
    #
    #     if ty == EV_REL:
    #         print("rel", event)
    #     elif ty == EV_ABS:
    #         print("abs", event)
    #
    #     return
    #     print(event.type)
    #     e = categorize(event)
    #     if isinstance(e, SynEvent): return
    #     print(type(e), e)
    #     if isinstance(e, KeyEvent):
    #         k = e.keycode
    #         if isinstance(k, list): k = k[0]
    #         if e.keystate == KeyEvent.key_down:
    #             press = True
    #         elif e.keystate == KeyEvent.key_up:
    #             press = False
    #         elif e.keystate == KeyEvent.key_hold:
    #             # this happens if a key is hold down for
    #             # longer mode. Usually, this will just send
    #             # the key repeatedly. Here, it is ignored.
    #             return
    #         else:
    #             raise ValueError
    #         name = k[4:].lower()
    #         t = k[:4]
    #         if t == "KEY_":
    #             self.queue_key(name, press=press)
    #         elif t == "BTN_":
    #             self.queue_button(name, press=press)
    #         else:
    #             raise NameError
    #     elif isinstance(e, RelEvent):
    #         if event.code == 8:
    #             if event.value == 1:
    #                 self.queue_button(4, press=True)
    #                 # scroll_up
    #             elif event.value == -1:
    #                 self.queue_button(5, press = True)
    #                 # scroll_down
    #             else:
    #                 raise ValueError(event.value)
    #         elif event.code == 0:
    #             self.queue_cursor(event.value, 0)
    #         elif event.code == 1:
    #             self.queue_cursor(0, event.value)
    #         else:
    #             raise ValueError(event.code)


class EvdevhookMixin:
    
    def process_custom_kwargs(self,  **kwargs):
        new = Collector(self.__class__, **kwargs)
        old = self.collector
        if not old or old != new:
            self.collector = new
        new = Capturer(self.__class__, **kwargs)
        old = self.capturer
        if not old or old != new:
            self.capturer = new


class Keyhook(EvdevhookMixin, KeyhookBase):
    collector = KeyCollector(category="keyboard")
    capturer = Capturer(category="keyboard")

    name_translation_dict = {"braceleft": "bracketleft", "braceright":
        "bracketright"}
    

class Buttonhook(EvdevhookMixin, ButtonhookBase):
    collector = ButtonCollector(category="mouse")

class Cursorhook(EvdevhookMixin, CursorhookBase):
    collector = CursorCollector(category="mouse")

class Customhook(EvdevhookMixin, CustomhookBase):
    pass
    # collector must be set via custom_kwargs