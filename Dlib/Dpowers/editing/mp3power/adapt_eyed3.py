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
from ... import DependencyManager

with DependencyManager(__name__) as tester:
    mp3 = tester.import_module("eyed3.mp3", pkg="eyed3")

import eyed3 #this is already imported and will just place the name here again

obj_class = eyed3.id3.tag.Tag
eyed3.log.setLevel("ERROR")

def load(file, **kwargs):
    file = eyed3.load(file)
    return file.tag
    

def save(backend_obj, destination):
    backend_obj.save(destination)

def close(backend_obj):
    pass

def genre(backend_obj, val):
    if val is None:
        g = backend_obj.genre
        if g is None: return ""
        return g.name
    backend_obj.genre = val
    
