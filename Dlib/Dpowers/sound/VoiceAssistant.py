from .ttspower import TextToSpeechAdaptor
from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor
from .recognizepower import RecognizerAdaptor
from .soundplaypower import SoundPlayAdaptor
import types
from Dhelpers.named import NamedObj



class VoiceAssistantResource:
    tts = TextToSpeechAdaptor(group="voice_assistant")
    ntfy = NotificationAdaptor(group="tts")
    tts.ntfy = ntfy
    clip = ClipboardAdaptor(group="voice_assistant")
    recognizer = RecognizerAdaptor(group="voice_assistant")
    play = SoundPlayAdaptor(group="voice_assistant")
    silent = False
    last_heard = None
    before_last_heard = None
    frequency_before_recognize = 1600
    frequency_abort = 300
    
    def speak(self, text):
        if self.silent:
            self.ntfy(text)
        else:
            self.tts(text)
            
    def get_voice(self, question=None, beep=True):
        if question: self.speak(question)
        if beep:
            if self.frequency_before_recognize:
                self.beep(self.frequency_before_recognize)
            else:
                self.beep(beep)
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
    
    def beep(self, *args, **kwargs):
        self.play.beep(*args, **kwargs)
    
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
            heard = self.get_voice(self.question)
            if not heard or heard in self.stopp_phrases:
                self.beep(self.frequency_abort)
                #self.ntfy("Stop phrase heard")
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
    

    
    

