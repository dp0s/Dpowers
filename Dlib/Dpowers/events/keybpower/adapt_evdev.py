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
from evdev_prepared.uinput import global_uinput

from evdev.ecodes import KEY, EV_KEY

keynames = {}
for a, b in KEY.items():
    if isinstance(b, list): b = b[0]
    b = b[4:].lower()
    keynames[b] = a
    
global_uinput.start()

def press(keynumber):
    global_uinput.write(EV_KEY, keynumber, 1)

def rls(keynumber):
    global_uinput.write(EV_KEY, keynumber, 0)