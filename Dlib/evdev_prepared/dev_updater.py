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
import time, threading
from evdev import list_devices
from .input_dev import AdhancedInputDevice, EvdevInputLooper
from evdev.ecodes import (EV_KEY, EV_ABS, EV_SYN, EV_MSC, KEY, BTN,
    EV_LED)


class EvdevDeviceUpdater:
    device_folder = "/dev/input"
    InputDevice_cls = AdhancedInputDevice
    
    def __init__(self, autoupdating=True, update_interval=5,
            print_dev_change=True, activate_looper=False):
        if activate_looper:
            self.input_looper = EvdevInputLooper()
            self.InputDevice_cls = self.input_looper.DeviceClass
        self.all_devs = []
        self._autoupdating = False
        self.update_interval = update_interval
        self.change_actions = []
        if print_dev_change: self.change_actions.append(self.print_dev_change)
        self.autoupdating = autoupdating
            # this will trigger self.update_devs if autoupdating is True
        
    
    # upon creation of an InputDevice for a path/device that has already been
    # created, the fileno alias fd can change, which might give problems.
    # I.e. we have two instances of InputDevice for the same path, but with
    # different fd. A typical problem: If one of them is grabbed, the other
    # instance is useless suddenly.
    # The problem is solved below by manually checking if such an InputDevice
    # was already found in the last run of update_devs and replace the new
    # with the old instance to keep the fd identic.
    # NOTE: if a device is disconnected for more than 5s (i.e. until the next
    # run of update_devs), it is "forgotten". so that when the device is
    # reconnected, a fresh instance of InputDevice is created (with possibly
    # new fd).
    
    
    
    def update_devs(self, run_change_action=True):
        remaining_devs = self.all_devs
        new_devs = []
        found_new = []
        for path in list_devices(self.device_folder):
            dev = self.InputDevice_cls(path)
            for old_dev in remaining_devs:
                if dev == old_dev:
                    # this compares info and path attributes, but not fd
                    dev = old_dev  # this makes sure fd is the same.
                    remaining_devs.remove(old_dev)
                    break
            else:
                found_new.append(dev)
            new_devs.append(dev)
        if not new_devs:
            msg = 'error: no input devices found (do you have rw permission ' \
                  'on %s/*?)'
            raise IOError(msg%self.device_folder)
        self.all_devs = new_devs
        #print("Update devs\n", "found_new\n",found_new,"\nremaining_devs\n",
        # remaining_devs)
        if run_change_action and (found_new or remaining_devs):
            for action in self.change_actions:
                action(found_new, remaining_devs)
    
    
    @staticmethod
    def print_dev_change(found_new, lost_devs):
        msg = ""
        if found_new:
            msg += "New devs found:\n"
            for dev in found_new: msg += str(dev) + "\n"
        if lost_devs:
            msg += "Following devs lost:\n"
            for dev in lost_devs: msg += str(dev) + "\n"
        print(msg)
    
    @property
    def autoupdating(self):
        return self._autoupdating
    
    @autoupdating.setter
    def autoupdating(self, state: bool):
        old = self._autoupdating
        self._autoupdating = state
        if not old and state:
            self.update_devs()
            threading.Thread(target=self.updater).start()
    
    def updater(self):
        while self._autoupdating:
            time.sleep(self.update_interval)
            self.update_devs()
            #self.input_looper.print_devices()




class EvdevDeviceSelector:
    
    _used_updaters = []
    
    def __init__(self, category=None, name=None, path=None,
            selection_func=None, dev_updater=None):
        self.category = category
        self.name = name
        self.path = path
        self.selection_func = selection_func
        self.matched_devs = []
        if dev_updater is None:
            if self._used_updaters:
                for old_updater in self._used_updaters:
                    if old_updater.autoupdating: dev_updater = old_updater
            else:
                dev_updater = EvdevDeviceUpdater()
        self.devupdater = dev_updater
        if dev_updater not in self._used_updaters:
            self._used_updaters.append(dev_updater)
        dev_updater.change_actions.append(self.dev_change_action)
    
    def properties(self):
        return self.category, self.name, self.path, self.selection_func
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.properties() == other.properties()
        elif isinstance(other, (tuple, list)) and len(other) == 4:
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
        return list(dev for dev in self.devupdater.all_devs if
        self.dev_is_selected(dev))
    
    def dev_change_action(self, found_new, lost_devs):
        pass