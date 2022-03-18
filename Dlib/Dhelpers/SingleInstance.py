import __main__, os, signal

path = os.path

class SingleInstance:
    
    def __init__(self):
        script_file = __main__.__file__
        script_folder = path.dirname(script_file)
        self.file = path.join(script_folder,".active_processes")
        with open(self.file,"a") as f:
            f.write(str(os.getpid())+"\n")
            
    def kill_other(self):
        pids=[]
        with open(self.file,"r") as f:
            for line in f.readlines():
                pid = int(line)
                if pid == os.getpid(): continue
                pids.append(pid)
        for pid in pids:
            try:
                os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            else:
                print("Killed old process with pid",pid)
        with open(self.file,"w") as f:
            f.write(str(os.getpid())+"\n")