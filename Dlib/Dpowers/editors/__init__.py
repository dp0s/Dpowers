from Dpowers import Adaptor, adaptionmethod
from types import GeneratorType
from Dhelpers.arghandling import check_type, CollectionWithProps
from Dhelpers.named import NamedObj
import os, warnings

path = os.path

iter_types = (list, tuple, GeneratorType)

class ClosedResource: pass

class CloseResourceError(Exception): pass


edit_tag = "__edit"



class EditorAdaptor(Adaptor):
    attr_dict = {}
    defined_names = {}
    
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
    def set_value(self, backend_obj, name, value=None):
        self._check(backend_obj)
        attr = self.attr_dict.get(name, name)
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