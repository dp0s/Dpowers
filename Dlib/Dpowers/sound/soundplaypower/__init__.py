from ... import Adaptor, adaptionmethod
from time import sleep

class SoundPlayAdaptor(Adaptor):
    
    
    @adaptionmethod
    def beep(self, frequency=440, duration=0.3, repeat=1, pause=None):
        if repeat>1 and pause is None: pause=duration
        for _ in range(repeat):
            self.beep.target(frequency, duration)
            sleep(duration)
            if pause: sleep(pause)