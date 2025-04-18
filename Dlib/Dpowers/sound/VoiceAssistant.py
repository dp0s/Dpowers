from .ttspower import TextToSpeechAdaptor
from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor
from .recognizepower import RecognizerAdaptor
import types
from Dhelpers.named import NamedObj



class VoiceAssistantResource:
    tts = TextToSpeechAdaptor(group="voice_assistant")
    ntfy = NotificationAdaptor(group="tts")
    tts.ntfy = ntfy
    clip = ClipboardAdaptor(group="voice_assistant")
    recognizer = RecognizerAdaptor(group="voice_assistant")
    silent = False
    last_heard = None
    before_last_heard = None
        
    def speak(self, text):
        if self.silent:
            self.ntfy(text)
        else:
            self.tts(text)
            
    def get_voice(self):
        self.beep(6000,500)
        heard = self.recognize()
        if heard:
            self.ntfy("Heard: "+heard)
            heard = heard.lower().strip()
            self.before_last_heard = self.last_heard
            self.last_heard = heard
            return heard
        else:
            self.ntfy("Nothing heard")
            
        
        
    def run(self):
        raise NotImplementedError
    
    def beep(self, *args):
        return
    
    def recognize(self):
        return self.recognizer.recognize()


    
class VoiceChoice(VoiceAssistantResource):
    
    def __init__(self, question=None):
        self.question = question
        class NamedOption(NamedObj):
            pass
        self.OptionClass = NamedOption
        self.stopp_phrases = ["stopp", "da"]
        self.edit_phrases = ["ändern", "andern", "ende"]
        self.new_word_phrase = "Neues Wort hinzufügen"
        self.unknown_phrase = "Unbekannt: "

    def run(self, repeat=10):
        for _ in range(repeat):
            if self.question: self.speak(self.question)
            heard = self.get_voice()
            if not heard or heard in self.stopp_phrases:
                self.beep(1200, 500)
                self.tts("Stop phrase heard")
                return
            if heard in self.edit_phrases:
                self.speak(self.new_word_phrase)
                self.clip.fill(heard)
                self.open_for_edit()
                return
            if heard is True: return
            try:
                return self.OptionClass.instance(heard)
            except KeyError:
                if self.silent is False:
                    self.speak(self.unknown_phrase + heard)
    
    def define_method(self, func):
        method = types.MethodType(func, self)
        setattr(self, func.__name__, method)
        
    def open_for_edit(self):
        raise NotImplementedError
    

    
    

