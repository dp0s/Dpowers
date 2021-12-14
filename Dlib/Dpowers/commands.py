import types
from . import Win
from Dhelpers.launcher import launch

class CustomCommand:
    
    Win = Win
    
    def __init__(self, base=NotImplemented, check_installed=False):
        self.base = base
        self.winsearch = None
        if base and check_installed: pass #tba
        
    @property
    def base(self):
        if self._base is NotImplemented:
            raise NotImplementedError(f"No base command defined for {self}.")
            
    @base.setter
    def base(self, val):
        self._base = val
        
        
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
    
    def compare_win(self, *winargs,**winkwargs):
        self.winsearch.compare_win(*winargs,**winkwargs)
    
    def add_method(self, func):
        method = types.MethodType(func, self)
        setattr(self, func.__name__, method)
        
        
class Editor(CustomCommand):
    
    def jump_to_line(self, file, line=None):
        add = " --line " + str(line) if line else ""
        launch(self.base + add + f' "{file}"')


pythoneditor = Editor()