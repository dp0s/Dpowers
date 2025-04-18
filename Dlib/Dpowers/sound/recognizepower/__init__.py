from ... import Adaptor, adaptionmethod, NotificationAdaptor


class RecognizerAdaptor(Adaptor):
    
    language = "en"
    @adaptionmethod
    def recognize(self, language = None):
        if language is None: language = self.language
        return self.recognize.target(language)