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
import os, json
import getpass, platform  # useful for the profile functions


json_editor = "xdg-open"
file_manager = "xdg-open"


# ==============================================================================
# #profile functions - return name of the profile of the given environment
def user_node():
    return getpass.getuser() + "_at_" + platform.node()

# ==============================================================================


def jsonwrite(f, obj):
    if not os.path.isfile(f):
        os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w") as fp:
        json.dump(obj, fp, indent=4, sort_keys=True)

def jsonread(f):
    if os.path.isfile(f):
        with open(f) as fp:
            return json.load(fp)

class PortableObject:
    basefolder = None
    default_func = user_node
    allowed_types = (list, dict, float, int, str)
    
    @classmethod
    def set_folder(cls, folder):
        os.makedirs(folder, exist_ok=True)
        cls.basefolder = folder
    
    
    def __init__(self, name: str, obj_type: type, profile_func: callable = None,
            folder: str = None, ini_val=None):
        if folder is None:
            folder = self.__class__.basefolder
        if folder is None:
            raise Exception("No folder specified.")
        elif not os.access(folder, os.F_OK | os.W_OK | os.R_OK):
            raise Exception("No access to " + folder)
        elif not os.path.isdir(folder):
            raise Exception(folder + " is not a folder")
        if profile_func is None:
            profile_func = self.__class__.default_func
        if profile_func.__code__.co_argcount != 0:
            raise Exception("Profile function function must have 0 arguments.")
        if obj_type not in self.__class__.allowed_types:
            raise Exception("PortableObject only allows for types: " + str(
                    self.__class__.allowed_types))
        
        self.profile = profile_func
        self.func_name = self.profile.__name__
        self.name = name
        self.type = obj_type
        self.folder = folder
        
        file = self.path()
        
        if not os.path.isfile(file):
            # this happens if file is not existing yet
            if ini_val is not None:
                if type(ini_val) is not self.type:
                    raise Exception("ini_val is of type" + str(
                            type(ini_val)) + ",\nbut " + str(
                            self.type) + " was expected.")
            else:
                if self.type in (list, tuple):
                    ini_val = []
                elif self.type in (int, float):
                    ini_val = 0
                elif self.type is str:
                    ini_val = ""
                elif self.type is dict:
                    ini_val = {"": ""}
            jsonwrite(file, ini_val)
            self.edit()
        else:
            if ini_val is not None:
                raise Exception(
                        "ini_val given, but file " + file + " already exists.")
            obj = jsonread(file)
            if type(obj) != self.type:
                raise Exception(file + " contains object type " + str(
                        type(obj)) + ",\nbut " + str(
                        self.type) + " was expected.")
    
    
    def path(self, profile=None):
        if profile is None: profile = str(self.profile())
        return os.path.join(self.folder, self.func_name, profile,
                self.name + ".json")
    
    def path_folder(self, profile=None):
        return os.path.dirname(self.path(profile))
    
    def path__include(self, profile=None):
        x = os.path.splitext(self.path(profile))
        return x[0] + "__include" + x[1]
    
    def path_folder__include(self, profile=None):
        return os.path.join(self.path_folder(profile), "__include.json")
    
    
    # the included dictionary is of the form {"1":"profile1", "2":"profile2",
    # ...}
    def get__include_dict(self, profile=None, folder_default=False):
        if folder_default:
            file = self.path_folder__include(profile)
        else:
            file = self.path__include(profile)
        r = jsonread(file)
        if r is None:
            r = {}  # empty dictionary
        return r
    
    def __call__(self, profile=None):
        value = jsonread(self.path())
        t = type(value)
        if t != self.type:
            raise Exception(self.path() + " contains object type " + str(
                    t) + ",\nbut " + str(self.type) + " was expected.")
        
        if t in (dict, list, str):
            for default in (False, True):
                l = self.get__include_dict(folder_default=default)
                if l != {}:
                    # first check if there is a self.name__include file,
                    # telling us which additional profiles to include
                    # If there is not a self.name__include file, l will be
                    # set to {} by get__include_dict.
                    for i in sorted(l):  # gives sorted list of keys
                        f_add = self.path(l[i])  # gives path of the
                        # corresponding file in profile l[i]
                        value_add = jsonread(f_add)
                        if t == type(value_add):
                            if t == dict:
                                value_add.start_uinput(value)  # this way,
                                # the value-keys are overwriting the
                                # value_add keys
                                value = value_add
                            else:
                                value += value_add
                    break  # In case a self.name__included file was found
                    # stop here.  # Do not use default=True.  # otherwise the
                    # second loop is performed with folder_default=True  # so
                    # that the __include file of the whole folder is used
                    # instead.
        
        return value
    
    
    def edit(self, profile=None):
        os.system(json_editor + " " + self.path(profile))
    
    def edit_folder(self, profile=None):
        os.system(file_manager + " " + self.path_folder(profile))
    
    
    def write(self, obj, profile=None):
        if type(obj) != self.type:
            raise Exception(
                    "Wrong object type for writing. Expected type: " + str(
                            self.type))
        else:
            jsonwrite(self.path(profile), obj)
    
    
    def incl_profile(self, profile_to_include: str, i=0):
        i = str(i)
        if self.profile() == profile_to_include:
            raise Exception(
                    "Including values of " + profile_to_include + " to itself "
                                                                  "does not "
                                                                  "make sense.")
        
        l = self.get__include_dict()
        l[i] = profile_to_include
        jsonwrite(self.path__include(), l)
    
    def incl_profile_default(self, profile_to_include: str, i=0):
        i = str(i)
        if self.profile() == profile_to_include:
            raise Exception(
                    "Including values of " + profile_to_include + " to itself does not make sense.")
        
        l = self.get__include_dict(folder_default=True)
        l[i] = profile_to_include
        jsonwrite(self.path_folder__include(), l)

# To allow for different basefolders/type, you can use:
#
# class MyPortableObject(PortableObject):
#    basefolder=...
#    allowed_types=...
