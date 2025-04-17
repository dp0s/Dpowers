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
from ... import Adaptor, adaptionmethod, NotificationAdaptor
import time


class TextToSpeechAdaptor(Adaptor):
    
    ntfy = NotificationAdaptor(group="tts")
    
    def __call__(self, text):
        return self.call(text)
    
    @adaptionmethod
    def call(self, text, notify=True):
        if notify: self.ntfy(f"'{text}'", 10, "Read aloud by TTS")
        return self.call.target(text)
    
    @property
    def volume(self):
        return self.set_volume()
    
    @volume.setter
    def volume(self, val):
        self.set_volume(val)
    
    @adaptionmethod
    def set_volume(self, value=None):
        return self.set_volume.target_with_args()