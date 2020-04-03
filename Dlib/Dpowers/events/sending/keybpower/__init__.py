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
from ... import Adaptor, adaptionmethod, hotkeys, Keyvent
from ..event_sender import PressReleaseSender

class KeyboardAdaptor(Adaptor, PressReleaseSender):
    
    default_delay = None
    
    def __getattr__(self, item):
        # this allows keyb.key to dynamically reference the current
        # NamedKeyClass even if it is changed
        if item == "key": return self.NamedKeyClass.NameContainer
        if item == "NamedClass": return self.NamedKeyClass
        raise AttributeError

    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def text(self, string, delay = None):
        delay = self.default_delay if delay is None else delay
        func = self.text.target
        if func is NotImplemented: func = self.tap
        for character in string:
            func(character)
            if delay: time.sleep(delay/1000)

    @adaptionmethod("rls", require=True)
    def _rls(self, keyname):
        #print("_rls", keyname)
        return self._rls.target(self._keyname_dict.apply(keyname))

    @adaptionmethod("press", require=True)
    def _press(self, keyname):
        #print("_press", keyname)
        return self._press.target(self._keyname_dict.apply(keyname))

    @adaptionmethod(require=True)
    def keynames(self):
        return self.keynames.target
    @keynames.target_modifier
    def _apply_update(self, target):
        self._update_keyname_dict(target)
        return target
    
    def _translation_dict(self):
        try:
            return self.keynames.target_space.translation_dic
        except AttributeError:
            return
    
    @property
    def _keyname_dict(self):
        return self.keynames.target_space.keyname_dict
    
    def _update_keyname_dict(self, keynames_target=None):
        if keynames_target is None: keynames_target = self.keynames.target
        keyname_dic = self.NamedKeyClass.StandardizingDict(keynames_target)
        trans_dic = self._translation_dict()
        if trans_dic:
            dic2 = self.NamedKeyClass.StandardizingDict()
            for key,val in trans_dic.items():
                if key != val: dic2[key] = keyname_dic.apply(val)
            keyname_dic.update(dic2)
        self.keynames.target_space.keyname_dict = keyname_dic
    
    
    def add_key_translation(self, dic):
        self.keynames.target_space.translation_dic = dic
        self._update_keyname_dict()
 
