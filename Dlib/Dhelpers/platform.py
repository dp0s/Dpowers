#
#
# Copyright (c) 2020-2024 DPS, dps@my.mail.de
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
from typing import Any

from .launcher import launch
import platform


class PlatformChecker:
    
    def __init__(self, evaluate=True):
        self.val_dir = None
        if evaluate: self.__evaluate__()
    
    def __evaluate__(self):
        self._system = self.system
        self._version = self.version
        val_dir = dict()
        for name in self.__class__.__dict__:
            if name.startswith("__") or name.endswith("__"): continue
            func = getattr(self, name)
            if not callable(func): continue
            val = func()
            assert val in (True, False)
            val_dir[name] = val
        self.val_dir = val_dir
        del self._system
        del self._version
        
    @property
    def system(self):
        try:
            return self._system
        except AttributeError:
            return platform.system().lower()
    
    @property
    def version(self):
        try:
            return self._version
        except AttributeError:
            return platform.version().lower()
    
    def linux(self):
        return self.system == "linux"
    
    def windows(self):
        return self.system == "windows"
    
    def mac(self):
        return self.system == "darwin"
    
    def termux(self):
        return self.linux() and bool(
                launch.get("command -v termux-setup-storage", check=False))
    
    def ubuntu(self):
        return self.linux() and "ubuntu" in self._version






class PlatformInfo:
    
    def __init__(self, **platform_kwargs):
        self.effective_vals = platform_kwargs
        self.preset_vals = platform_kwargs.copy()
        self.variables = list()
        
    def __repr__(self):
        sup = super().__repr__()[:-1]
        sup += " with values:"
        for key,val in self.effective_vals.items():
            if val is True: sup += f" {key},"
        sup = sup[:-1] + ">"
        return sup
        
    def update(self, use_platform_checks=True, **platform_kwargs):
        self.preset_vals.update(platform_kwargs)
        effective_vals = self.preset_vals.copy()
        if use_platform_checks:
            for platform_property, val in self.platform_property_checks(
                    ).val_dir.items():
                preset = self.preset_vals.get(platform_property)
                if preset is None: effective_vals[platform_property] = val
        self.effective_vals = effective_vals
        
        
    def copy(self):
        new_inst = self.__class__()
        new_inst.effective_vals = self.effective_vals.copy()
        new_inst.preset_vals = self.preset_vals.copy()
        if new_inst.platform_property_checks != self.platform_property_checks:
            new_inst.platform_property_checks = self.platform_property_checks
        return new_inst