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

keyboard = pynput.keyboard.Controller()
DefinedKeys = pynput.keyboard.Key

text = keyboard.type

press = keyboard.press
rls = keyboard.release

names = {key.name: key for key in DefinedKeys}  # these names are defined
names["minus"]="-"
# in pynput
# alphanumeric keys are automatically supported via they standard names


# # support for numpad keys:
# numpad_to_normal = {'p_delete': 'Delete', 'p_home': 'Home', 'p_down':
# 'down', 'p_next':
# 'PageDown', 'p_add': 'plus',
#                     'p_right': 'right', 'p_page_up': 'PageUp',
# 'p_page_down': 'PageDown',
# 'p_multiply': 'multiply',
#                     'p_end': 'End', 'p_up': 'up', 'p_insert': 'insert',
# 'p_divide': 'slash',
#  'p_left': 'left',
#                     'p_subtract': 'minus'}
# keynames.update(numpad_to_normal)
# DOESNT WORK YET