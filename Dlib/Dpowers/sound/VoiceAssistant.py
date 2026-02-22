from . import SoundToolsMixin
from Dhelpers.named import NamedObj
import types

class VoiceChoice(SoundToolsMixin):
    question = None
    choices = None
    stop_phrases = []
    edit_phrases = []
    new_word_phrase = []
    unknown_phrase = []
    
    def __init__(self, question=None, choices=None):
        if question: self.question = question
        if not self.question: raise ValueError
        class NamedOption(NamedObj):
            pass
        self.OptionClass = NamedOption
        if choices: self.choices = choices
        if not self.choices: raise ValueError
        self.update_names(self.choices)
    
    def update_names(self, new_info):
        return self.OptionClass.update_names(new_info)
    
    def process_heard(self, heard):
        if not heard or heard in self.stop_phrases:
            self.beep(self.frequency_abort)
            # self.ntfy("Stop phrase heard")
            return False
        if heard in self.edit_phrases:
            self.speak(self.new_word_phrase)
            self.clip.fill(heard)
            self.open_for_edit()
            return False
        if heard is True: return
        try:
            return self.OptionClass.instance(heard)
        except KeyError:
            if self.silent is False:
                self.speak(self.unknown_phrase + heard)
    
    def run(self, repeat=10):
        obj = None
        for _ in range(repeat):
            heard = self.get_voice(self.question)
            obj = self.process_heard(heard)
            if obj or obj is False: break
        if obj: self.process_result(obj)
    
    def process_result(self, obj):
        raise NotImplementedError
    
    
    def define_method(self, func):
        method = types.MethodType(func, self)
        setattr(self, func.__name__, method)
    
    def open_for_edit(self):
        raise NotImplementedError



class CleverAssistant(SoundToolsMixin):
    # Allows to combine several VoiceChoices into a single Assistant
    
    def __init__(self, question=None):
        self.question = question
        self.choices = {}
    
    def add_voice_choice(self, VoiceAssistantInstance, catchword):
        self.choices[catchword.lower()] = VoiceAssistantInstance
    
    @property
    def stop_phrases(self):
        for cls in self.choices.values():
            if cls.stop_phrases: return cls.stop_phrases
            
    @property
    def recognizer_language(self):
        for cls in self.choices.values():
            if cls.recognizer_language: return cls.recognizer_language
    
    def run(self, repeat=10):
        obj = None
        for _ in range(repeat):
            heard = self.get_voice(self.question)
            if not heard or heard in self.stop_phrases:
                self.beep(self.frequency_abort)
                # self.ntfy("Stop phrase heard")
                return
            words = heard.split(" ")
            if len(words) <= 1: continue
            try:
                VA_inst = self.choices[words[0]]
            except KeyError:
                self.speak("No catchword heard.")
                continue
            obj = VA_inst.process_heard(words[1:].join(" "))
            if obj or obj is False: break
        if obj: VA_inst.process_result(obj)