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
from Dhelpers.launcher import launch
from .baseclasses import TimedObject
import time, collections

class Container:
    
    def __init__(self):
        self.store = {}
        self.active_object_lists = collections.defaultdict(list)
    
    def set_temp_store_key(self,keyname, value, timeout=60*30):
        self.store[keyname] = value
        if timeout:
            launch.thread(self.remove_temp_store_key, keyname, timeout)
    
    def remove_temp_store_key(self,keyname, timeout=0):
        time.sleep(timeout)
        if keyname in self.store: self.store.pop(keyname, None)
    
    
    def key_stored(self, *args, **kwargs):
        return key_stored(self, *args,**kwargs)
    
    
class key_stored(TimedObject):
    def __init__(self, container_instance, keyname, timeout=60*30, value=None):
        super().__init__(timeout=timeout)
        self.keyname = keyname
        self.value = value
        self.value_before = None
        self.container = container_instance
        self.store = container_instance.store
        self.active_objects = container_instance.active_object_lists[keyname]
    
    def _start_action(self):
        self.value_before = self.store.get(self.keyname)
        self.active_objects.append(self)
        if self.value is not None:
            self.store[self.keyname] = self.value
        return self.active_objects
    
    def _stop_action(self):
        ao = self.active_objects
        if self not in ao: raise ValueError
        last = ao[-1]
        if last is self:
            if self.value_before is not None:
                self.store[self.keyname] = self.value_before
            else:
                try:
                    self.store.pop(self.keyname)
                except KeyError:
                    pass
        else:
            for i in range(len(ao)):
                if ao[i] is self: break
            ao[i+1].value_before = self.value_before
        ao.remove(self)
    
    def __repr__(self) -> str:
        sup = super().__repr__()[:-1]
        return sup + f" (key:{self.keyname}, value:{self.value}, " \
                     f"value_before:{self.value_before}) >"



container = Container()