#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
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
from Dhelpers.adaptor import DependencyManager

with DependencyManager(__name__) as manager:
    pynput = manager.import_module("pynput")

from .baseclasses import (InputEventHandler, KeyhookBase, ButtonhookBase,
    CursorhookBase)

keyboard = pynput.keyboard.Controller()


class PynputHandler(InputEventHandler):
    
    
    collector = None
    capturer = None
    
    def start_collecting(self):
        self.collector = self.get_collector()
        self.collector.start()
    def stop_collecting(self):
        self.collector.stop()
        
    def start_capturing(self):
        self.capturer = self.get_capturer()
        self.capturer.start()
    def stop_capturing(self):
        self.capturer.stop()
        

    def get_collector(self):
        raise NotImplementedError
    

    def get_capturer(self):
        raise NotImplementedError


class PynputKeyHandler(PynputHandler):
    
    
    def get_collector(self):
        return pynput.keyboard.Listener(on_press=self.key_down_event,
                on_release=self.key_up_event)
    
    def key_down_event(self, event):
        name = self._get_key_info(event)
        self.queue_event(name, press=True)
    
    def key_up_event(self, event):
        name = self._get_key_info(event)
        self.queue_event(name, press=False)

    @staticmethod
    def _get_key_info(key_object):
        if type(key_object) is pynput.keyboard.Key:
            return key_object.name#, key_object.value.vk
        elif type(key_object) is pynput.keyboard.KeyCode:
            return key_object.char#, key_object.vk
        else:
            raise TypeError

    @staticmethod
    def get_capturer():
        return pynput.keyboard.Listener(suppress=True)


class PynputMouseHandler(PynputHandler):
    def get_collector(self):
        return pynput.mouse.Listener(on_click=self.click_event,
                on_scroll=self.scroll_event)

    def click_event(self, x, y, button, pressed):
        self.queue_event(button.value, press=pressed, x=x, y=y)
    
    def scroll_event(self, x, y, dx, dy):
        d = dx, dy
        if d == (0, 1):
            button = 4  # "scroll_up"
        elif d == (0, -1):
            button = 5  # "scroll_down"
        elif d == (1, 0):
            button = 7  # "scroll_right"
        elif d == (-1, 0):
            button = 6  # "scroll_left"
        else:
            raise ValueError
        self.queue_event(button, press=None, x=x, y=y)

    @staticmethod
    def get_capturer():
        return pynput.mouse.Listener(suppress=True)



class PynputCursorHandler(PynputHandler):
    
    capture_allowed = False
    
    def get_collector(self):
        return pynput.mouse.Listener(on_move=self.queue_event)
    



class Keyhook(KeyhookBase):
    handler = PynputKeyHandler()

class Buttonhook(ButtonhookBase):
    handler = PynputMouseHandler()

class Cursorhook(CursorhookBase):
    handler = PynputCursorHandler()