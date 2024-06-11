from .ttspower import TextToSpeechAdaptor
from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor
import types

class Question:
    
    def __init__(self, to_speak):
        self.to_speak = to_speak
        

class VoiceAssistantBase:

    
    def __init__(self):
        self.tts = TextToSpeechAdaptor(group="voice_assistant")
        self.ntfy = NotificationAdaptor(group="voice_assistant")
        self.clip = ClipboardAdaptor(group="voice_assistant")
        self.silent = False
        self.last_heard = None
        self.before_last_heard = None
        
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
    
    
    
class SimpleVoiceAssistant(VoiceAssistantBase):
    
    question = None
    
    
    def __init__(self, question=None):
        super().__init__()
        if question: self.question = question
        self.stopp_phrases = ["stopp", "da"]
        self.edit_phrases = ["ändern", "andern", "ende"]
        self.new_word_phrase = "Neues Wort hinzufügen"
        self.unknown_phrase = "Unbekannt:"
        
    def run(self):
        for _ in range(10):
            self.speak(self.question)
            heard = self.get_voice()
            if not heard or heard in self.stopp_phrases:
                self.beep(1200,500)
                return
            if heard in self.edit_phrases:
                self.speak(self.new_word_phrase)
                self.clip.fill(heard)
                self.open_for_edit()
                return
            ret = self.analyze_heard(heard)
            if ret is True: return
            if ret != "silent": self.speak(self.unknown_phrase + " " + heard)
        
    def open_for_edit(self):
        raise NotImplementedError
    
    def analyze_heard(self, heard):
        raise NotImplementedError
    
    def define_method(self, func):
        method = types.MethodType(func, self)
        setattr(self, func.__name__, method)
    
    

class PlaylistAssistant(SimpleVoiceAssistant):
    
    question = "Welche Playlist?"

    def analyze_heard(self, heard):
        try:
            playlist_name = playlist_dic[heard]
        except KeyError:
            return
        self.speak("Spiele Playlist "+playlist_name)
        self.start_playlist(playlist_name) #tbc
        return True
    
    def start_playlist(self, playlist_name):
        raise NotImplementedError
    


Playlists = {"01 Meditation": ["meditation", "medikation"]}


playlist_dic = {}
for key, val in Playlists.items():
    for name in val:
        playlist_dic[name]=key