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
from .ressource_classes import *
from .imagepower import *
from .mp3power import *
from datetime import datetime


class Image(ImageBase):
    adaptor = ImageAdaptor(_primary_name="Image.adaptor")
    
    
class mp3tag(mp3tagBase):
    adaptor = mp3tagAdaptor(_primary_name="mp3tag.adaptor")



from Dhelpers.file_iteration import FilelistCreator


class PlaylistCreator(FilelistCreator):
    editor_class = mp3tag
    filelist_extension = ".m3u"
    #file_start = "#EXTM3U"
    
    @classmethod
    def adapt(cls, *args, **kwargs):
        return cls.editor_class.adapt(*args,**kwargs)
    
    def print_mp3_tags(self, name, header=True, dest_folder=None):
        #os.makedirs(dest_folder)
        if isinstance(name, self.Filelist): name = name.name
        l = self.imported_lists[name]
        self._create_print(l, name, header=header)
        
    def _create_print(self, l, name="", header=True):
        if header:
            print("-------------------------------------------------")
            print(f"Playlist '{name}' containing {len(l)} entries")
            print("-------------------------------------------------")
            print("Date: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print()
            print("Title / Artist / Album / 'filename'")
            print()
        for file in l:
            with self.editor_class(file) as obj:
                print(obj.title," / ",obj.artist, " / ",obj.album, " / '",
                        os.path.basename(file),"'", sep="")