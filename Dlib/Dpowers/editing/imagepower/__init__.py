from ..ressource_classes import EditorAdaptor, adaptionmethod, Resource
from types import GeneratorType
iter_types = (list,tuple,GeneratorType)



class ImageAdaptor(EditorAdaptor):
    
    @adaptionmethod
    def compression(self, backend_obj, value=None):
        return self.compression.target_with_args()
    
    @adaptionmethod
    def compr_quality(self, backend_obj, value=None):
        return self.compr_quality.target_with_args()


    @adaptionmethod
    def resolution(self, backend_obj, value=None):
        return self.resolution.target_with_args()

    @adaptionmethod
    def size(self, backend_obj, value=None):
        return self.size.target_with_args()



class ImageBase(Resource, ImageAdaptor.coupled_class()):
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        multi = type(cls.__name__+".multipage", (multipage, cls.Sequence),{})
        multi.__module__ = cls.__module__
        cls.multipage = multi
        
    # def compression(self, value=None):
    #     return self.adaptor.compression(self.backend_obj, value)
    # compr = compression
    #
    # def compr_quality(self, value=None):
    #     return self.adaptor.compr_quality(self.backend_obj, value)
    # compression_qiality = compr_quality
    # compr_qu = compr_quality
    # compqual = compr_quality
    #
    # def size(self, value=None):
    #     return self.adaptor.size(self.backend_obj, value)
    #
    # def res(self, value=None):
    #     return self.adaptor.resolution(self.backend_obj, value)
    # resolution = res

ImageBase.set_prop("compression", "compr")
ImageBase.set_prop("compr_quality", "compression_quality", "comprqu",
        "compr_q", "compr_qu", "comprq")
ImageBase.set_prop("size")
ImageBase.set_prop("resolution", "res")



class multipage:
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        self.file=file
        if isinstance(file,iter_types): raise ValueError
        self.file = file
        self.filepath_split()
        backend_objs = self.adaptor.load_multi(file,
                resolution= resolution, **load_kwargs)
        images = tuple(self.SingleClass(backend_obj=bo) for bo in backend_objs)
        super().__init__(images=images)
        self.compr("jpeg")
    
    def save(self, destination=None, combine=True):
        return super().save(destination, combine)