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
    uinput = tester.import_module("evdev_prepared.uinput",pkg="evdev_prepared")

global_uinput = uinput.global_uinput

from evdev.ecodes import KEY, EV_KEY

names = {}

def iterator(dic):
    for a, b in dic.items():
        if isinstance(b, (tuple, list)):
            for c in b: yield a,c
        else:
            yield a, b

for integer, name in iterator(KEY):
    n = name[4:]
    if len(n)==1 and n.isalpha(): n=n.lower()
    names[n] = integer
    
global_uinput.start()

def press(keynumber):
    global_uinput.write(EV_KEY, keynumber, 1)

def rls(keynumber):
    global_uinput.write(EV_KEY, keynumber, 0)