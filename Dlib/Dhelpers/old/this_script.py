#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
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
import os, __main__, time
from ..external import ExternalDict
from ..launcher import terminate_process, launch
from ..psutil_fix import psutil

path = os.path


def check_process_exists(pid, ctime):
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        pass
    else:
        if process.create_time() == ctime:
            return process
    return False



class ProcessCheckerExternalDict(ExternalDict):
    
        
    def load_profile(self, profile=None):
        d = super().load_profile(profile)
        for pid, ctime in d.copy().items():
            p = check_process_exists(pid, ctime)
            if p is False:
                d.pop(pid)
                self.empty_profile(profile,pid)
            else:
                self.processes.append(p)
        return d
    
    def get_val(self):
        self.processes = []
        super().get_val()
        return self.processes



class ThisScript:
    
    def __init__(self, name=None, folder = None, register=True, log_folder=None):
        if not name or not log_folder:
            try:
                f = __main__.__file__
            except AttributeError:
                f = None
        if name:
            self.name = name
        else:
            if not f:
                raise NameError("Name argument of ThisScript not specified and "
                                "no __main__.__file__ attribute found.")
            self.name = path.splitext(path.basename(f))[0]
        
        self.external_dict = ProcessCheckerExternalDict("Script_processes",
                folder=folder, profile=self.name, incl_default_profiles=False)
        self.process = psutil.Process()
        if register:
            self.register()
            launch.thread(self.register_thread)

    @property
    def active_processes(self):
        return self.external_dict.load()

    @property
    def registered_processes(self):
        return self.external_dict.val

    def register(self, pid=None):
        process = self.process if pid is None else psutil.Process(pid)
        self.external_dict.update_items({process.pid: process.create_time()})
        # identifying a process needs pid AND  # creation time. this is
        # actually also stored in  # process._ident and used for comparison
        # checks in the __eq__  # method of the process class of psutil
        self.external_dict.load()
    
    def register_thread(self):
        while True:
            time.sleep(10)
            self.register()
            
            

    def other_instance_procs(self):
        t=  tuple(proc
            for proc in self.active_processes if proc != self.process)
        if t: print(f"Found earlier instances: {t}")
        return t
    
    
    def terminate_other_instances(self, timeout=5):
        terminate_process(*self.other_instance_procs(), timeout=timeout)
        aprocs = self.active_processes
        assert len(aprocs) == 1
        assert aprocs[0] == self.process

    def terminate(self):
        terminate_process(self.process)