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

with DependencyManager(__name__) as tester:
    pynput = tester.import_module("pynput", pkg="pynput")

mouse = pynput.mouse.Controller()

def pos():
    return mouse.position

move=mouse.move


def moveto(x,y):
    mouse.position = (x,y)


names = {i : pynput.mouse.Button(i) for i in range(1,31)}
#this is necessary because somehow pynput send button.value instead of button

#click=mouse.click
press=mouse.press
rls=mouse.release

def scroll(vertical,horizontal):
    return mouse.scroll(horizontal,vertical)