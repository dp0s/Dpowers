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



from .baseclasses import (InputEventHandler, KeyhookBase, ButtonhookBase,
    CursorhookBase, PressReleaseHook)
from ..event_classes import PressReleaseEvent

from Dhelpers.adaptor import DependencyManager

with DependencyManager(__name__) as manager:
    device_control = manager.import_module("evdev_prepared.device_control")
    uinput = manager.import_module("evdev_prepared.uinput")


# the following import will not be performed if the DependencyManager is only
# checking the import capability. if evdev is not installed, an error will
# be raised when trying to import evdev_prepared already.
from evdev.ecodes import (EV_KEY, EV_ABS, EV_SYN, EV_MSC, KEY, BTN,
    EV_LED, EV_REL, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_X, ABS_Y,
    REL_X, REL_Y, bytype)

class EvdevHandler(device_control.DeviceHandler, InputEventHandler):
    
   
    devupdater = device_control.DeviceUpdater()
    # this class will also use the CollactableInputDevice class and the
    # EvdevInputLooper class in the background
    uinput = uinput.global_uinput
    uinput.start()
    
    def __init__(self, hook_cls=None, **selection_kwargs):
        InputEventHandler.__init__(self,hook_cls)
        device_control.DeviceHandler.__init__(self,devupdater= self.devupdater,
                **selection_kwargs)
    
    def process_event(self, ty, co ,val, dev):
        if ty == EV_SYN: return
        press = bool(val != 0)
            # val==0 means that it was released, val==1 or
            # val==2 means it is pressed
        name = bytype[ty][co]
        if isinstance(name, (list,tuple)): name = name[0]
        self.queue_event(name.lower(), press=press)
    
    
    
    

class KeyHandler(EvdevHandler):
    
    reinject_implemented = True
    
    
    name_dict = {}
    for a, b in KEY.items():
        if isinstance(b, list): b = b[0]
        b = b[4:].lower()
        name_dict[a] = b
            
    def process_event(self,ty,co,val, dev):
        #_print(ty,co,val,dev)
        if ty == EV_KEY:
            press = bool(val != 0)
            if self.queue_event(co, press=press) is True:
                self.uinput.write(ty, co, val)
        elif ty not in (EV_SYN, EV_MSC, EV_LED):
            raise TypeError("Wrong event type: ", ty, co , val)
        
        

class ButtonHandler(EvdevHandler):
    
    capture_allowed = False
    
    name_dict = {}
    for a, b in BTN.items():
        if isinstance(b, list): b = b[0]
        b = b[4:].lower()
        name_dict[a] = b

    def process_event(self, ty, co, val, dev):
        #print(ty,co,val)
        if ty == EV_KEY:
            press = bool(val != 0)
            self.queue_event(co, press=press)
        elif ty not in (EV_SYN, EV_MSC, EV_ABS, EV_REL):
            _print("Wrong event type: ", ty, co ,val)


class CursorHandler(EvdevHandler):
    
    capture_allowed = False

    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
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


class EvdevhookMixin:
    
    def process_custom_kwargs(self,  **selection_kwargs):
        if not selection_kwargs: return
        # create a new collector or capturer instance with updated
        # selection_kwargs
        old = self.handler
        cls = EvdevHandler if not old else old.__class__
        new = cls(self.__class__, **selection_kwargs)
        if old != new: self.handler = new
        
            
    def matching_devs(self):
        return self.handler.matching_devs()
    
    def collected_devs(self):
        return self.handler.collected_devs
    
    def captured_devs(self):
        return self.handler.grabbed_devs



class Keyhook(EvdevhookMixin, KeyhookBase):
    handler = KeyHandler(category="keyboard")

    name_translation_dict = {"braceleft": "bracketleft", "braceright":
        "bracketright"}
    

class Buttonhook(EvdevhookMixin, ButtonhookBase):
    handler = ButtonHandler(category="mouse")

class Cursorhook(EvdevhookMixin, CursorhookBase):
    handler = CursorHandler(category="mouse")


class Customhook(EvdevhookMixin, PressReleaseHook):
    
    EventClass = PressReleaseEvent
    
    # collector is set via process_custom_kwargs (see above)
    
    def process_custom_kwargs(self, **selection_kwargs):
        if not selection_kwargs:
            selection_kwargs = {"exclude_category": ("mouse", "keyboard")}
        super().process_custom_kwargs(**selection_kwargs)