from ... import Adaptor, adaptionmethod


class SoundPlayAdaptor(Adaptor):
    
    
    @adaptionmethod
    def beep(self, frequency=440, duration=0.3):
        self.beep.target(frequency, duration)