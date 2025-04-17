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
from typing import Any

from .launcher import launch
import platform


class PlatformLogic:
    
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
        return self.linux() and "ubuntu" in self.version
    
    
    def platform_checker_methods_(self):
        for name in self.__class__.__dict__:
            if name.startswith("_") or name.endswith("_"): continue
            func = getattr(self, name)
            if not callable(func): continue
            yield name, func
    
    def set_states_(self, system=None, version=None):
        self.system = system
        self.version = version
    
    def evaluate_(self):
        val_dir = {
            "__based_on__": {
                "system": self.system, "version": self.version
                }
            }
        for name, func in self.platform_checker_methods_():
            val = func()
            assert val in (True, False)
            val_dir[name] = val
        return val_dir


class PlatformChecker:
    
    PlatformLogic = PlatformLogic
    
    def __init__(self, evaluate=True):
        self.platform_logic = self.PlatformLogic()
        self.val_dir = None
        if evaluate: self.evaluate()
    
    @staticmethod
    def system():
        return platform.system().lower()
    
    @staticmethod
    def version():
        return platform.version().lower()
    
    def set_states(self, system=None, version = None):
        if system is None: system = self.system()
        if version is None: version = self.version()
        self.platform_logic.set_states_(system, version)
        
    def evaluate(self, system=None, version = None):
        self.set_states(system, version)
        self.val_dir = self.platform_logic.evaluate_()
        return self.val_dir
    
    
    def check(self, platform_name, system=None, version=None):
        self.set_states(system, version)
        for name,func in self.platform_logic.platform_checker_methods_():
            if platform_name == name: return func()
        raise NotImplementedError(platform_name)
    
    def compare(self, dic):
        # this is just a sketch.. Needs to become cleverer in future
        # in particular account for sub platforms like Linux > Ubuntu
        for platform_info in self.val_dir:
            try:
                return dic[platform_info]
            except KeyError:
                pass
        raise NotImplementedError