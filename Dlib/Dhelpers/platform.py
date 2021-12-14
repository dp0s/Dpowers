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
from .launcher import launch


class Platform:
    
    def __init__(self):
        self.effective_vals = dict()
        self.preset_vals = dict()
        
    def update(self, use_platform_checks=True, **platform_kwargs):
        self.preset_vals.update(platform_kwargs)
        effective_vals = self.preset_vals.copy()
        if use_platform_checks:
            for platform_property, func in self.platform_property_checks().func_dir.items():
                assert callable(func)
                preset = self.preset_vals.get(platform_property)
                if preset is None:
                    val = func()
                    assert val in (True,False)
                    effective_vals[platform_property] = val
        self.effective_vals = effective_vals
        
        
    def copy(self):
        new_inst = self.__class__()
        new_inst.effective_vals = self.effective_vals.copy()
        new_inst.preset_vals = self.preset_vals.copy()
        if new_inst.platform_property_checks != self.platform_property_checks:
            new_inst.platform_property_checks = self.platform_property_checks
        return new_inst
            
    
    def evaluate(self, allow_multiple=False,**platform_kwargs):
        if allow_multiple: result = []
        for key,val in platform_kwargs.items():
            if self.effective_vals.get(key) is True:
                if allow_multiple:
                    result.append(val)
                else:
                    return val
        if allow_multiple: return result
        return NotImplemented



    class platform_property_checks:
    
        def __init__(self):
            self.func_dir = dict((name, getattr(self, name)) for name in \
                self.__class__.__dict__ if
            not (name.startswith("__") and name.endswith("__")))
    
        @staticmethod
        def termux():
            return bool(
                    launch.get("command -v termux-setup-storage", check=False))
    
        def linux(self):
            return True
    
        def windows(self):
            return False