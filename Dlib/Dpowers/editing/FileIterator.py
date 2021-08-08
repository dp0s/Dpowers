import os

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