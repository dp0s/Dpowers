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
from ..launcher import launch

class platform:
    
    attrs = ["termux", "linux", "windows"]
    
    def __init__(self):
        for attr in self.attrs: setattr(self,attr,None)
    
    def update(self):
        for attr in self.attrs:
            setattr(self,attr,getattr(self,f"check_{attr}")())
            
    
    @staticmethod
    def check_linux():
        pass
    
    
    @staticmethod
    def check_termux():
        return bool(launch.get("command -v termux-setup-storage",check=False))
    
    @staticmethod
    def check_windows():
        pass