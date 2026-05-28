from ... import Adaptor, adaptionmethod
from time import sleep
from Dhelpers.baseclasses import TimedObject
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



class VolumeMonitor(VolumeAdaptor.AdaptiveClass, TimedObject):
    
    adaptor = VolumeAdaptor(group="VolumeMonitor", _primary_name=
        "VolumeMonitor.adaptor")

    def __init__(self,stream=None, timeout=60, interval=0.5):
        self.stream = stream
        self.interval = interval
        self.initial = self.adaptor.get(stream)
        super().__init__(timeout=timeout)

    def checker_thread(self):
        for _ in range(int(self.timeout/self.interval)):
            current, max, name = self.adaptor.get(self.stream)
            #print(current)
            if current != self.initial[0]:
                print(current, "  stopped")
                self.stop()
                return
            sleep(self.interval)
    
    def _start_action(self):
        self._checker_thread = launch.thread(self.checker_thread)
    
    def _stop_action(self):
        try:
            self._checker_thread.cancel()
        except:
            pass
    
    