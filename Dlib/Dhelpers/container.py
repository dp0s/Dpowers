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
from .launcher import launch
from .baseclasses import TimedObject
import time

class container:
    dependency_paths = {}
    
    store = {}
    
    @staticmethod
    def set_temp_store_key(keyname, value, timeout=60*30):
        container.store[keyname] = value
        if timeout:
            launch.thread(container.remove_temp_store_key, keyname, timeout)
    
    @staticmethod
    def remove_temp_store_key(keyname, timeout=0):
        time.sleep(timeout)
        if keyname in container.store:
            container.store.pop(keyname, None)
    
    
    class key_stored(TimedObject):
        def __init__(self, keyname, timeout=60*30, new_value=None):
            super().__init__(timeout=timeout)
            self.keyname = keyname
            self.value = new_value
        
        def _start_action(self):
            self.saved_keyval = container.store.get(self.keyname, "__Nothing__")
            if self.value is not None:
                container.store[self.keyname] = self.value
            return self.saved_keyval
        
        def _stop_action(self):
            if self.saved_keyval == "__Nothing__":
                if self.keyname in container.store:
                    container.store.pop(self.keyname)
            else:
                container.store[self.keyname] = self.saved_keyval