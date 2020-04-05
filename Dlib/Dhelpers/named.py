#
#
# Copyright (c) 2020 DPS, dps@my.mail.de
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

from .baseclasses import KeepInstanceRefs
from .arghandling import extract_if_single_collection, check_type
from .decorators import (extend_to_collections, extend_to_collections_dirs,
    ignore_first_arg)
import collections


#TODO: Standardizing classmethods should be made more clear.


class NamedObj(KeepInstanceRefs):
    defined_objects = None
    name_to_stnd_name = None
    names_with_important_capital_letters = None
    StandardizingDict = None
    defined_groups = None
    NameContainer = None
    
    __slots__ = ["names", "groups"]
    
    def __init_subclass__(cls, inherit_names=False):
        cls.names_with_important_capital_letters = set()
        cls.defined_groups = dict()
        cls.defined_objects = dict()
        cls.name_to_stnd_name = dict()
        sd = type(f"{cls.__name__}.StandardizingDict", (StandardizingDict,),{})
        sd.__module__ = cls.__module__
        sd.NamedClass = cls
        cls.StandardizingDict = sd
        new = NameContainer(cls)
        if inherit_names:
            for defining_class in cls.NameContainer.name_defining_classes:
                new.update(defining_class)
        cls.NameContainer = new
        
        
        
    @classmethod
    def update_names(cls, decorated_class):
        """A class decorator"""
        cls.NameContainer.update(decorated_class)
        return decorated_class
    
    def __init__(self, *names):
        super().__init__()
        self.groups = []
        self.names = list()
        self.add_names(*names)


    def add_to_group(self, group_name):
        if group_name in self.groups: return
        self.groups.append(group_name)
        try:
            members = self.defined_groups[group_name]
        except KeyError:
            self.defined_groups[group_name] = [self]
        else:
            if self not in members: members.append(self)
    
    def add_names(self, *names):
        #names = list(extract_if_single_collection(names))
        for name in names:
            if isinstance(name, int): name = str(name)
                #names[i] = name
                # names must be strings.
            check_type(str, name)
            if not self._check_if_name_is_allowed(name):
                raise NameError("Name " + name + " is forbidden.")
            try:
                existing_obj = self.instance(name)  # this uses make_comparable
            except KeyError:
                continue
            # if name was already used:
            if name in existing_obj.names:  # this does not use make_comparable
                raise NameError("Name " + name + " already assigned.")
            else:
                # this happens if e.g. agrave and Agrave are entered
                self.names_with_important_capital_letters.update({name.lower()})
        self.names += names
        self.calculate_refs()  # it is important that calculate_refs is run
            # each time so that names_with_important_capital_letters stays up
            # tp date
        
    @classmethod
    def calculate_refs(cls, ignore=None):
        cls.defined_objects = {}
        cls.name_to_stnd_name = {}
        for keyobj in cls.get_instances():
            if keyobj is ignore:
                continue  # this possibilitx is intended for the __del__ method
            for name in keyobj.names_comparable:
                if name in cls.defined_objects:
                    print(keyobj, keyobj.names,keyobj.names_comparable)
                    raise NameError("Key name " + str(
                            name) + " exists more than 1 time.")
                cls.defined_objects[name] = keyobj
                cls.name_to_stnd_name[name] = keyobj.name
            for group_name in keyobj.groups:
                members = cls.defined_groups[group_name]
                if keyobj not in members: members.append(keyobj)
        # for group in cls.defined_groups:
        #     group = cls.make_comparable(group)
        #     if group in cls.defined_objects:
        #         raise NameError(f"{group} defined multiple times for {cls}")
                
    
    @property
    def name(self):
        return self.names[0]
    
    @property
    def names_comparable(self):
        for name in self.names: yield self.make_comparable(name)
    
    @classmethod
    @extend_to_collections
    def make_comparable(cls, name):
        if isinstance(name, int): name = str(name)
        check_type(str, name)
        name = str(name)  #convert from Keyvent events to normal strings
        n = name.lower()
        if n not in cls.names_with_important_capital_letters:
            return n
            # usually return the lower case version.
            # but if the name exists in different cases,
            # return the name unchanged.
        return str(name)
    
    @property
    def stnd_name_comparable(self):
        return self.make_comparable(self.name)
    
    @classmethod
    def instance(cls, name):
        if not name: raise ValueError
        if isinstance(name, cls): return name
        return cls.defined_objects[cls.make_comparable(name)]

        
    
    @classmethod
    def get_stnd_name(cls, name, return_if_not_found=None):
        if isinstance(name, cls):
            return name.name
        try:
            return cls.name_to_stnd_name[cls.make_comparable(name)]
        except KeyError:
            return return_if_not_found
    
    # def set_stnd_name(self, stnd_name):
    #     self.stnd_name=stnd_name
    #     if self.stnd_name_comparable in self.stnd_names():
    #         raise Exception("This stnd name already given.")
    #     if self.stnd_name_comparable not in self.names_comparable:
    #         self.add_names(stnd_name)
    #     else:
    #         self.calculate_refs()
    
    
    @classmethod
    def _check_if_name_is_allowed(cls, name):
        # override this in a subclass
        return True
        # raise NotImplementedError("method '_check_if_name_is_allowed' must
        # be defined in a subclass of", cls)
    
    @classmethod
    def all_names_comparable(cls):
        return set(cls.name_to_stnd_name.keys())
    
    @classmethod
    def stnd_names(cls):
        return set(cls.name_to_stnd_name.values())
    
    def __del__(self):
        # 1. if an object is completely deleted and garbage collected,
        #   recalculate the refs
        # 2.  this will happen automatically after this instance is
        # completely destroyed
        # because the get_instances() method notices that the weakref is
        # targeting an non-existing object
        # 3. But for now, the instance is not yet destroyed,
        #  so we need to explicitely tell the calculate ref function to
        # ignore this instance
        #raise RuntimeError
        self.calculate_refs(ignore=self)
    
    
    def __eq__(self, other):
        if isinstance(other,int): other=f"[{other}]"
        if isinstance(other, str):
            return self.make_comparable(other) in self.names_comparable
        else:
            return super().__eq__(other)
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return super().__repr__()[:-1] + " with standard name '%s'>"%self.name
    
    
    @classmethod
    def standardize_single(cls, string, applied_func):
        if isinstance(string, int):
            return applied_func(str(string))
        if isinstance(string, cls):
            return applied_func(string.name)
        return cls.analyze_string(str(string), applied_func)
    
    
    @classmethod
    def analyze_string(cls, string, applied_func):
        # override this in a subclass
        return applied_func(string)
    
    @classmethod
    @ignore_first_arg(extend_to_collections_dirs)
    def standardize(cls, obj):
        return cls.standardize_single(obj,
                lambda name: cls.get_stnd_name(name, name))
    
    
    
    
