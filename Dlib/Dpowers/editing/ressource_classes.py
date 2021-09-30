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
from Dhelpers.adaptor import AdaptionMethod
from types import GeneratorType
import os, functools
from Dhelpers.file_iteration import FileIterator
from Dhelpers.baseclasses import iter_all_vars
from Dhelpers.named import NamedObj

path = os.path

iter_types = (list, tuple, GeneratorType)
class ClosedResource: pass
class ClosedResourceError(Exception): pass


edit_tag = "__edit"


class NamedValue(NamedObj):
     pass
    



class EditorAdaptor(Adaptor):
    
    property_value_dict = None
    named_classes = dict()
    
    
    @classmethod
    def Values_for_Property(cls, property_name):
        NamedClass = type(f"NamedValue_for_property_{property_name}",
                (NamedValue,), {})
        cls.named_classes[property_name] = NamedClass
        def decorator(container_class):
            NamedClass.update_names(container_class)
        return decorator
    
    baseclass = True  #for Adaptor mechanism
    
    # def __init_subclass__(cls):
    #     super().__init_subclass__()
    #     cls.NamedValue = type(f"{cls.__name__}.NamedValue", (NamedValueBase,),{})
    
    save_in_place = False  #if False, automatically rename before saving
    
    
    def _check(self, obj):
        if isinstance(obj, iter_types):
            for o in obj:
                if not isinstance(o, self.obj_class): raise TypeError
        else:
            if not isinstance(obj, self.obj_class): raise TypeError
        return obj
    
    @adaptionmethod(require=True)
    def load(self, file, **load_kwargs):
        backend_object = self._check(self.load.target_with_args())
        return backend_object
    
    obj_class = load.adaptive_property("obj_class", NotImplementedError)
    names = load.adaptive_property("names", default={}, ty=dict)
    value_names = load.adaptive_property("value_names", {}, dict)

    @load.target_modifier
    def _load_tm(self, target):
        self.create_effective_dict()
        return target

    def create_effective_dict(self):
        self.property_value_dict = dict()
        for prop_name, NamedCls in self.named_classes.items():
            stand_dict = NamedCls.StandardizingDict()
            try:
                value_list = self.value_names[prop_name]
            except KeyError:
                pass
            else:
                stand_dict.update(value_list)
            self.property_value_dict[prop_name] = stand_dict

    @adaptionmethod
    def load_multi(self, file, **load_kwargs):
        backend_objects = self._check(self.load_multi.target_with_args())
        return backend_objects
    
    @adaptionmethod
    def construct_multi(self, sequence_of_backend_objs):
        sequ = tuple(sequence_of_backend_objs)
        self._check(sequ)
        return self.construct_multi.target(sequ)
        
    @adaptionmethod(require=True)
    def save(self, backend_obj, destination=None):
        self._check(backend_obj)
        if self.save_in_place:
            assert destination is None
        else:
            assert  destination is not None
        self.save.target(backend_obj, destination)
    
    @adaptionmethod(require=True)
    def close(self, backend_obj):
        self._check(backend_obj)
        self.close.target_with_args()
        
    
    def forward_property(self, name, backend_obj, value = None):
        if self.property_value_dict and value is not None:
            try:
                stand_dict = self.property_value_dict[name]
            except KeyError:
                pass
            else:
                value = stand_dict.apply(value)
        try:
            amethod = getattr(self,name)
        except AttributeError:
            pass
        else:
            if isinstance(amethod,AdaptionMethod):
                return amethod(backend_obj, value)
        backend_name = self.names.get(name, name)
        if value is None:
            ret = getattr(backend_obj, backend_name)
            try:
                NamedCls = self.named_classes[name]
            except KeyError:
                pass
            else:
                try:
                    ret = NamedCls.get_stnd_name(ret)
                except KeyError:
                    pass
            return ret
        setattr(backend_obj, backend_name, value)
    
    
    def forward_func_call(self, name, backend_obj, *args, **kwargs):
        try:
            amethod = getattr(self,name)
        except AttributeError:
            pass
        else:
            if isinstance(amethod,AdaptionMethod):
                return amethod(backend_obj, *args,**kwargs)
        backend_name = self.names.get(name, name)
        return getattr(backend_obj, backend_name)(*args,**kwargs)
    




def resource_property(name, *name_alias):
    def func(self):
        return self.adaptor.forward_property(name,self.backend_obj)
    func.__name__ = name
    func.__qualname__ = name
    func._resource = True
    func._names = name_alias
    func = property(func)
    @func.setter
    def func(self, val):
        return self.adaptor.forward_property(name,self.backend_obj, val)
    return func

