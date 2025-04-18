from .ttspower import TextToSpeechAdaptor
from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor
import types
from Dhelpers.named import NamedObj


import sounddevice #this is important because it suppresses error messages
# from pyaudio when listening from microphone
import speech_recognition as sr

# from contextlib import contextmanager
# from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
# #import pyaudio
#
# ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
#
# def py_error_handler(filename, line, function, err, fmt):
#     pass
#
# c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
#
# @contextmanager
# def noalsaerr():
#     asound = cdll.LoadLibrary('libasound.so')
#     asound.snd_lib_error_set_handler(c_error_handler)
#     yield
#     asound.snd_lib_error_set_handler(None)



class VoiceAssistantResource:
    tts = TextToSpeechAdaptor(group="voice_assistant")
    ntfy = NotificationAdaptor(group="tts")
    tts.ntfy = ntfy
    clip = ClipboardAdaptor(group="voice_assistant")
    silent = False
    recognizer = sr.Recognizer()
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
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
        # recognize speech using whisper
        try:
            return self.recognizer.recognize_faster_whisper(audio,
                    language="de")
        except sr.UnknownValueError:
            print("Whisper could not understand audio")
            raise
        except sr.RequestError as e:
            print(f"Could not request results from Whisper; {e}")
            raise


    
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
    

    
    

