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
from contextlib import redirect_stdout


class Image(ImageBase):
    adaptor = ImageAdaptor(_primary_name="Image.adaptor")
    
    
class mp3tag(mp3tagBase):
    adaptor = mp3tagAdaptor(_primary_name="mp3tag.adaptor")


from .FilelistCreator import FilelistCreator


class PlaylistCreator(FilelistCreator):
    editor_class = mp3tag
    filelist_extension = ".m3u"
    mytag = ""
    #file_start = "#EXTM3U"
    
    @classmethod
    def adapt(cls, *args, **kwargs):
        return cls.editor_class.adapt(*args,**kwargs)
    
    def print_mp3_tags(self, name, header=True):
        #os.makedirs(dest_folder)
        if isinstance(name, self.Filelist): name = name.name
        l = self.imported_lists[name]
        self._create_print(l, name, header=header)
        
    def print_tags_to_file(self, l, destpath, playlist_name="", header=True,
            txt_name=None):
        if txt_name is None: txt_name = playlist_name
        with open(os.path.join(destpath, txt_name + ".txt"), "w") as f:
            with redirect_stdout(f):
                self._create_print(l, playlist_name, header)
        
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
    
    def copy_files(self, filelist, dest_folder, numerate=False,
            clear_tags=True, include_txt=False):
        if isinstance(filelist, self.Filelist): filelist = filelist.name
        created_files = super().copy_files(filelist, dest_folder, numerate)
        if clear_tags and self.mytag:
            print("Removing custom tags.")
            for file in os.listdir(dest_folder):
                if not self._file_allowed(file): continue
                with self.editor_class(path.join(dest_folder, file)) as obj:
                    obj.remove_tag_from_genre(self.mytag)
        if include_txt:
            self.print_tags_to_file(created_files,dest_folder,
                    filelist, txt_name="0_readme")
    