from wand.image import Image

image_class = Image


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