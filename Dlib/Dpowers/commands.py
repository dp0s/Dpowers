import types
from . import Win
from Dhelpers.launcher import launch

class CustomCommand:
    
    Win = Win
    
    def __init__(self, base=None, check_installed=False):
        self.base = base
        self.winsearch = None
        if base and check_installed: pass #tba
        
    def set_winprops(self, *winargs,**winkwargs):
        if winargs:
            if isinstance(winargs[0], (CustomCommand, Win.Search)):
                assert not winkwargs
                self.winsearch = 0
                for obj in winargs:
                    if isinstance(obj,CustomCommand): obj = obj.winsearch
                    self.winsearch += obj
                return
        self.winsearch = self.Win.Search(*winargs,**winkwargs)
    
    def find_win(self):
        return self.winsearch.find()
    
    def matches_win(self, *winargs,**winkwargs):
        self.winsearch.match_win(*winargs,**winkwargs)
    
    def add_method(self, func):
        method = types.MethodType(func, self)
        setattr(self, func.__name__, method)
        
        
class Editor(CustomCommand):
    
    def jump_to_line(self, file, line=None):
        add = " --line " + str(line) if line else ""
        launch(self.base + add + f' "{file}"')


pythoneditor = Editor()