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

from .. import Adaptor, adaptionmethod
from .windowobjects import FoundWindows, WindowSearch, WindowObject

class WindowAdaptor(Adaptor):
    
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
                "\nTried to use the following property name for window "
                "argument: {prop_name}\nHowever, the following adaption module "
                "does not support this window property name:\n{"
                "func.module}".format_map(locals()))
    
    @adaptionmethod(require=True)
    def IDs_from_property(self, prop_name, prop_val, visible=None):
        try:
            i_list = self.IDs_from_property.target_with_args()
        except NotImplementedError as e:
            raise self._error(prop_name,self.IDs_from_property) from e
        if not i_list: i_list = set()
        return i_list
    
    @adaptionmethod(require=True)
    def property_from_ID(self, ID, prop_name):
        try:
            val = self.property_from_ID.target_with_args()
        except NotImplementedError as e:
            raise self._error(prop_name,self.property_from_ID) from e
        if val: return val
    
    def id_exists(self, ID):
        return bool(self.property_from_ID(ID, "title"))
    
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
    
    
    @classmethod
    def screen_res(cls):
        return cls.adaptor.screen_res()
    
    
    