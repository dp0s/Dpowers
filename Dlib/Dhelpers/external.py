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
import os,yaml, tempfile, __main__
path = os.path
import getpass,platform #useful for the profile functions
from Dhelpers.launcher import launch
from .strhandling import slugify

# taken from https://stackoverflow.com/questions/13293680/pyyaml-how-to-align-map-entries
# def dict_representer(dumper, dic):
#     keyWidth = max(len(k) for k in dic)
#     aligned = {k +' '*(keyWidth-len(k)):v for k,v in dic.items()}
#     return dumper.represent_mapping('tag:yaml.org,2002:map', aligned)

#yaml.add_representer(dict, dict_representer)

#==============================================================================
# #profile functions - return name of the profile of the given environment
def user_node():
    return getpass.getuser()+"_at_"+platform.node()

#==============================================================================

def yaml_write(obj, f):
    if isinstance(f, str):
        if not os.path.isfile(f):
            os.makedirs(os.path.dirname(f),exist_ok=True)
        with open(f,"w") as fp:
            yaml.dump(obj,fp, default_flow_style=False, indent=4)
    else:
        raise TypeError

def yaml_read(f):
    if isinstance(f, str):
        if path.isfile(f):
            with open(f) as fp: return yaml.load(fp)
        else:
            raise FileNotFoundError
    else:
        raise TypeError


def get_files(folder):
    try:
        dircontent = os.listdir(folder)
    except FileNotFoundError:
        return # creates an empty generator
    for f in dircontent:
        ff = path.join(folder, f)
        if path.isfile(ff): yield f, ff


class ExternalDict:
    basefolder = None
    _default_profile_dic = {"_": None}
    yaml_editor_command = None
        
    
    
    def __init__(self, name, folder=None, profile=None,
            incl_default_profiles=True):
        if folder is None: folder = self.basefolder #inherit from class
        if folder is None:
            try:
                f = __main__.__file__
            except AttributeError:
                raise Exception("No folder specified.")
            folder = path.join(path.dirname(path.realpath(f)), "external_dicts")
        if not os.access(folder, os.F_OK | os.W_OK | os.R_OK):
            raise Exception("No access to " + folder)
        if not os.path.isdir(folder):
            raise Exception(folder + " is not a folder")
        if isinstance(profile, str) or callable(profile):
            profile = [profile]
        elif profile is None:
            profile = []
        elif "global" in profile or "user_node" in profile:
            incl_default_profiles = False
        if incl_default_profiles:
            profiles = ["global"] + list(profile) + ["user_node"]
        else:
            profiles = list(profile)
        if not profiles: raise ValueError
        profile_values = []
        for p in profiles:
            if isinstance(p, str):
                if p=="user_node": p = user_node()
                profile_values.append(p)
            elif callable(p):
                profile_values.append(str(p()))
            else:
                raise ValueError(f"{p} is not a alid argument for profile.")
        self.profiles = profile_values
        self.basefolder = folder
        self.name = name
        self.folder = path.join(folder,name)
        os.makedirs(self.basefolder, exist_ok=True)
        for p in self.profiles:
            os.makedirs(self.path(p), exist_ok=True)
        self.load()
        self.locked = False
    
    
    def load(self):
        self.val = self.get_val()
        return self.val
    
    def get_val(self):
        val = dict()
        for profile in self.profiles:
            val.update(self.load_profile(profile))
        return val
        
        
    def load_profile(self,profile=None):
        d = dict()
        for fname, fpath in get_files(self.path(profile)):
            retrieved = yaml_read(fpath)
            if isinstance(retrieved, (tuple,list)):
                if retrieved[0] == "__key_val__":
                    if len(retrieved) != 3: raise ValueError
                    d[retrieved[1]] = retrieved[2]
                    continue
            d[fname] = retrieved
        return d
    
    def path(self, profile=None, *args):
        keys = tuple(slugify(arg) for arg in args)
        if profile is None: profile = self.profiles[-1]
        return path.join(self.folder, profile, *keys)
    
    def update_items(self,dic, profile=None, remove=False, keep_timestamps=True):
        if not dic: return
        if dic == self._default_profile_dic: return
        old_dic = self.load_profile(profile)
        #print(dic, "\n\n", old_dic)
        for key,val in dic.items():
            try:
                v_old = old_dic.pop(key)
            except KeyError:
                pass
            else:
                if val == v_old and keep_timestamps: continue
            #This makes sure that only files are touched if the value has
            #actually changed. This is cruical for synchronization by time stamp.
            yaml_write(["__key_val__",key,val], self.path(profile,key))
        if remove and old_dic: self.empty_profile(profile, *old_dic.keys())
        #print("removed", old_dic)
    
    def empty_profile(self, profile=None, *keys):
        if not keys:
            keys = tuple(fname for fname,fpath in get_files(self.path(profile)))
        for key in keys:
            #print(f"removing {key} from {profile}")
            os.remove(self.path(profile,key))
        
    def empty(self):
        for profile in self.profiles: self.empty_profile(profile)
    
    
    def edit(self, wait=False, keep_timestamps=True):
        if self.locked:raise RuntimeError(f"ExternalDict {self} already "
                    f"opened for editing")
        self.locked = True
        editable = dict()
        num = 0
        for profile in self.profiles:
            dic = self.load_profile(profile)
            if not dic: dic = self._default_profile_dic.copy()
            k=f"PROFILE {num} -- '{profile}'"
            editable[k] = dic
            num += 1
        editable[f"EXTERNAL OBJECT '{self.name}'"]={
            "basefolder":self.basefolder, }
        after_thread = launch.thread(self.after_edit, editable, keep_timestamps)
        if wait: after_thread.join()
        return after_thread
        
    def after_edit(self, editable, keep_timestamps):
        after_edit = self.edit_obj(editable)
        for k, dic in after_edit.items():
            if k.startswith("EXTERNAL OBJECT"): continue
            profile = k.split(" -- '")[-1][:-1]
            self.update_items(dic, profile, remove=True,
                    keep_timestamps=keep_timestamps)
        self.load()
        self.locked = False

    
    def edit_obj(self, obj):
        tempdir = tempfile.gettempdir()
        fpath = path.join(tempdir, f"external_edit_Dhelpers_{self.name}.yaml")
        if path.isfile(fpath): raise FileExistsError(fpath)
        yaml_write(obj, fpath)
        if not self.yaml_editor_command:
            raise ValueError("You need to set the "
                             "ExternalDict.yaml_editor_command attribute to "
                             "edit external objects with a text editor.")
        launch.wait(self.yaml_editor_command, fpath)
        new = yaml_read(fpath)
        os.remove(fpath)
        return new
        
    def __info__(self):
        return self.name, self.folder, self.profiles
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__info__() == other.__info__()
        return NotImplemented
    
    def __hash__(self):
        return hash(self.__info__())
    
    def __str__(self):
        return f"<{self.__class__.__name__}: {self.__info__()}>"