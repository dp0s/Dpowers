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
from .ressource_classes import *
from .imagepower import *
from .mp3power import *



class Image(ImageBase):
    adaptor = ImageAdaptor(_primary_name="Image.adaptor")
    
    
class mp3tag(mp3tagBase):
    adaptor = mp3tagAdaptor(_primary_name="mp3tag.adaptor")



from Dhelpers.file_iteration import FileSelector


class playlist_creator(FileSelector):
    editor_class = mp3tag
    file_extension = ".m3u"
    file_start = "#EXTM3U"