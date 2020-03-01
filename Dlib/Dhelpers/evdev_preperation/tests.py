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
import re

def check_uinput():
    from evdev.uinput import UInput
    UInput()  # this will raise an error if /dev/uinput is not writable


# the following check is performed automatically if importing the
# evdev_preperation.input_dev module.
def check_evdev_input_devices(device_dir='/dev/input'):
    from evdev import list_devices, InputDevice
    # the following is taken from evdev.evtest.select_devices()
    
    
    def devicenum(device_path):
        digits = re.findall('\d+$', device_path)
        return [int(i) for i in digits]
    devices = sorted(list_devices(device_dir), key=devicenum)
    devices = [InputDevice(path) for path in devices]
    
    if not devices:
        msg = 'error: no input devices found (do you have rw permission ' \
              'on %s/*?)'
        raise IOError(msg%device_dir)
    return devices