def multi_resource_property(name):
    def func(self):
        ret = []
        same = True
        for single in self.sequence:
            this = getattr(single,name)
            ret.append(this)
            if this is not ret[0]: same=False
        if same: return ret[0]
        return ret
    func.__name__ = name
    func.__qualname__ = name
    func._resource = True
    func = property(func)
    @func.setter
    def func(self, val):
        for single in self.sequence: setattr(single,name,val)
    return func

def is_resource_property(obj):
    return isinstance(obj, property) and hasattr(obj.fget,"_resource")



def resource_func(name, *names):
    def func(self,*args,**kwargs):
        return self.adaptor.forward_func_call(name,self.backend_obj, *args,
                **kwargs)
    func.__name__ = name
    func.__qualname__ = name
    func._resource = True
    func._names = names
    return func

def multi_resource_func(name):
    def func(self,*args,**kwargs):
        ret = []
        same = True
        for single in self.sequence:
            this = getattr(single, name)(*args,**kwargs)
            ret.append(this)
            if this is not ret[0]: same = False
        if same: return ret[0]
        return ret
    func.__name__ = name
    func.__qualname__ = name
    func._resource = True
    return func

def is_resource_func(obj):
    return callable(obj) and hasattr(obj,"_resource") and obj._resource is True





class Resource:
    
    file = None
    adaptor = None  #inherited as AdaptiveClass subclass

    allowed_file_extensions = None
    attr_redirections = None
    
    @classmethod
    def list_resource_properties(cls):
        return set(iter_all_vars(cls,is_resource_property))
    
    @classmethod
    def list_resource_funcs(cls):
        return set(iter_all_vars(cls, is_resource_func))

    @classmethod
    def _update_redirections(cls):
        cls.attr_redirections = {}
        for name in cls.list_resource_properties():
            cls.attr_redirections[name] = name
            names = getattr(cls,name).fget._names
            for n in names: cls.attr_redirections[n] = name
        for name in cls.list_resource_funcs():
            cls.attr_redirections[name] = name
            names = getattr(cls,name)._names
            for n in names: cls.attr_redirections[n] = name
        return cls.attr_redirections

    def filepath_split(self):
        folder, filename = path.split(self.file)
        name, ext = path.splitext(filename)
        self.folder = folder
        self.filename = name
        self.ext = ext

    def get_destination(self, input_dest=None, num=None, insert_folder=False):
        ext = None
        inp_name = None
        if input_dest:
            if input_dest.startswith("."):
                inp_name, ext = "", input_dest
            else:
                inp_name, ext = path.splitext(input_dest)
        elif self.adaptor.save_in_place:
            return
        if not ext: ext = self.ext
        if insert_folder:
            folder_name = insert_folder if isinstance(insert_folder,
                    str) else self.filename + edit_tag
        if not inp_name:
            if insert_folder:
                folder = path.join(self.folder, folder_name)
                os.makedirs(folder, exist_ok=True)
                append = f"_{num}" if num else ""
            else:
                folder = self.folder
                append = f"_{num}" if num else edit_tag
            return path.join(folder, self.filename + append + ext)
        if insert_folder:
            if not path.split(inp_name)[0]:
                # that means inp_name is a file not a folder structure
                os.makedirs(folder_name, exist_ok=True)
                inp_name = path.join(folder_name, inp_name)
        append = f"_{num}" if num else ""
        return inp_name + append + ext

    def _save(self, dest=None):
        raise NotImplementedError

    def save(self, destination=None, num=None):
        dest = self.get_destination(destination, num)
        return self._save(dest)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        raise NotImplementedError
    
    
    def __getattr__(self, item):
        try:
            redirected = self.attr_redirections[item]
        except KeyError:
            raise AttributeError(item)
        return self.__getattribute__(redirected)
    
    def __setattr__(self, key, value):
        try:
            key = self.attr_redirections[key]
        except KeyError:
            pass
        super().__setattr__(key,value)

    
    
