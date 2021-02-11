from ..launcher import launch

class platform:
    
    attrs = ["termux", "linux", "windows"]
    
    def __init__(self):
        for attr in self.attrs: setattr(self,attr,None)
    
    def update(self):
        for attr in self.attrs:
            setattr(self,attr,getattr(self,f"check_{attr}")())
            
    
    @staticmethod
    def check_linux():
        pass
    
    
    @staticmethod
    def check_termux():
        return bool(launch.get("command -v termux-setup-storage",check=False))
    
    @staticmethod
    def check_windows():
        pass