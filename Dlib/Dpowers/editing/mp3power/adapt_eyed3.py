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
import eyed3.mp3


obj_class = eyed3.mp3.Mp3AudioFile
eyed3.log.setLevel("ERROR")

def load(file, **kwargs):
    return eyed3.load(file)

def save(backend_obj, destination):
    backend_obj.tag.save(destination)


def genre(backend_obj, val):
    t = backend_obj.tag
    if val is None:
        if t is None: return ""
        g = backend_obj.tag.genre
        if g is None: return ""
        return g.name
    backend_obj.tag.genre = val
    
def close(backend_obj):
    pass