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
from .volumepower import *

tts = TextToSpeechAdaptor(_primary_name="tts")
play = SoundPlayAdaptor(_primary_name="play")
vol = VolumeAdaptor(_primary_name="vol")

from ..notificationpower import NotificationAdaptor
from ..clipboardpower import ClipboardAdaptor

from Dhelpers.baseclasses import TimedCheckerObject


class SoundToolsMixin:
    silent = False
    last_heard = None
    before_last_heard = None
    frequency_before_recognize = 1600
    frequency_abort = 300
    frequency_vol_up= 800
    frequency_vol_down = 600
    vol_up_options = []
    vol_down_options = []
    vol_stream = None
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
        cls.vol = VolumeAdaptor(group=group)
    
    @classmethod
    def auto_adapt_all(cls):
        cls.tts.adapt()
        cls.ntfy.adapt()
        cls.clip.adapt()
        cls.recognizer.adapt()
        cls.play.adapt()
        cls.vol.adapt()
    
    def speak(self, text):
        if self.silent:
            self.ntfy(text)
        else:
            self.tts(text)
    
    def get_voice(self, question=None, language=None, beep=True, notify=False,vol_up=[],vol_down=[]):
        if question: self.speak(question)
        if beep:
            if self.frequency_before_recognize:
                self.beep(self.frequency_before_recognize)
            else:
                self.beep(beep)
        if not language: language = self.recognizer_language
        vol_up=vol_up if vol_up else self.vol_up_options
        vol_down=vol_down if vol_down else self.vol_down_options
        if vol_up or vol_down: 
            with self.VolumeInput(self,vol_up,vol_down,20) as volinp:
                heard = self.recognize(language)
            if volinp.option: heard = volinp.option
        else:
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

    
    
    
    class VolumeInput(TimedCheckerObject):

    
        def __init__(self,soundtools, vol_up=[], vol_down=[], timeout=60, interval=0.1):
            self.st=soundtools
            self.initial = self.get_vol()
            self.val = 0
            self.option=None
            self.vol_up_options = vol_up
            self.vol_down_options = vol_down
            super().__init__(timeout=timeout, interval=interval)

        def get_vol(self):
            return self.st.vol.get(self.st.vol_stream)[0]

        def reset_vol(self):
            self.st.vol.set(self.initial,self.st.vol_stream)
    
        def check_condition(self):
            st=self.st
            current = self.get_vol()
            #print(current)
            if current < self.initial:
                self.reset_vol()
                if self.val > 0: return True
                self.val -= 1
                st.beep(st.frequency_vol_down)
            elif current> self.initial:
                self.reset_vol()
                if self.val < 0: return True
                self.val += 1
                st.beep(st.frequency_vol_up)

        def _stop_action(self):
            ret = self.val
            if ret > 0:
                self.option = self.vol_up_options[ret-1]
            elif ret < 0:
                self.option = self.vol_down_options[-ret-1]

    
SoundToolsMixin.create_adaptor_instances()
        

from .VoiceAssistant import *
