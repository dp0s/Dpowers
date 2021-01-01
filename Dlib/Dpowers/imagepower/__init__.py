from .. import Adaptor, adaptionmethod


class ImageAdaptor(Adaptor):
    
    @adaptionmethod
    def image_class(self):
        return self.image_class.target
    
    def _check(self, obj):
        if not isinstance(obj, self.image_class()): raise TypeError
    
    @adaptionmethod
    def load(self, file):
        backend_object = self.load.target(file)
        self._check(backend_object)
        return backend_object
    
    @adaptionmethod
    def save(self, backend_object, destination):
        self._check(backend_object)
        self.save.target_with_args()
        
    @adaptionmethod
    def close(self, backend_obj):
        self._check(backend_obj)
        self.close.target_with_args()
    

class ImageBase(ImageAdaptor.coupled_class()):
    
    def __init__(self, file):
        self.file = file
        self.backend_object = self.adaptor.load(file)
        
    def save(self, destination):
        self.adaptor.save(self.backend_object, destination)
        
    def __enter__(self):
        try:
            enter = self.backend_object.__enter__
        except AttributeError:
            pass
        else:
            enter()
        return self
    
    def close(self):
        self.adaptor.close(self.backend_object)
        del self.backend_object
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            exit = self.backend_object.__exit__
        except AttributeError:
            self.close()
        else:
            ret = exit(exc_type, exc_val, exc_tb)
            del self.backend_object
            return ret