#
#
# Copyright (c) 2020 DPS, dps@my.mail.de
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

import time
from ... import adaptionmethod, hotkeys, NamedKey
from ..event_sender import AdaptivePressReleaseSender

class KeyboardAdaptor(AdaptivePressReleaseSender):
    
    #inherits adaptionmethods _press and _rls
    
    @property
    def NamedClass(self):
        return self.NamedKeyClass
    @NamedClass.setter
    def NamedClass(self, val):
        if not issubclass(val, NamedKey): raise TypeError
        self.NamedKeyClass = val
        self._update_stand_dicts()
    
    @property
    def key(self):
        return self.NamedKeyClass.NameContainer

    @adaptionmethod("text")
    def _text(self, string):
        func = self._text.target
        if func is NotImplemented: func = self.tap
        for character in string:
            func(character)
            
    @_text.target_modifier
    def _text_tm(self, target):
        if target is NotImplemented: target = self.tap
        return target
