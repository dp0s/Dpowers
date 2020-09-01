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
from evdev_prepared.uinput import global_uinput

from evdev.ecodes import BTN, EV_KEY

names = {}

def iterator(dic):
    for a, b in dic.items():
        if isinstance(b, (tuple,list)):
            for c in b: yield a,c
        else:
            yield a,b
    
for integer, name in iterator(BTN):
    n = name[4:]
    names[n] = integer
    
global_uinput.start()

def press(number):
    global_uinput.write(EV_KEY, number, 1)

def rls(number):
    global_uinput.write(EV_KEY, number, 0)