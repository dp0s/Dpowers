#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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
from ... import DependencyManager, launch

with DependencyManager(__name__) as manager:
    pyttsx3 = manager.import_module("pyttsx3")

engine = pyttsx3.init()


def call(text):
    engine.say(text)
    engine.runAndWait()
    
def set_volume(val):
    if val is None:
        return engine.getProperty('volume')
    engine.setProperty('volume', val)