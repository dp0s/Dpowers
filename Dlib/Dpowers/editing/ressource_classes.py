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
from types import GeneratorType
from Dhelpers.arghandling import check_type, CollectionWithProps
import os
from warnings import warn

path = os.path

iter_types = (list, tuple, GeneratorType)
class ClosedResource: pass
class CloseResourceError(Exception): pass


edit_tag = "__edit"



class EditorAdaptor(Adaptor):
    baseclass = True
    save_in_place = False
    
    @adaptionmethod(require=True)
    def obj_class(self):
        return self.obj_class.target
    
    def _check(self, obj):
        if isinstance(obj, iter_types):
            for o in obj:
                if not isinstance(o, self.obj_class()): raise TypeError
        else:
            if not isinstance(obj, self.obj_class()): raise TypeError
        return obj
    
    @adaptionmethod(require=True)
    def load(self, file, **load_kwargs):
        backend_object = self._check(self.load.target_with_args())
        return backend_object
    
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



class ResourceBase:
    
    allowed_file_extensions = None
    
    # def __init_subclass__(cls) -> None:
    #     super().__init_subclass__()
    #     print(cls)
    #     for name, inst in NamedAttr.defined_objects.items():
    #         def method(self,value=None):
    #             return self.set_value(inst,value)
    #         method.__name__ = name
    #         cls.name = method
    #         print(name, method)
    
    def filepath_split(self):
        folder, filename = path.split(self.file)
        name, ext = path.splitext(filename)
        self.folder = folder
        self.filename = name
        self.ext = ext
    
    def default_destination(self, num=None):
        append = edit_tag
        if num: append += f"_{num}"
        return path.join(self.folder, self.filename + edit_tag + self.ext)
    
    
    def __enter__(self):
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the ressource"""
        if self.backend_obj: self.adaptor.close(self.backend_obj)
        self.backend_obj = ClosedResource
    
    
    def __add__(self, other):
        seq = self.sequence
        assert all(type(s) is self.SingleClass for s in seq)
        try:
            if all(type(s) is self.SingleClass for s in other.sequence):
                return self.SingleClass.Sequence(
                        images=self.sequence + other.sequence)
        except AttributeError:
            pass
        return NotImplemented
    
    # def __getattr__(self, item):
    #     try:
    #         ret = getattr(self.backend_obj, item)
    #     except AttributeError as e:
    #         raise AttributeError(item, self)
    #     warn(f"Using attr {item} of backend_obj instead of {self}.")
    #     return ret


class Resource(ResourceBase):
    
    adaptor = None #to be set in subclass

   

    def __init_subclass__(cls):
        Sequence = type("Sequence", (ResourceSequence,), {})
        Sequence.__module__ = cls.__module__
        Sequence.SingleClass = cls
        cls.SingleClass = cls
        cls.Sequence = Sequence
        super().__init_subclass__()
    
    
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
    
    @property
    def backend_obj(self):
        if self._backend_obj is ClosedResource: raise CloseResourceError
        return self._backend_obj
    
    @backend_obj.setter
    def backend_obj(self, value):
        self._backend_obj = value
    
    
    def save(self, destination=None):
        if destination is None and not self.adaptor.save_in_place:
            destination = self.default_destination()
        return self.adaptor.save(self.backend_obj, destination)


    def _wrapper_func(self, adaptionmethod_name, *args, **kwargs):
        amethod = getattr(self.adaptor, adaptionmethod_name)
        return amethod(self.backend_obj, *args, **kwargs)
    
    def _sequence_wrapper_func(self, adaptionmethod_name, *args, **kwargs):
        amethod = getattr(self.adaptor, adaptionmethod_name)
        val = amethod(self.backend_obj, *args,
                **kwargs) if self.backend_obj else None
        vals = tuple(amethod(single.backend_obj, *args, **kwargs) for single in
        self.sequence)
        return val, vals
    
    
    @classmethod
    def set_prop(cls, *names):
        amethod_name = names[0]
        assert hasattr(cls.adaptor_class, amethod_name)
        @property
        def wrapper_prop(self):
            return self._wrapper_func(amethod_name)
        @wrapper_prop.setter
        def wrapper_prop(self,value):
            return self._wrapper_func(amethod_name, value)
        @property
        def sequence_wrapper_prop(self):
            return self._sequence_wrapper_prop(amethod_name)
        @sequence_wrapper_prop.setter
        def sequence_wrapper_prop(self, value):
            return self._sequence_wrapper_prop(amethod_name, value)
        for name in names:
            setattr(cls, name, wrapper_prop)
            setattr(cls.Sequence, name, sequence_wrapper_prop)
        
        
    
    @classmethod
    def set_func(cls, *names):
        amethod_name = names[0]
        assert hasattr(cls.adaptor_class, amethod_name)
        def wrapper_func(self,*args,**kwargs):
            return self._wrapper_func(amethod_name,*args,**kwargs)
        def sequence_wrapper_func(self,*args,**kwargs):
            return self._sequence_wrapper_func(amethod_name,*args,**kwargs)
        wrapper_func.__name__ = amethod_name
        sequence_wrapper_func.__name__ = amethod_name
        for name in names:
            setattr(cls, name, wrapper_func)
            setattr(cls.Sequence, name, sequence_wrapper_func)
        
        
        
        
        
class ResourceSequence(ResourceBase):
    SingleClass = None  # set by init subclass form Image class
    
    
    def __init__(self, files=None, images=None, **load_kwargs):
        self.files = files
        if files:
            check_type(iter_types, files)
            assert images is None
            self.sequence = tuple(
                    self.SingleClass(file=f, **load_kwargs) for f in files)
        elif images:
            assert files is None
            assert load_kwargs == {}
            check_type(CollectionWithProps(self.SingleClass, minlen=1), images)
            self.sequence = images
        self.backend_obj = self.construct_backend_obj()
    
    
    @property
    def adaptor(self):
        return self.SingleClass.adaptor
    
    def backend_objs(self):
        return tuple(im.backend_obj for im in self.sequence)
    
    def construct_backend_obj(self):
        return self.adaptor.construct_multi(self.backend_objs())
    
    
    
    def save(self, destination=None, combine=False):
        if combine:
            if destination is None:
                if not hasattr(self, "file") or not self.file:
                    raise ValueError("Could not find destination name.")
                destination = self.default_destination()
            self.adaptor.save(self.backend_obj, destination)
            return destination
        destinations = []
        for num in range(len(self.sequence)):
            single = self.sequence[num]
            dest = None
            if destination is None and not self.adaptor.save_in_place:
                if not single.file:  # this means we need to find dest otherwise
                    if not hasattr(self, "file") or not self.file:
                        raise ValueError("Could not find destination name.")
                    new_folder = path.join(self.folder, self.filename + edit_tag)
                    os.makedirs(new_folder, exist_ok=True)
                    destination = path.join(new_folder, self.filename + self.ext)
            if destination:
                base, ext = path.splitext(destination)
                dest = base + f"_{num}" + ext
            destinations.append(single.save(destination=dest))
        return destinations
    
    
    def close(self):
        for im in self.sequence: im.close()
        super().close()
    
    
    # def __getattr__(self, item):
    #     if self.backend_obj:
    #         return super().__getattr__(item)
    #     else:
    #         attrs = []
    #         for im in self.sequence:
    #             try:
    #                 attrs.append(getattr(im,item))
    #             except AttributeError:
    #                 warn(f"Subimage {im} of ImageSequence {self} does not "
    #                           f"have attr {item}.")
    #         if not attrs: raise AttributeError(item)
    #         if all(callable(a) for a in attrs):
    #             def func(*args,**kwargs):
    #                 ret = []
    #                 for attr in attrs: ret.append(attr(*args,**kwargs))
    #                 if all(r==ret[0] for r in ret): return ret[0]
    #                 return ret
    #             return func
    #         elif all(a==attrs[0] for a in attrs):
    #             return attrs[0]
    #         else:
    #             return attrs
    
    def __getitem__(self, item):
        ims = self.sequence[item]
        if isinstance(item, int):
            check_type(self.SingleClass, ims)
            return ims
        if isinstance(item, slice):
            return self.__class__(images=ims)
        raise NotImplementedError
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.sequence == other.sequence
        return NotImplemented
    
    def __hash__(self):
        return hash(self.sequence)