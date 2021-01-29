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
import os, warnings
from . import mp3tag


class FileSelector:
    editor_class = None
    
    def __init__(self, basepath, destpath=None):
        self.basepath = basepath
        self.destpath = destpath if destpath else os.path.join(basepath,
                "__playlists")#
        os.makedirs(self.destpath, exist_ok=True)
        self.playlists = {}
    
    def add(self, name, func=None, **kwargs):
        self.playlists[name] = (func, kwargs)
    
    def playlist(self, name):
        def decorator(func):
            self.add(name, func=func)
            return func
        return decorator
    
    __call__ = playlist
    
    @staticmethod
    def default_selection_func(obj, kwargs):
        raise NotImplementedError
    
    def find_files(self, *names, suppress_error=False, warn=True):
        for dirpath, _, files in os.walk(self.basepath):
            for file in files:
                ext = os.path.splitext(file)[-1]
                allowed = self.editor_class.allowed_file_extensions
                if ext not in allowed: continue
                file = os.path.realpath(os.path.join(dirpath,file))
                try:
                    with self.editor_class(file) as obj:
                        for name in names:
                            func, kwargs = self.playlists[name]
                            if func:
                                if func(obj): yield name,file
                            elif self.default_selection_func(obj, **kwargs):
                                yield name,file
                except Exception as e:
                    if not suppress_error: raise
                    if warn:
                        warnings.warn(f"\nerror with file {file}:\n{e}")
                        print()
                            
    def assemble_lists(self, *names, **kwargs):
        if not names: names = self.playlists.keys()
        lists = {name:[] for name in names}
        for name,file in self.find_files(*names, **kwargs):
            #print(name,file)
            lists[name].append(file)
        return lists
        
    
    def write_paths(self, *names, **kwargs):
        lists = self.assemble_lists(*names, **kwargs)
        print("Creating playlists:")
        for name, list in lists.items():
            fpath = os.path.join(self.destpath,name+".m3u")
            with open(fpath,"w") as new:
                for file in list: new.write(file+"\n")
            print(f"{name}: {len(list)} songs in {fpath}")



class playlist_creator(FileSelector):
    
    editor_class = mp3tag
    
    @staticmethod
    def default_selection_func(obj,genre=None):
        return genre in obj.genre