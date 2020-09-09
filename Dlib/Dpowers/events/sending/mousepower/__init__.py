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
from ... import adaptionmethod, hotkeys, MouseMoveEvent, NamedButton
from ..event_sender import AdaptivePressReleaseSender
from time import sleep

class MouseAdaptor(AdaptivePressReleaseSender):
    
    # inherits adaptionmethods _press and _rls
    
    @property
    def NamedClass(self):
        return self.NamedButtonClass
    @NamedClass.setter
    def NamedClass(self, val):
        if not issubclass(val, NamedButton): raise TypeError
        self.NamedButtonClass = val
        self._update_stand_dicts()
    
    @property
    def button(self):
        return self.NamedButtonClass.NameContainer
    
    @adaptionmethod
    def pos(self):
        return self.pos.target()
    
    @adaptionmethod
    def move(self, dx, dy):
        return self.move.target_with_args()
    
    @adaptionmethod
    def moveto(self, x=None, y=None):
        if x is None: x = self.pos()[0]
        if y is None: y = self.pos()[1]
        return self.moveto.target(x, y)
    

    def press(self, *buttons, x=None, y=None, delay=None, pause_hotkeys=True):
        if x or y: self.moveto(x, y)
        return super().press(*buttons,delay=delay)

    
    def rls(self, *buttons, x=None, y=None, delay=None, pause_hotkeys=True):
        if x or y: self.moveto(x, y)
        return super().press(*buttons, delay=delay)


    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def scroll(self, vertical, horizontal=0):
        # it is necessary to explicitely pass the parameters here, because
        # hotkeys.add_pause_option is adding a parameter which confuses
        # call_target
        return self.scroll.target(vertical, horizontal)

    @hotkeys.add_pause_option(True)
    def click(self, button=1, count=1, x=None, y=None, duration=0.05):
        if x or y: self.moveto(x, y)
        stan_name = self._press.standardizing_dict.get(button, button)
        for _ in range(count):
            self._press.target(stan_name)
            sleep(duration)
            self._rls.target(stan_name)
    
    def rclick(self, *args, **kwargs):
        return self.click("right", *args, **kwargs)
    
    def mclick(self, *args, **kwargs):
        return self.click("middle", *args, **kwargs)
    
    def click2(self, button=1, *args, **kwargs):
        return self.click(button, 2, *args, **kwargs)
    
    def click3(self, button=1, *args, **kwargs):
        return self.click(button, 3, *args, **kwargs)
    
    def clickrel(self, button=1, count=1, dx=0, dy=0, **kwargs):
        self.move(dx, dy)
        self.click(button, count, **kwargs)
    
    @hotkeys.add_pause_option(True)
    def drag(self, dx, dy, button=1, x=None, y=None):
        self.press(button, x=x, y=y)
        self.move(dx, dy)
        self.rls(button)
    
    @hotkeys.add_pause_option(True)
    def dragto(self, x, y, button=1, x0=None, y0=None):
        self.press(button, x=x0, y=y0)
        self.moveto(x, y)
        self.rls(button)
    
    
    def _send_event(self, event, delay=None, reverse_press=False,
            autorelease=False):
        try:
            return super()._send_event(event, delay, reverse_press,
                autorelease)
        except TypeError:
            if isinstance(event, MouseMoveEvent):
                if event.relative:
                    self.move(event.x, event.y)
                else:
                    self.moveto(event.x, event.y)
            else:
                raise TypeError