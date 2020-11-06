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
from evdev_prepared.uinput import global_uinput
from evdev_prepared.device_control import DeviceSelector
    
global_uinput.start()
names = {}

def select_device(**device_kwargs):
    selector = DeviceSelector(**device_kwargs)
    devs = selector.matching_devs()
    global_uinput.update_from_devices(*devs)
    for name, nums in iterator(devs):
        name = name.lower()
        names[name] = nums
    return devs

def iterator(devs):
    for dev in devs:
        caps = dev.capabilities(verbose=True)
        for event_type,event_list in caps.items():
            if len(event_type) != 2: raise ValueError(event_type)
            ev_type_name = event_type[0]
            ev_type_num = event_type[1]
            if ev_type_name == "EV_SYN": continue
            for entry in event_list:
                if len(entry) != 2: raise ValueError(entry)
                event_num = entry[1]
                nums = ev_type_num, event_num
                name = entry[0]
                if isinstance(name, (tuple, list)):
                    for n in name: yield n, nums
                else:
                    yield name, nums
    
def press(nums):
    ev_type_num, event_num = nums
    global_uinput.write(ev_type_num, event_num, 1)

def rls(nums):
    ev_type_num, event_num = nums
    global_uinput.write(ev_type_num, event_num, 1)