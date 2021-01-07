from .. import Adaptor, adaptionmethod
from types import GeneratorType
from Dhelpers.arghandling import check_type, CollectionWithProps
import os
path = os.path

iter_types = (list,tuple,GeneratorType)
class ClosedResource: pass
class CloseResourceError(Exception): pass


edit_tag = "__Dpowers_edit"

class ImageAdaptor(Adaptor):
    
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
    
    
    
class Resource:
    
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
    
    def save(self, destination=None):
        if destination is None: destination = self.default_destination()
        self.adaptor.save(self.backend_obj, destination)
        return destination

    def close(self):
        self.adaptor.close(self.backend_obj)
        self.backend_obj = ClosedResource
    
    def __enter__(self):
        try:
            enter = self.backend_obj.__enter__
        except AttributeError:
            pass
        else:
            enter()
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            exit = self.backend_obj.__exit__
        except AttributeError:
            self.close()
        else:
            exit(exc_type, exc_val, exc_tb)
            self.backend_obj = ClosedResource
    
    
    def __getattr__(self, item):
        try:
            attr = getattr(self.backend_obj, item)
        except AttributeError:
            raise AttributeError(item)
        else:
            return attr


   
    
    
    

class ImageBase(Resource, ImageAdaptor.coupled_class()):
    
    def __init_subclass__(cls):
        Sequence = type("ImageSequence",(ImageSequence,),{})
        Sequence.__module__ = ImageSequence.__module__
        Sequence.ImageClass = cls
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
        
    
    
class ImageSequence(Resource):
    
    ImageClass = None  # set by init subclass form Image class
    
    
    def __init__(self, files=None, images=None, **load_kwargs):
        self.files = files
        if files:
            check_type(iter_types, files)
            assert images is None
            self.sequence = tuple(self.ImageClass(file=f, **load_kwargs)
                for f in files)
            
        elif images:
            assert files is None
            assert load_kwargs == {}
            check_type(CollectionWithProps(self.ImageClass, minlen=1), images)
            self.sequence = images

    @property
    def adaptor(self):
        return self.ImageClass.adaptor

    def backend_objs(self):
        return tuple(im.backend_obj for im in self.sequence)

    def backend_obj(self):
        return self.adaptor.construct_multi(self.backend_objs())
    
    
    def save(self, destination=None, combine=False):
        if combine:
            if destination is None:
                if not hasattr(self, "file") or not self.file:
                    raise ValueError("Could not find destination name.")
                destination = self.default_destination()
            self.adaptor.save(self.backend_obj(), destination)
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
        
    
    def __enter__(self):
        for im in self.sequence: im.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for im in self.sequence: im.__exit__(exc_type, exc_val, exc_tb)
    
    
    def __getattr__(self, item):
        attrs = []
        for im in self.sequence:
            try:
                attrs.append(getattr(im.item))
            except AttributeError:
                pass
        if not attrs: raise AttributeError(item)
        def func(*args,**kwargs):
            for attr in attrs: attr(*args,**kwargs)
        return func




class multipage:
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        self.file=file
        if isinstance(file,iter_types): raise ValueError
        self.file = file
        self.filepath_split()
        backend_objs = self.adaptor.load_multipage(file,
                resolution= resolution, **load_kwargs)
        images = tuple(self.ImageClass(backend_obj=bo) for bo in backend_objs)
        super().__init__(images=images)
    
    def save(self, destination=None, combine=True):
        return super().save(destination, combine)