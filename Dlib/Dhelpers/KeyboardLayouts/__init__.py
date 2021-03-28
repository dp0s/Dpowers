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
import json, os
from abc import ABC, abstractmethod
from Dhelpers.launcher import launch
path = os.path

parentfolder = path.split(__file__)[0]
saved_folder = path.join(parentfolder,"layouts_imported_from_xkb")
try:
    os.makedirs(saved_folder, exist_ok=True)
except PermissionError:
    pass
    


def get_files(folder):
    for f in os.listdir(folder):
        fp = path.join(folder, f)
        if path.isfile(fp): yield f, fp


class LayoutBase(ABC):
    
    json_savefolder = saved_folder
    folders=[]
    file_ending = ""
    available_layouts = {}
    
    def __init__(self, name, folder=None, raise_error=True):
        self.name = name
        self.custom_folder = folder
        self.key_dict = {}
        self.key_dict = self.get_keydict()
        if not self.key_dict and raise_error: raise ValueError
    
    def sourcepath(self):
        full_name = self.name + self.file_ending
        l = (self.custom_folder,) if self.custom_folder else self.folders
        for folder in l:
            fp = path.join(folder, full_name)
            if path.isfile(fp): return fp
        raise FileNotFoundError
    
    @abstractmethod
    def get_keydict(self):
        raise NotImplementedError
        
    
    def save_json_dict(self, name=None, folder=None):
        if not folder: folder = self.json_savefolder
        if not name: name = self.name
        with open(path.join(folder, name + ".json"), "w") as f:
            json.dump(self.key_dict, f, indent=4)
    
    @classmethod
    def find_available(cls, folder=None):
        l = (folder,) if folder else cls.folders
        saved=[]
        available={}
        for folder in l:
            for name, fp in get_files(folder):
                name = path.splitext(name)[0]
                if name in saved: continue
                try:
                    obj = cls(name, folder=folder)
                except:
                    # if this object cannot be created, do not list it as
                    # available
                    continue
                saved.append(name)
                available[name] = obj
        cls.available_layouts = available
        return saved
    
    @classmethod
    def create_available_jsons(cls):
        for name,obj in cls.available_layouts.items():
            obj.save_json_dict()
    
    
    def __lt__(self, other):
        if not isinstance(other, self.__class__): return NotImplemented
        d = {}
        kd2 = self.key_dict
        kd1 = other.key_dict
        for key in kd2:
            right = kd2[key][0]
            try:
                left = kd1[key][0]
            except KeyError:
                left = key
            if left is not right: d[left] = right
        return d
    
    




class Layout(LayoutBase):
    
    folders = [saved_folder]
    file_ending = ".json"
    
    def get_keydict(self):
        with open(self.sourcepath()) as f: return json.load(f)
    
    
    
    
class Layout_from_klfc(LayoutBase):
    #klfc command line tool needs to be installed
    #this way, json layout tables can be created.
    
    klfc_option = None #to be set in subclass (see below)
    
    def get_keydict(self):
        json_str = launch.get(
                f"klfc --{self.klfc_option} '{self.sourcepath()}'")
        return self.convert_from_klfc_json(json.loads(json_str))
    
    @staticmethod
    def convert_from_klfc_json(klfc_dict):
        d = {}
        for entry in klfc_dict["keys"]:
            d[entry["pos"].lower()] = entry["letters"]
        return d
    
    
class XKBLayout(Layout_from_klfc):
    
    folders = ["/usr/share/X11/xkb/symbols"]
    klfc_option = "from-xkb"

    