class SingleResource(Resource):
    
    multi_base = None
    
    @classmethod
    def make_multi_base(cls, MultiClass):
        """A decorator"""
        cls.multi_base = MultiClass
        cls._set_multi(MultiClass)
        return MultiClass
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._update_redirections()
        cls._set_multi(cls.multi_base)
    
    

    @classmethod
    def _set_multi(cls, multi_base):
        class multi(multi_base):
            __qualname__ = f"{cls.__name__}.multi"
            __name__ = __qualname__
            __module__ = cls.__module__
            SingleClass = cls
            attr_redirections = cls.attr_redirections
        for name in cls.list_resource_properties():
            rp = multi_resource_property(name)
            setattr(multi,name,rp)
        for name in cls.list_resource_funcs():
            rf = multi_resource_func(name)
            setattr(multi,name,rf)
        cls.multi = multi
        

    def __init__(self, file=None, backend_obj=None, **load_kwargs):
        if isinstance(file, iter_types) or isinstance(backend_obj, iter_types):
            raise ValueError
        self.file = file
        self.backend_obj = backend_obj
        if file:
            assert backend_obj is None
            self.filepath_split()
            self.backend_obj = self.adaptor.load(file, **load_kwargs)
        elif backend_obj:
            self.adaptor._check(backend_obj)
        self.sequence = (self,)
        
    @classmethod
    def iterator(cls, *args,**kwargs):
        for filepath in FileIterator(*args,**kwargs).generate_paths():
            yield cls(filepath)

    @property
    def backend_obj(self):
        if self._backend_obj is ClosedResource: raise ClosedResourceError
        return self._backend_obj

    @backend_obj.setter
    def backend_obj(self, value):
        self._backend_obj = value
        
    def _save(self, dest=None):
        self.adaptor.save(self.backend_obj, dest)
        return dest
    
    
    def close(self):
        """Close the resource"""
        if self.backend_obj: self.adaptor.close(self.backend_obj)
        self.backend_obj = ClosedResource
    
    
    # def __add__(self, other):
    #     seq = self.sequence
    #     assert all(type(s) is self.SingleClass for s in seq)
    #     try:
    #         if all(type(s) is self.SingleClass for s in other.sequence):
    #             return self.SingleClass.Sequence(
    #                     images=self.sequence + other.sequence)
    #     except AttributeError:
    #         pass
    #     return NotImplemented
    
    



@SingleResource.make_multi_base
class MultiResource(Resource):
    
    SingleClass = None  # set by init subclass form Image class
    allowed_file_extensions = None #might differ from SingleClass
        
    
    def __init__(self, file=None, **load_kwargs):
        self.file = file
        self.filepath_split()
        self.sequence = []
        if isinstance(self.file, iter_types): raise ValueError(self.file)
        #self.filepath_split()
        if file:
            backend_objs = self.adaptor.load_multi(file, **load_kwargs)
            images = tuple(self.SingleClass(backend_obj=bo) for bo in backend_objs)
            self.sequence += images
    
    def _save(self, dest=None):
        self.adaptor.save(self.construct_backend_obj(), dest)
        return dest
    
    def save(self, destination=None, split=False):
        if destination and not destination.endswith(tuple(self.allowed_file_extensions)):
            split = True
        if not split: return super().save(destination)
        l = len(self.sequence)
        if l == 0: raise ValueError
        first = self.sequence[0]
        if l == 1:
            if destination is None and self.adaptor.save_in_place:
                return first._save()
            try:
                dest = self.get_destination(destination)
            except AttributeError:
                try:
                    dest = first.get_destination(destination)
                except AttributeError:
                    raise ValueError("Could not find destination name.")
            return first._save(dest)
        destinations = []
        for num in range(l):
            single = self.sequence[num]
            if destination is None:
                if self.adaptor.save_in_place: single._save()
            try:
                dest = self.get_destination(destination, num=num+1,
                        insert_folder=True)
            except AttributeError:
                try:
                    dest = single.get_destination(destination)
                except AttributeError:
                    raise ValueError("Could not find destination name.")
            destinations.append(single._save(dest))
        return destinations
        
    
    
    
    # def __init__(self, files=None, images=None, **load_kwargs):
    #     self.files = files
    #     if files:
    #         check_type(iter_types, files)
    #         assert images is None
    #         self.sequence = tuple(
    #                 self.SingleClass(file=f, **load_kwargs) for f in files)
    #     elif images:
    #         assert files is None
    #         assert load_kwargs == {}
    #         check_type(CollectionWithProps(self.SingleClass, minlen=1), images)
    #         self.sequence = images
    #     self.backend_obj = self.construct_backend_obj()
    
    
    @property
    def adaptor(self):
        return self.SingleClass.adaptor
    
    def backend_objs(self):
        return tuple(im.backend_obj for im in self.sequence)
    
    def construct_backend_obj(self):
        return self.adaptor.construct_multi(self.backend_objs())
    
    
    def close(self):
        for im in self.sequence: im.close()
    
    

    
    # def __getitem__(self, item):
    #     ims = self.sequence[item]
    #     if isinstance(item, int):
    #         check_type(self.SingleClass, ims)
    #         return ims
    #     if isinstance(item, slice):
    #         return self.__class__(images=ims)
    #     raise NotImplementedError
    #
    # def __eq__(self, other):
    #     if isinstance(other, self.__class__):
    #         return self.sequence == other.sequence
    #     return NotImplemented
    #
    # def __hash__(self):
    #     return hash(self.sequence)