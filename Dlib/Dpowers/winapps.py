import types
from Dhelpers.launcher import launch, Application
from . import Win


class WindowApplication(Application):
    
    Win = Win
    mouse=NotImplemented
    
    def __init__(self, command=NotImplemented, check_installed=False):
        super().__init__(command, check_installed)
        self._winsearch = 0
        self.last_found = None


    @property
    def winsearch(self):
        if self.used_inst: return self.used_inst.winsearch
        return self._winsearch
        
        
    def add_winprops(self, *winargs,**winkwargs):
        if self.used_inst:
            self._winsearch = self.used_inst.winsearch
            self.used_inst = None
        if winargs and isinstance(winargs[0], (Application, self.Win.Search)):
                assert not winkwargs
                for obj in winargs:
                    if isinstance(obj,Application): obj = obj.winsearch
                    self._winsearch += obj
                return
        if "visible" not in winkwargs: winkwargs["visible"] = True
        self._winsearch += self.Win.Search(*winargs,**winkwargs)
    
    def __getattr__(self, item):
        winobj = self.last_found.winsearch_object if self.last_found else \
            self.winsearch
        if winobj is not 0:
            obj = getattr(winobj, item)
            if isinstance(obj,(types.FunctionType, types.MethodType)):
                return obj
            raise AttributeError
        
    def find(self):
        found_win = self.winsearch.find()
        if len(found_win) == 1: self.last_found = found_win
        return found_win
        
    find_win = find
    
    def startwait(self, *args, start=True, timeout=10,**kwargs):
        return self.wait(*args,start=start,timeout=timeout, **kwargs)
        
    def wait(self, *args,start=False,timeout=10,**kwargs):
        self._found = self.find()
        if start:
            cmd = start if isinstance(start, str) else self.command
            launch(cmd,*args, **kwargs)
        # capturing the pid of this process doesnt help, as windows might
        # share same pid of the one that was first opened
        new_win = self._found.wait_num_change(+1, timeout=timeout)
        if not new_win: return
        new_win.activate()
        self.last_found = new_win
        return new_win
        
    
    def center_mouse(self):
        geom = self.geometry()
        self.mouse.moveto(geom[0]+geom[2]/2, geom[1]+geom[3]/4)
        
        
class EditorApp(WindowApplication):
    
    def jump_to_line(self, file, line=None):
        args = []
        if line: args += ["--line", str(line)]
        args += [str(file)]
        launch(self.command, *args)
        self.wait_exist_activate()


pythoneditor = EditorApp()
