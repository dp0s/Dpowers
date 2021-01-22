from Dpowers import Adaptor, adaptionmethod
from types import GeneratorType
from Dhelpers.arghandling import check_type, CollectionWithProps
from Dhelpers.named import NamedObj
import os, warnings
path = os.path

iter_types = (list,tuple,GeneratorType)
class ClosedResource: pass
class CloseResourceError(Exception): pass


edit_tag = "__edit"




class ImageAdaptor(Adaptor):
    
    attr_dict = {}
    defined_names ={}
    
    @adaptionmethod
    def image_class(self):
        return self.image_class.target
    
    def _check(self, obj):
        if isinstance(obj, iter_types):
            for o in obj:
                if not isinstance(o, self.image_class()): raise TypeError
        else:
            if not isinstance(obj, self.image_class()): raise TypeError
        return obj
    
    @adaptionmethod(require=True)
    def load(self, file, **load_kwargs):
        backend_object = self._check(self.load.target_with_args())
        return backend_object

    @adaptionmethod
    def load_multipage(self, file, **load_kwargs):
        backend_objects = self._check(self.load_multipage.target_with_args())
        return backend_objects
    
    @adaptionmethod
    def construct_multi(self, sequence_of_backend_objs):
        sequ = tuple(sequence_of_backend_objs)
        self._check(sequ)
        return self.construct_multi.target(sequ)
    
    @adaptionmethod(require=True)
    def save(self, backend_obj, destination):
        self._check(backend_obj)
        self.save.target_with_args()
        
    @adaptionmethod(require=True)
    def close(self, backend_obj):
        self._check(backend_obj)
        self.close.target_with_args()
        
    @adaptionmethod
    def set_value(self, backend_obj, name, value = None):
        self._check(backend_obj)
        attr = self.attr_dict.get(name,name)
        try:
            ret = self.set_value.target(backend_obj, attr, value)
        except AttributeError:
            raise NotImplementedError
        return ret
    
    @set_value.target_modifier
    def _get_values(self, target, amethod):
        al = amethod.target_space.attr_list
        self.attr_dict = NamedAttr.StandardizingDict(al)
        self.defined_names = self.attr_dict.normal_version(all=True)
        return target
    

class NamedAttr(NamedObj):
    pass

@NamedAttr.update_names
class attr_names:
    compression = "compression", "compr"
    resolution = "resolution", "res"
    compression_quality = "compression_quality", "compr_quality", "compr_qu"
    size = "size"

    
    
class Resource:
    
    
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
    
    def default_destination(self,num=None):
        append = edit_tag
        if num: append += f"_{num}"
        return path.join(self.folder,self.filename + edit_tag + self.ext)


    def __enter__(self):
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        if self.backend_obj: self.adaptor.close(self.backend_obj)
        self.backend_obj = ClosedResource
        
    def set_value(self, name, value=None):
        return self.adaptor.set_value(self.backend_obj, name, value)
    
    
    def __getattr__(self, item):
        names = self.adaptor.defined_names
        try:
            name = names[item]
        except KeyError:
            raise AttributeError
        def func(value=None):
            return self.set_value(name, value)
        func.__name__ = item
        return func
    
    
    def __add__(self, other):
        seq = self.sequence
        assert all(type(s) is self.SingleClass for s in seq)
        try:
            if all(type(s) is self.SingleClass for s in other.sequence):
                return self.SingleClass.Sequence(
                        images=self.sequence+other.sequence)
        except AttributeError:
            pass
        return NotImplemented
    
    
    
    
class ImageBase(Resource, ImageAdaptor.coupled_class()):
    
    def __init_subclass__(cls):
        Sequence = type("ImageSequence",(ImageSequence,),{})
        Sequence.__module__ = ImageSequence.__module__
        Sequence.SingleClass = cls
        cls.SingleClass = cls
        cls.Sequence = Sequence
        cls.multipage = type("multipage", (multipage, Sequence),{})
        super().__init_subclass__()
        
    
    def __init__(self, file=None, backend_obj=None, **load_kwargs):
        if isinstance(file,iter_types) or isinstance(backend_obj, iter_types):
            raise ValueError
        self.file = file
        self.backend_obj = backend_obj
        if file:
            assert backend_obj is None
            self.filepath_split()
            self.backend_obj = self.adaptor.load(file, **load_kwargs)
            # this happens if a pdf is opend e.g.
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
        if destination is None: destination = self.default_destination()
        self.adaptor.save(self.backend_obj, destination)
        return destination
        
    
    # def __getattr__(self, item):
    #     if item in self.adaptor.adaptionmethod_names:
    #         amethod = getattr(self.adaptor,item)
    #         def amethod_call(*args,**kwargs):
    #             return amethod(self.backend_obj, *args,**kwargs)
    #         return amethod_call
    #     return super().__getattr__(item)
    
    
class ImageSequence(Resource):
    
    SingleClass = None  # set by init subclass form Image class
    
    
    def __init__(self, files=None, images=None, **load_kwargs):
        self.files = files
        if files:
            check_type(iter_types, files)
            assert images is None
            self.sequence = tuple(self.SingleClass(file=f, **load_kwargs)
                for f in files)
            
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
    
    
    def set_value(self, name, value=None):
        val = None
        if self.backend_obj: val = super().set_value(name, value)
        vals = []
        for im in self.sequence:
            vals.append(im.set_value(name,value))
        return val, vals



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
            im = self.sequence[num]
            dest = None
            if destination is None:
                if not im.file: #this means we need to find dest otherwise
                    if not hasattr(self, "file") or not self.file:
                        raise ValueError("Could not find destination name.")
                    new_folder = path.join(self.folder,self.filename+edit_tag)
                    os.makedirs(new_folder, exist_ok=True)
                    destination = path.join(new_folder, self.filename+self.ext)
            if destination:
                base, ext = path.splitext(destination)
                dest = base + f"_{num}" + ext
            destinations.append(im.save(destination=dest))
        return destinations
            
    
    def close(self):
        for im in self.sequence: im.close()
        super().close()
    
    
    # def __getattr__(self, item):
    #     if item in self.adaptor.adaptionmethod_names:
    #         amethod = getattr(self.adaptor,item)
    #         def amethod_call(*args,**kwargs):
    #             for im in self.sequence:
    #                 amethod(im.backend_obj, *args,**kwargs)
    #             if self.backend_obj:
    #                 amethod(self.backend_obj, *args,**kwargs)
    #         return amethod_call
    #     if self.backend_obj:
    #         return super().__getattr__(item)
    #     else:
    #         attrs = []
    #         for im in self.sequence:
    #             try:
    #                 attrs.append(getattr(im,item))
    #             except AttributeError:
    #                 warnings.warn(f"Subimage {im} of ImageSequence {self} does not "
    #                               f"have attr {item}.")
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
            return self.__class__(images = ims)
        raise NotImplementedError
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return self.sequence == other.sequence
        return NotImplemented
    
    def __hash__(self):
        return hash(self.sequence)


class multipage(ImageSequence):
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        self.file=file
        if isinstance(file,iter_types): raise ValueError
        self.file = file
        self.filepath_split()
        backend_objs = self.adaptor.load_multipage(file,
                resolution= resolution, **load_kwargs)
        images = tuple(self.SingleClass(backend_obj=bo) for bo in backend_objs)
        super().__init__(images=images)
        self.compr("jpeg")
    
    def save(self, destination=None, combine=True):
        return super().save(destination, combine)