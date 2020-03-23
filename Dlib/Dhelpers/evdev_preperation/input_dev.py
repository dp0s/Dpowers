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
from evdev import ecodes, InputDevice, uinput
from ..launcher import launch
import selectors

class EvdevDeviceGrabError(Exception):
    pass

class AdhancedInputDevice(InputDevice):
    
    #_error_msg = "AdhancedInputDevice object was already created. Use " \
    #             "AdhancedInputDevice.get() instead of multiple calls of " \
    #             "AdhancedInputDevice() "
    
    def __init__(self, path):
        super().__init__(path)
        self.was_grabbed = False
        self.is_collected = False
        self.category = self.get_category()
        self.collected_by = []
        self.grabbed_by = []
    
    # def __eq__(self, other):
    #     if not isinstance(other, InputDevice):
    #         return NotImplemented
    #     if super().__eq__(other) and self.path == other.path:
    #         return True
    #     return False
    #
    # def __hash__(self):
    #     # this is to make AdhancedInputDevice available for sets and dicts
    #     return hash(self.path)
    
    def __str__(self):
        return super().__str__() + f', fd={self.fd}, category "{self.category}"'



    def get_category(self):
        if "uinput" in self.name: return "uinput"
        devcaps = self.capabilities()
        keylist = devcaps.get(ecodes.EV_KEY)
        if keylist is not None:
            # print(dev.capabilities(verbose=True))
            if ecodes.BTN_LEFT in keylist: return "mouse"
            if len(keylist) > 10: return "keyboard"
            if ecodes.KEY_POWER in keylist: return "power_button"
            if ecodes.KEY_BRIGHTNESSDOWN in keylist: return "brightness_keys"
        else:
            switchlist=devcaps.get(ecodes.EV_SW)
            if ecodes.SW_LID in switchlist: return "lid_switch"
            if ecodes.SW_HEADPHONE_INSERT in switchlist: return \
                "headphone_switch"
        return NotImplemented
    
    def grab(self, release_keys=True, grabber=None):
        if self.was_grabbed:
            raise EvdevDeviceGrabError("Device was already grabbed by this "
                                       "process.")
        if release_keys: self.release_all()
        if grabber:
            if grabber in self.grabbed_by: raise ValueError
            if not self.grabbed_by: self.test_grab(ungrab=False)
            self.grabbed_by.append(grabber)
            # if it has already been grabbed, just add a new grabber
        else:
            return self.test_grab(ungrab=False)
    
    
    def test_grab(self, ungrab=True, raise_error=True):
        try:
            InputDevice.grab(self)
        except OSError as e:
            if raise_error:
                raise EvdevDeviceGrabError(str(self) + "--  seems to be already "
                            "grabbed by another process.") from e
            return False
        else:
            return True
        finally:
            if ungrab:
                InputDevice.ungrab(self)
            else:
                self.was_grabbed = True
    
    
    def ungrab(self, grabber=None):
        if grabber:
            self.grabbed_by.remove(grabber)
            if self.grabbed_by:
                return  #this means that there is still another grabber
        try:
            InputDevice.ungrab(self)
        except OSError:
            pass
        finally:
            self.was_grabbed = False
            
    
    
    def syn(self):
        """weirdly, the InputDeviceClass features a write method, but not a
        syn method. This way, we can actually inject input using the
        InputDevice - without using a seperate Uinput instance.
        WARNING: If the device is grabbed, this changes the internal state of
        the key, but the event is not passed on to the system. In this case,
        a uinput tool is needed. Use self.test_grab to check this."""
        uinput.UInput.syn(self)
        
    def release_all(self):
        self.syn()
        for keycode in self.active_keys():
            # release the active keys:
            self.write(ecodes.EV_KEY, keycode, 0)
        self.syn()
    
    # def close(self):
    #     try:
    #         super().close()
    #     except RuntimeError:
    #         pass
    #     #this is necessary because in the latest evdev version, close will
    #     # automatically use some of the async stuff, which I don't want!


class CollectableInputDevice(AdhancedInputDevice):
    
    _inputevent_looper = None

    
    def collect(self, collector=None):
        if collector:
            if collector in self.collected_by: raise ValueError
            if not self.collected_by: self._start_collect()
            self.collected_by.append(collector)
        else:
            self._start_collect()
            
    
    def _start_collect(self):
        #actually start it
        if self.is_collected:
            raise RuntimeError("Tried to collect following device multiple "
                               "times:\n%s"%str(self))
        if not self.was_grabbed:
            self.test_grab()  # checking if another process has already  #
            # taken control of this device and raise error if yes
        self.is_collected = True
        while self.read_one() is not None:
            pass  # this will read out all left over events before  #
            # starting the actual hook
        self._inputevent_looper.start(self)
        
    def uncollect(self, collector=None):
        if collector:
            self.collected_by.remove(collector)
            if self.collected_by:
                return  #this means that there is still another collector
        if not self.is_collected: raise RuntimeError
        self.is_collected = False
        self._inputevent_looper.stop(self)
        
        
    def process(self,event):
        ty, co, val = event.type, event.code, event.value
        for handler in self.collected_by:
            handler.process_event(ty,co,val, self)




class EvdevInputLooper:
    
    _running_number = 0
    
    def __init__(self):
        self.running_number = self._running_number
        self.__class__._running_number += 1
        self.collected_devs = []
        self.selector = None
        self.loop_thread = None
        self.DeviceClass = type(f"CollectableInputDevice_for_looper_"
            f"{self.running_number}", (CollectableInputDevice,),{})
        # create a dedicated subclass
        self.DeviceClass._inputevent_looper = self
    
    def start(self, dev):
        #print(dev, self.collected_devs)
        if not self.collected_devs:
            self.collected_devs.append(dev)
            self.selector = selectors.DefaultSelector()
            self.loop_thread = launch.thread(self.run_loop)
        else:
            if dev in self.collected_devs: raise ValueError
            self.collected_devs.append(dev)
        #_print("Start collecting from", dev)
        self.selector.register(dev, selectors.EVENT_READ)
    
    
    def stop(self, dev):
        #_print("Stopp collecting from", dev)
        self.selector.unregister(dev)
        self.collected_devs.remove(dev)
    
    def run_loop(self):
        # print("run")
        while self.collected_devs:
            for key, mask in self.selector.select(timeout=0.1):
                # timeout is necessary to check the loop condition regularly
                # even if no key is pressed. In this case select will
                # return an emtpy list and the for loop is skipped
                device = key.fileobj
                # print(key, mask, device)
                try:
                    events = tuple(device.read())
                except OSError:
                    # this happens if device was removed and cannot be found
                    self.stop(device)
                    continue
                for event in events: device.process(event)
        self.selector.close()
    
    def selected_devices(self):
        return tuple(key.fileobj for key in self.selector.get_map().values())
    
    def __repr__(self) -> str:
        old = super().__repr__()[:-1]
        return old + f" with running number {self.running_number}>"

    # def process_event(self, event, dev):  #     #
    # self.hook_class.queue_event(categorize(event), dev)  #     ty, co,
    # val = event.type, event.code, event.value  #     if ty == EV_KEY:  #
    # dev.queue_keybutton(co,val)  #     elif ty == EV_ABS:  #
    # dev.queue_cursor(co,val)  #     elif ty not in (EV_SYN, EV_MSC,
    # EV_LED):  #         raise TypeError("Wrong event type: ", event,
    # ty)  #     #print(ty,co,val)  #     #dev.queue_key()