class StandardizingDict(dict):
    
    
    NamedClass = None  #set by NamedObj init_subclass method
        
    def __init__(self, *new_info, func=None):
        self.standardize = self.NamedClass.standardize
        super().__init__()
        if len(new_info) > 0:
            # print(new_info)
            self.update(*new_info, func=func)
    
    def update(self, *new_info, func=None):
        new_info = extract_if_single_collection(new_info)
        if isinstance(new_info, (set, list, tuple)):
            new_info = dict(zip(new_info, new_info))
        check_type(dict, new_info)
        if not func: func = lambda x: x
        dic = {self.standardize(k): func(v) for (k, v) in new_info.items()}
        return super().update(dic)
    
    def __setitem__(self, k, v) -> None:
        return super().__setitem__(self.standardize(k), v)
    
    def get(self, k, default):
        return super().get(self.standardize(k), default)
    
    def __getitem__(self, k):
        return super().__getitem__(self.standardize(k))
    
    def __contains__(self, item):
        #print(repr(item), self.standardize(item))
        return super().__contains__(self.standardize(item))
    
    def apply(self, obj):
        # print(obj, type(obj))
        return self.NamedClass.standardize_single(obj,
                lambda name: self.get(name, self.standardize(name)))
    
    
    
    

def get_attributes(cls):
    for a, b in cls.__dict__.items():
        if not (a.startswith("__") and a.endswith("__")): yield (a,b)


class GroupContainer:
    def __call__(self, arg):
        return getattr(self,arg)
    
    def __init__(self, NamedClass):
        self.NamedClass =NamedClass
        
    def __getattr__(self, item):
        try:
            return self.NamedClass.defined_groups[item]
        except KeyError:
            raise AttributeError

class NameContainer:
    def __init__(self, NamedClass):
        self.NamedClass = NamedClass
        self.group = GroupContainer(NamedClass)
        self.name_defining_classes = []
        
    
    def update(self, NameDefiningClass):
        self.name_defining_classes.append(NameDefiningClass)
        self._iter_class(NameDefiningClass)
                
    def _iter_class(self,  cls, group_name=None, excluded=()):
        excluded = list(excluded) #creates copy
        for attr, val in get_attributes(cls):
            if val is None:
                excluded.append(attr)
                continue
            if attr in excluded: continue
            if isinstance(val,type):
                # nested class can be used to define a group
                gn = attr if group_name is None else group_name
                self._iter_class(val, group_name=gn, excluded=excluded)
            else:
                if isinstance(val, (tuple,list)):
                    names = list(val)
                elif isinstance(val,(str,int)):
                    names = [val]
                else:
                    raise TypeError(f"{val} of type {type(val)}")
                try:
                    inst = super().__getattribute__(attr)
                    # this will avoid the special __getattr__ from below
                except AttributeError:
                    inst = self.NamedClass(*names)
                setattr(self, attr, inst)
                if inst.names != names:
                    raise NameError(f"multiple defined attribute {attr}")
                if group_name: inst.add_to_group(group_name)
        for bcls in cls.__bases__:
            self._iter_class(bcls, group_name=group_name, excluded=excluded)
        
    
    def __getattr__(self, item):
        try:
            return self(item)
        except KeyError:
            raise AttributeError
        
    def __call__(self, name):
        return self.NamedClass.instance(name)