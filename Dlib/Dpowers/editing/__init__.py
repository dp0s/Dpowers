from .imagepower import *
from .mp3power import *



class Image(ImageBase):
    adaptor = ImageAdaptor(_primary=True)
    
    
class mp3tag(mp3tagBase):
    adaptor = mp3tagAdaptor(_primary=True)
    
    
from .FileSelector import *