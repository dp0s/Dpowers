import types
from Dhelpers.launcher import launch, Application
from . import Win




class WindowApplication(Application):
    
    Win = Win
    
    def __init__(self, command=NotImplemented, check_installed=False):
        super().__init__(command, check_installed)
        self._winsearch = 0


    @property
    def winsearch(self):
        if self.used_inst: return self.used_inst.winsearch
        return self._winsearch
        
        
    def add_winprops(self, *winargs,**winkwargs):
        if self.used_inst:
            self._winsearch = self.used_inst.winsearch
            self.used_inst = None
        if winargs:
            if isinstance(winargs[0], (Application, self.Win.Search)):
                assert not winkwargs
                for obj in winargs:
                    if isinstance(obj,Application): obj = obj.winsearch
                    self._winsearch += obj
                return
        self._winsearch += self.Win.Search(*winargs,**winkwargs)
    
    def __getattr__(self, item):
        winsearch = self.winsearch
        if winsearch is not 0:
            obj = getattr(winsearch, item)
            if isinstance(obj,(types.FunctionType, types.MethodType)):
                return obj
            raise AttributeError
        
    def find_win(self):
        return self.find()
    
    def startwait(self, *options):
        launch(self.command,*options)
        self.wait_active()
   
        
        
class EditorApp(WindowApplication):
    
    def jump_to_line(self, file, line=None):
        add = " --line " + str(line) if line else ""
        launch(self.command + add + f' "{file}"')


pythoneditor = EditorApp()