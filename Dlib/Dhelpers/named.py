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

from .baseclasses import KeepInstanceRefs
from .arghandling import check_type
from .decorators import (extend_to_collections)


class NamedObj(KeepInstanceRefs):
    defined_objects = None
    name_to_stnd_name = None
    names_with_important_capital_letters = None
    StandardizingDict = None
    defined_groups = None
    NameContainer = None
    
    __slots__ = ["names", "groups", "mapping_dict"]
    
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
        self.mappings = {}


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
                pass
            else:
                # if name was already used:
                if name in existing_obj.names:  # this does not use make_comparable
                    raise NameError("Name " + name + " already assigned.")
                else:
                    # this happens if e.g. agrave and Agrave are entered
                    self.names_with_important_capital_letters.update({name.lower()})
            self.names.append(name)
            name2 = self.make_comparable(name)
            self.defined_objects[name2] = self
            self.name_to_stnd_name[name2] = self.name
        
        
    @classmethod
    def re_calculate_refs(cls, ignore=None):
        cls.defined_objects = {}
        cls.name_to_stnd_name = {}
        for inst in cls.get_instances():
            if inst is ignore:
                continue  # this possibilitx is intended for the __del__ method
            inst._register_instance()
    
    def _register_instance(self):
        for name in self.names_comparable:
            if name in self.defined_objects:
                print(self, self.names, self.names_comparable)
                raise NameError(
                        "Key name " + str(name) + " exists more than 1 time.")
            self.defined_objects[name] = self
            self.name_to_stnd_name[name] = self.name
        for group_name in self.groups:
            members = self.defined_groups[group_name]
            if self not in members: members.append(self)
    
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
        return name
    
    @property
    def stnd_name_comparable(self):
        return self.make_comparable(self.name)
    
    @classmethod
    def instance(cls, name):
        if not name: raise ValueError
        if isinstance(name, cls): return name
        return cls.defined_objects[cls.make_comparable(name)]

        
    
    @classmethod
    def get_stnd_name(cls, name):
        if isinstance(name, cls): return name.name
        return cls.name_to_stnd_name[cls.make_comparable(name)]
        
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
        self.re_calculate_refs(ignore=self)
    
    
    def __eq__(self, other):
        if isinstance(other, (int,str)):
            return self.make_comparable(other) in self.names_comparable
        else:
            return super().__eq__(other)
    
    def __hash__(self):
        return hash(self.name)
    
    def __repr__(self):
        return super().__repr__()[:-1] + " with standard name '%s'>"%self.name
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"
    
    
    
class StandardizingDict:
    
    _running_number = 0
    NamedClass = None  #set by NamedObj init_subclass method
        
    def __init__(self, new_info=None, func=None, others_comparable=True):
        self.running_number = self._running_number
        self.__class__._running_number += 1
        self.other_dict = dict()
        self.registered_instances = dict()
        self.registered_names = dict()
        self.others_comparable= others_comparable
        self.make_comparable = self.NamedClass.make_comparable
        if new_info: self.update(new_info, func=func)
        
    
    def _comparable(self, k):
        return self.make_comparable(k) if self.others_comparable else k
        
            
    def copy(self):
        return self.__class__(self,others_comparable=self.others_comparable)
    
    def update(self, new_info, func=None):
        if isinstance(new_info, (set, list, tuple)):
            new_info = dict(zip(new_info, new_info))
        elif isinstance(new_info, StandardizingDict):
            new_info = new_info.normal_version()
        check_type(dict, new_info)
        if not func: func = lambda x: x
        for k,v in new_info.items(): self[k] = func(v)
    
    def normal_version(self, str_of_inst=False, all=False):
        if str_of_inst:
            f = lambda inst: str(inst)
        else:
            f = lambda inst: inst.name
        d = self.other_dict.copy()
        if all:
            d.update(self.registered_names)
        else:
            d.update({f(inst): inst.mappings[self.running_number]
                for inst in self.registered_instances})
        return d
    
    def __repr__(self) -> str:
        old = super().__repr__()[:-1]
        return old + f" with running number {self.running_number}>"
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            if self.NamedClass == other.NamedClass and \
                self.other_dict == other.other_dict and \
                self.registered_instances == other.registered_instances:
                    return True
            return False
        return NotImplemented
    
    
    def __str__(self):
        return "StandardizingDict" + str(self.normal_version(
                str_of_inst=True)).replace("'","").replace('"','')
    
    
    def __setitem__(self, k, v) -> None:
        try:
            inst = self.NamedClass.instance(k)
        except KeyError:
            self.other_dict[self._comparable(k)] = v
        else:
            inst.mappings[self.running_number]=v
            for name in inst.names:
                self.registered_names[self.make_comparable(name)] = v
            self.registered_instances[inst] = v
    
    def __getitem__(self, k):
        # this method is optimized for speed
        try:
            if isinstance(k, self.NamedClass):
                return k.mappings[self.running_number]
            try:
                return self.registered_names[self.make_comparable(k)]
                #this is fast way to look up
            except KeyError:
                return self.other_dict[self._comparable(k)]
        except KeyError:
            raise KeyError(k)

        
    def __delitem__(self, k):
        try:
            inst = self.NamedClass.instance(k)
        except KeyError:
            del self.other_dict[self._comparable(k)]
        else:
            del inst.mappings[self._running_number]
            for name in inst.names: del self.registered_names[name]
            del self.registered_instances[inst]
        
    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default
        
    def pop(self, k, default=None):
        try:
            val = self[k]
        except KeyError:
            if default is not None: return default
            raise
        del self[k]
        return val
        
    def apply(self, k):
        try:
            inst = self.NamedClass.instance(k)
        except KeyError:
            try:
                return self.other_dict[self._comparable(k)]
            except KeyError:
                return k  #if k is not a defined name of any kind, return itself
        else:
            try:
                return inst.mappings[self.running_number]
            except KeyError:
                return inst.name
                #if k is not in dict, at least it can be standardized
    
    def __contains__(self, item):
        try:
            self[item]
            return True
        except KeyError:
            return False
    
    def keys(self):
        for inst in self.registered_instances: yield inst.name
        for key in self.other_dict.keys(): yield key
    
    def values(self):
        for value in self.registered_instances.values(): yield value
        for value in self.other_dict.values(): yield value
        
    def items(self):
        return zip(self.keys(), self.values())
    
    
    

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
                else:
                    for name in names:
                        n = self.NamedClass.make_comparable(name)
                        if n not in inst.names_comparable:
                            
                            raise NameError(f"multiple defined attribute {attr}")
                setattr(self, attr, inst)
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
    
    
    
    
# class NameCombination:
#
#     def __init__(self, *named_subclasses):
#         for NamedClass in named_subclasses:
#             if not issubclass(NamedClass, NamedObj): raise TypeError
#         self.NamedClasses = named_subclasses
#         self.StandardizingDict = type(f"NameCombination.StandardizingDict",
#                 (StandardizingDict,),{})
#         self.StandardizingDict.NamedClass = self
#