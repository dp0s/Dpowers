#
#
# Copyright (c) 2020-2023 DPS, dps@my.mail.de
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
import os, warnings, sys, random, functools
from collections import defaultdict
from contextlib import contextmanager

p = os.path



class FileIterator:
    
    def __init__(self, *filepaths):
        self.given_paths = filepaths
    
    def generate_paths(self):
        for path in self.given_paths:
            path = path.strip()
            if p.isdir(path): raise ValueError
            if "\n" in path:
                for path2 in path.split("\n"):
                    yield path2.strip()
            else:
                yield path
    
    def __call__(self):
        for path in self.generate_paths():
            yield path, self.filepath_split(path)
    
    @staticmethod
    def filepath_split(file):
        folder, filename = p.split(file)
        name, ext = p.splitext(filename)
        if folder == "": folder = os.getcwd()
        return folder, name, ext




class BooleanFunction:
    
    _cache_lvl = False
    _last_cache_lvl = 0
    
    @classmethod
    def getfunc(cls, func):
        if isinstance(func, cls): func = func._func
        assert callable(func)
        return func

    def __init__(self,name=None, func=None):
        self.name = name
        self._func = self.getfunc(func)
        self.cached_val=None
        
    def func(self, *args, **kwargs):
        cls_cache_lvl = self.__class__._cache_lvl
        if cls_cache_lvl is False: return bool(self._func(*args,**kwargs))
        if self.cached_val is None or self._cache_lvl <= cls_cache_lvl:
            self.cached_val = bool(self._func(*args,**kwargs))
            self._cache_lvl = cls_cache_lvl + 1
        return self.cached_val
    __call__ = func
    
    
    @classmethod
    @contextmanager
    def use_cache(cls):
        # Usage: see FilelistCreator.find_files method below
        cls._cache_lvl = cls._last_cache_lvl + 1
        try:
            yield cls._forget_cached_vals
        finally:
            cls._last_cache_lvl = cls._cache_lvl
            cls._cache_lvl = False
    
    @classmethod
    def _forget_cached_vals(cls):
        cls._cache_lvl += 1
        
    
    
    def negate(self):
        return self.__class__(
                func=lambda *args, **kwargs: not self.func(*args, **kwargs))
    def __and__(self, other):
        assert callable(other)
        return self.__class__(func=lambda *args, **kwargs:
                self.func(*args, **kwargs) & bool(other(*args, **kwargs)))
    def __or__(self, other):
        assert callable(other)
        return self.__class__(func=lambda *args, **kwargs:  self.func(*args,
                **kwargs) | bool(other(*args, **kwargs)))
    
    
    



class Filelist(BooleanFunction):
    creator = None
    def __init__(self, name=None, func=None, add=True, **kwargs):
        self.last_found_paths=[]
        if name is None: add = False
        if not func:
            if not kwargs: raise ValueError
            func = lambda obj: self.creator.default_selection_func(obj,
                    **kwargs)
        BooleanFunction.__init__(self, name, func)
        if add: self.creator.add_inst(self)


class FilelistCreator:
    editor_class = None
    filelist_extension = ""
    file_start = ""
    allowed_file_extensions = "inherit"
    Filelist = None
    
    def __init__(self, basepath=None, destpath=None):
        filelist_cls = type(f"Filelist", (Filelist,), {})
        filelist_cls.creator = self
        self.Filelist = filelist_cls
        self.basepath = basepath
        if not destpath and basepath:
            destpath = os.path.join(basepath, "__playlists")
        if destpath: os.makedirs(destpath, exist_ok=True)
        self.destpath = destpath
        self.filelist_objs = {}
        self.file_paths = {}
        self.imported_lists = None
    
    def add(self, name, func=None, **kwargs):
        new_inst = self.Filelist(name,func=func, **kwargs)
        self.add_inst(new_inst)
    
    def add_inst(self, filelist_inst):
        assert isinstance(filelist_inst, self.Filelist)
        name = filelist_inst.name
        self.filelist_objs[name] = filelist_inst
        self.file_paths[name] = filelist_inst.last_found_paths  #shortcut

    @staticmethod
    def default_selection_func(obj, case_sensitive=False, exact_match=False,
            **kwargs):
        for attr_name, value in kwargs.items():
            string = str(getattr(obj, attr_name))
            value = str(value)
            if not case_sensitive:
                value = value.lower()
                string = string.lower()
            if exact_match:
                if value != string: return False
            else:
                if value not in string: return False
        return True
    
    def find_files(self, *names, suppress_error=True, warn=True):
        for dirpath, _, files in os.walk(self.basepath):
            allowed_ext = self.allowed_file_extensions
            if allowed_ext == "inherit":
                allowed_ext=self.editor_class.allowed_file_extensions
            with self.Filelist.use_cache() as reset_cache:
                for file in files:
                    ext = os.path.splitext(file)[-1]
                    if ext not in allowed_ext: continue
                    file = os.path.realpath(os.path.join(dirpath, file))
                    try:
                        with self.editor_class(file) as obj:
                            for name in names:
                                filelist_obj = self.filelist_objs[name]
                                if filelist_obj(obj): yield name, file
                    except Exception as e:
                        if not suppress_error: raise
                        if warn:
                            warnings.warn(f"\nerror with file {file}:\n{e}")
                            print()
                    finally:
                        reset_cache()
    
    def assemble_lists(self, *names, **kwargs):
        if not names: names = self.file_paths.keys()
        for name in names:
            self.file_paths[name].clear()
        for name, file in self.find_files(*names, **kwargs):
            # print(name,file)
            self.file_paths[name].append(file)
    
    
    def write_paths(self, *names, assemble=True, **kwargs):
        if assemble: self.assemble_lists(*names, **kwargs)
        print("Creating playlists:")
        for name, file_path_list in self.file_paths.items():
            self._write_filelist(name,file_path_list, self.destpath)
            
            
    def _write_filelist(self, name, file_path_list, path):
        fpath = os.path.join(path, name + self.filelist_extension)
        with open(fpath, "w") as new:
            new.write(self.file_start + "\n")
            for file in file_path_list: new.write(file + "\n")
        print(f"{name}: {len(file_path_list)} songs in {fpath}")



    def import_lists(self, destpath=None, add_ext=()):
        if destpath is None: destpath = self.destpath
        allowed_ext = (self.filelist_extension,) + (add_ext,)
        self.imported_lists = defaultdict(list)
        for file in os.listdir(destpath):
            name, ext = os.path.splitext(file)
            if ext not in allowed_ext: continue
            with open(os.path.join(destpath,file), "r") as opened:
                for line in opened.readlines():
                    self.imported_lists[name].append(line.strip())
        return self.imported_lists
    
    def create_combination(self, *file_list_names, insert=None,
            from_imported=False):
        lists = self.imported_lists if from_imported else self.file_paths
        for name in file_list_names:
            if isinstance(name,self.Filelist): name=name.name
            l = lists[name]
            yield random.choice(l)
            if insert: yield insert
    
    @functools.wraps(create_combination)
    def write_combination(self, *args, **kwargs):
        filelist = tuple(self.create_combination(*args,**kwargs))
        comb_path=os.path.join(self.destpath, "combinations")
        os.makedirs(comb_path, exist_ok=True)
        self._write_filelist("test_combination", filelist, comb_path)