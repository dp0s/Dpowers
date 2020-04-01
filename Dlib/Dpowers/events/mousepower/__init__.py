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
from .. import Adaptor, adaptionmethod, hotkeys, Buttonevent, MouseMoveEvent
from ..event_sender import EventSenderBase

class MouseAdaptor(Adaptor, EventSenderBase):
    
    # def set_options(self, *options):
    #     if not options: options = ("NamedButton",)
    #     if len(options) != 1: raise SyntaxError
    #     self.NamedButtonClass = NamedKeyButton.subclass_from_name(options[0])
    #     self.button = self.NamedButtonClass.NameContainer()
    
    def __getattr__(self, item):
        # this allows mouse.button to dynamically reference the current
        # NamedButtonClass even if it is changed
        if item == "button": return self.NamedButtonClass.NameContainer
        if item == "NamedClass": return self.NamedButtonClass
        raise AttributeError
    
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
    
    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def click(self, button=1, count=1, x=None, y=None):
        if x or y: self.moveto(x, y)
        return self.click.target(self._keyname_dict.apply(button), count)

    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def press(self, button=1, x=None, y=None):
        if x or y: self.moveto(x, y)
        return self.press.target(self._keyname_dict.apply(button))

    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def rls(self, button=1, x=None, y=None):
        if x or y: self.moveto(x, y)
        return self.rls.target(self._keyname_dict.apply(button))

    @adaptionmethod("keynames")
    def _keynames(self):
        return self._keynames.target
    @_keynames.target_modifier
    def _standardize(self, target):
        self._keyname_dict = self.NamedButtonClass.StandardizingDict(target)
        return target


    @adaptionmethod
    @hotkeys.add_pause_option(True)
    def scroll(self, vertical, horizontal=0):
        # it is necessary to explicitely pass the parameters here, because
        # hotkeys.add_pause_option is adding a parameter which confuses
        # call_target
        return self.scroll.target(vertical, horizontal)
    
    def rclick(self, x=None, y=None, pause_hotkeys=True):
        return self.click("right", 1, x, y, pause_hotkeys=pause_hotkeys)
    
    def mclick(self, x=None, y=None, pause_hotkeys=True):
        return self.click("middle", 1, x, y, pause_hotkeys=pause_hotkeys)
    
    def click2(self, button="left", x=None, y=None, pause_hotkeys=True):
        return self.click(button, 2, x, y, pause_hotkeys=pause_hotkeys)
    
    def click3(self, button="left", x=None, y=None, pause_hotkeys=True):
        return self.click(button, 3, x, y, pause_hotkeys=pause_hotkeys)
    
    @hotkeys.add_pause_option(True)
    def clickrel(self, button=1, count=1, dx=0, dy=0):
        self.move(dx, dy)
        self.click(button, count)
    
    @hotkeys.add_pause_option(True)
    def drag(self, x=0, y=0, button=1):
        self.press(button)
        self.move(x, y)
        self.rls(button)
    
    @hotkeys.add_pause_option(True)
    def dragto(self, x=None, y=None, button=1):
        self.press(button)
        self.moveto(x, y)
        self.rls(button)

    def _send_event(self, event, reverse=False, autorelease=False):
        if isinstance(event, Buttonevent):
            if event.press and not reverse or not event.press and reverse:
                self.press(event.name, x=event.x, y=event.y)
                if autorelease: self.rls(event.name)
            else:
                self.rls(event.name, x=event.x, y=event.y)
        elif isinstance(event, MouseMoveEvent):
            if event.relative:
                self.move(event.x, event.y)
            else:
                self.moveto(event.x, event.y)
        else:
            raise TypeError