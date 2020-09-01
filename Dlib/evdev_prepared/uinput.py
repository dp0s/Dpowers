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
from evdev import uinput, ecodes, device
from collections import defaultdict


class UinputWrapper:
    """This class allows to use a single fixed uinput object even when
    updating the capatabilities of the underlying original uinput object."""
    
    def __init__(self, **kwargs):
        self.capabilities = defaultdict(set)
        self.capabilities[ecodes.EV_KEY] = set(ecodes.keys.keys())
        self.kwargs = kwargs
        self.filtered_types=(ecodes.EV_SYN, ecodes.EV_FF)
        self.uinput_object = None
        
    def start(self):
        if self.uinput_object is None: self.refresh()
    
    def refresh(self):
        self.close()
        for evtype in self.filtered_types:
            if evtype in self.capabilities: del self.capabilities[evtype]
        self.uinput_object = uinput.UInput(self.capabilities, **self.kwargs)
        
    def update_capabilities(self, capatability_dict):
        for ev_type, ev_codes in capatability_dict.items():
            self.capabilities[ev_type].update(ev_codes)
        self.refresh()
        
    def update_from_devices(self, *devices):
        device_instances = []
        for dev in devices:
            if not isinstance(dev, device.InputDevice):
                dev = device.InputDevice(str(dev))
            device_instances.append(dev)
        for dev in device_instances:
            self.update_capabilities(dev.capabilities())
        self.refresh()
        
    def close(self):
        if self.uinput_object is not None:
            self.uinput_object.close()
            self.uinput_object = None
        
    def syn(self):
        self.uinput_object.syn()

    def write(self, etype, code, value):
        self.uinput_object.write(etype, code, value)
        self.uinput_object.syn()
        
    def write_event(self, event):
        self.uinput_object.write_event(event)
        self.uinput_object.syn()
        
        
        
global_uinput = UinputWrapper(name="py-evdev-uinput-Dhelpers")