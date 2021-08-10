import os, warnings

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
    @classmethod
    def getfunc(cls, func):
        if hasattr(func, 'func'):
            if isinstance(func.func, cls):
                return func.func.func
            elif isinstance(func, cls):
                return func.func
        assert callable(func)
        return func
    def __init__(self, func):
        self.func = self.getfunc(func)
    def __call__(self, *args, **kwargs):
        return bool(self.func(*args, **kwargs))
    def negate(self):
        return self.__class__(
                func=lambda *args, **kwargs: not self.func(*args, **kwargs))
    def __and__(self, other):
        otherfunc = self.getfunc(other)
        return self.__class__(func=lambda *args, **kwargs: bool(
                self.func(*args, **kwargs)) & bool(otherfunc(*args, **kwargs)))
    def __or__(self, other):
        otherfunc = self.getfunc(other)
        return self.__class__(func=lambda *args, **kwargs: bool(
                self.func(*args, **kwargs)) | bool(otherfunc(*args, **kwargs)))



class Filelist(BooleanFunction):
    creator = None
    def __init__(self, name=None, func=None, add=True, **kwargs):
        self.name = name
        if name is None: add = False
        if not func:
            if not kwargs: raise ValueError
            func = lambda obj: self.creator.default_selection_func(obj,
                    **kwargs)
        BooleanFunction.__init__(self, func)
        if add: self.creator.add(name, func)


class FileSelector:
    editor_class = None
    file_extension = ""
    file_start = ""
    
    def __init__(self, basepath, destpath=None):
        filelist_cls = type(f"Filelist", (Filelist,), {})
        filelist_cls.creator = self
        self.Filelist = filelist_cls
        self.basepath = basepath
        self.destpath = destpath if destpath else os.path.join(basepath,
                "__playlists")  #
        os.makedirs(self.destpath, exist_ok=True)
        self.playlists = {}
    
    def add(self, name, func=None, **kwargs):
        self.playlists[name] = (func, kwargs)
    
    @staticmethod
    def default_selection_func(obj, kwargs):
        raise NotImplementedError
    
    def find_files(self, *names, suppress_error=False, warn=True):
        for dirpath, _, files in os.walk(self.basepath):
            for file in files:
                ext = os.path.splitext(file)[-1]
                allowed = self.editor_class.allowed_file_extensions
                if ext not in allowed: continue
                file = os.path.realpath(os.path.join(dirpath, file))
                try:
                    with self.editor_class(file) as obj:
                        for name in names:
                            func, kwargs = self.playlists[name]
                            if func:
                                if func(obj): yield name, file
                            elif self.default_selection_func(obj, **kwargs):
                                yield name, file
                except Exception as e:
                    if not suppress_error: raise
                    if warn:
                        warnings.warn(f"\nerror with file {file}:\n{e}")
                        print()
    
    def assemble_lists(self, *names, **kwargs):
        if not names: names = self.playlists.keys()
        lists = {name: [] for name in names}
        for name, file in self.find_files(*names, **kwargs):
            # print(name,file)
            lists[name].append(file)
        return lists
    
    
    def write_paths(self, *names, **kwargs):
        lists = self.assemble_lists(*names, **kwargs)
        print("Creating playlists:")
        for name, list in lists.items():
            fpath = os.path.join(self.destpath, name + self.file_extension)
            with open(fpath, "w") as new:
                new.write(self.file_start + "\n")
                for file in list: new.write(file + "\n")
            print(f"{name}: {len(list)} songs in {fpath}")