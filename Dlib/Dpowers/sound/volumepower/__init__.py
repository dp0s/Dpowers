from ... import Adaptor, adaptionmethod
from time import sleep
from Dhelpers.baseclasses import TimedObject

class VolumeAdaptor(Adaptor):
    
    
    @adaptionmethod
    def get(self, stream=None):
        dict = self.get.target()
        if stream:
            return dict[stream]
        return dict

    @adaptionmethod
    def set(self,new_level,stream="media"):
        self.set.target(new_level,stream)

    def increase(self,step=1, stream="media"):
        current, max = self.get(stream)
        new = current + step
        if new < 0 or new > max: 
            raise ValueError(f"Increasing by {step} not possible.") 
        self.set(new, stream)


class VolumeMonitor(VolumeAdaptor.AdaptiveClass, TimedObject):

    def __init__(self,stream="media", timeout=60):
        self.stream = stream
        self.initial = self.adaptor.get(stream)
        super().__init__(timeout=timeout)

    def checker_thread(self):
        current = self.adaptor.get(stream)
        if current != self.initial: print(current)