#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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

from .. import Adaptor, adaptionmethod
from .windowobjects import FoundWindows, WindowSearch, WindowObject
from collections import defaultdict
import functools
from contextlib import contextmanager

class WindowAdaptor(Adaptor):
    
    
    @functools.wraps(Adaptor.__init__)
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.cached_properties = defaultdict(dict)
        self.use_cache = False
        
    @functools.wraps(Adaptor.adapt)
    def adapt(self, *args,**kwargs):
        self.cached_properties.clear()
        return super().adapt(*args,**kwargs)


    @contextmanager
    def cached(self):
        self.cached_properties.clear()
        self.use_cache  =True
        try:
            yield
        finally:
            self.use_cache = False
            self.cached_properties.clear()


    @adaptionmethod
    def screen_res(self):
        return self.screen_res.target()
    
    @adaptionmethod("ID_from_location")
    def _ID_from_location(self, param):
        try:
            i = self._ID_from_location.target_with_args()
        except NotImplementedError as e:
            raise NotImplementedError(f"The adaption module "
              f" {self._ID_from_location.module} does not support the following"
              f" location argument for window objects: {param}") from e
        return i
    
    
    @staticmethod
    def _error(prop_name, func):
        return NotImplementedError(
                f"\nTried to use the following property name for window "
                f"argument: {prop_name}\nHowever, the following adaption "
                f"module does not support this window property name:\n"
                f"{func.__module__}")
    
    @adaptionmethod(require=True)
    def IDs_from_property(self, prop_name, prop_val, visible=None):
        try:
            i_list = self.IDs_from_property.target_with_args()
        except NotImplementedError as e:
            raise self._error(prop_name,self.IDs_from_property) from e
        if not i_list: i_list = set()
        if self.use_cache:
            for id in i_list: self.cached_properties[id][prop_name]=prop_val
        return i_list
    
    @adaptionmethod(require=True)
    def property_from_ID(self, ID, prop_name, query_cache=None):
        if query_cache is None and self.use_cache is True: query_cache = True
        if query_cache:
            try:
                return self.cached_properties[ID][prop_name]
            except KeyError:
                pass
        try:
            val = self.property_from_ID.target(ID, prop_name)
        except NotImplementedError as e:
            raise self._error(prop_name,self.property_from_ID) from e
        if not val: val = None
        if self.use_cache: self.cached_properties[ID][prop_name]=val
        return val
    
    def id_exists(self, ID):
        return bool(self.property_from_ID(ID, "title", query_cache=False))
    
    @adaptionmethod
    def activate(self, ID):
        return self.activate.target_with_args()
    
    @adaptionmethod
    def map(self, ID):
        return self.map.target_with_args()

    @adaptionmethod
    def unmap(self, ID):
        return self.unmap.target_with_args()
    
    @adaptionmethod
    def set_prop(self, ID, action: str, prop: str, prop2: str = False):
        return self.set_prop.target_with_args()
    
    @adaptionmethod
    def move(self, ID, x=-1, y=-1, width=-1, height=-1):
        return self.move.target_with_args()
    
    @adaptionmethod
    def close(self, ID):
        return self.close.target_with_args()
    
    @adaptionmethod
    def kill(self, ID):
        return self.kill.target_with_args()
    
    @adaptionmethod
    def minimize(self, ID):
        return self.minimize.target_with_args()


    
class WindowHandler(FoundWindows, WindowAdaptor.AdaptiveClass):
    pass
    
    
    