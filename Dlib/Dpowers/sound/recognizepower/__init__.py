from ... import Adaptor, adaptionmethod

class VoiceRecognizeAdaptor(Adaptor):
    
    def __call__(self, text):
        return self.call(text)
    
    @adaptionmethod
    def call(self):
        return self.call.target_with_args()

