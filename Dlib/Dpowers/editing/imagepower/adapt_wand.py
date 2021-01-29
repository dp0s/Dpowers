from wand.image import Image

obj_class = Image


def load(file, **kwargs):
    with Image(filename=file, **kwargs) as im:
        s = im.sequence
        if len(s) == 0: raise ValueError
        if len(s) == 1: return im.clone()
        raise ValueError(f"More than one image in file {file}.")
    
def load_multipage(file, **kwargs):
    with Image(filename=file, **kwargs) as im:
        s = im.sequence
        if len(s) == 0: raise ValueError
        return tuple(Image(i) for i in s)
    

def construct_multi(sequence_of_objs):
    im  = Image()
    for o in sequence_of_objs:
        im.sequence.append(o)
    return im

def save(obj, destination):
    obj.save(filename = destination)
    
def close(obj):
    obj.destroy()

def compression(obj, value):
    if value is None: return obj.compression
    obj.compression = value

def compr_quality(obj, value):
    if value is None: return obj.compression_quality
    obj.compression_quality = value
    
def resolution(obj, value):
    if value is None: return obj.resolution
    obj.resolution = value

def size(obj, value):
    if value is None: return obj.size
    obj.size = value

def set_value(backend_obj, name, value = None):
    val_before = getattr(backend_obj, name)
    if value is None: return val_before
    return setattr(backend_obj, name, value)