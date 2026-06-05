from ... import Adaptor, adaptionmethod
from time import sleep
from Dhelpers.launcher import launch

class VolumeAdaptor(Adaptor):
    
    @adaptionmethod
    def stream_names(self):
        return self.stream_names.target()
    
    @adaptionmethod
    def get(self, stream=None):
        ret = self.get.target(stream)
        if ret is False:
            raise ValueError(f"No stream '{stream}' found. Availabe: "
                             f"{self.stream_names()}")
        return ret

    @adaptionmethod
    def set(self,new_level,stream=None):
        ret = self.set.target(new_level,stream)
        if ret is False:
            raise ValueError(f"No stream '{stream}' found. Availabe: "
                             f"{self.stream_names()}")
        return ret

    def increase(self,step=1, stream=None):
        current, max, name = self.get(stream)
        if max == 1 and step == 1: step= 0.1
        new = current + step
        #if new < 0 or new > max:
         #   raise ValueError(f"Increasing by {step} not possible.")
        self.set(new, stream)

    
            