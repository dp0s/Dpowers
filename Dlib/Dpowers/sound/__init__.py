#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
from .ttspower import *
from .soundplaypower import *
from .recognizepower import *

tts = TextToSpeechAdaptor(_primary_name="tts")
play = SoundPlayAdaptor(_primary_name="play")

from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor



class SoundToolsMixin:
    silent = False
    last_heard = None
    before_last_heard = None
    frequency_before_recognize = 1600
    frequency_abort = 300
    group = "soundtools"
    recognizer_language = None
    
    @classmethod
    def create_adaptor_instances(cls, group=None):
        if not group: group = cls.group
        cls.tts = TextToSpeechAdaptor(group=group)
        cls.ntfy = NotificationAdaptor(group=group)
        cls.tts.ntfy = cls.ntfy
        cls.clip = ClipboardAdaptor(group=group)
        cls.recognizer = RecognizerAdaptor(group=group)
        cls.play = SoundPlayAdaptor(group=group)
    
    @classmethod
    def auto_adapt_all(cls):
        cls.tts.adapt()
        cls.ntfy.adapt()
        cls.clip.adapt()
        cls.recognizer.adapt()
        cls.play.adapt()
    
    def speak(self, text):
        if self.silent:
            self.ntfy(text)
        else:
            self.tts(text)
    
    def get_voice(self, question=None, language=None, beep=True, notify=False):
        if question: self.speak(question)
        if beep:
            if self.frequency_before_recognize:
                self.beep(self.frequency_before_recognize)
            else:
                self.beep(beep)
        if not language: language = self.recognizer_language
        heard = self.recognize(language)
        if heard:
            if notify: self.ntfy("Heard: " + heard)
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
    
    def recognize(self, language=None):
        return self.recognizer.recognize(language)
    
    
SoundToolsMixin.create_adaptor_instances()

from .VoiceAssistant import *
