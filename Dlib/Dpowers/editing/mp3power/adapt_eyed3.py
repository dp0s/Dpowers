import eyed3.mp3


obj_class = eyed3.mp3.Mp3AudioFile
eyed3.log.setLevel("ERROR")

def load(file, **kwargs):
    return eyed3.load(file)

def save(backend_obj, destination):
    backend_obj.tag.save(destination)


def genre(backend_obj, val):
    t = backend_obj.tag
    if val is None:
        if t is None: return ""
        g = backend_obj.tag.genre
        if g is None: return ""
        return g.name
    backend_obj.tag.genre = val
    
def close(backend_obj):
    pass