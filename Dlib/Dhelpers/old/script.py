#
# Copyright (c) 2020 DPS, dps@my.mail.de
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
import tempfile, os, psutil, __main__
from .launcher import terminate_process

class ThisScript:
    def __init__(self, name=None, register=True, update=True, log_folder=None):
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
            self.name = os.path.splitext(os.path.basename(f))[0]
        if not log_folder:
            log_folder = os.path.dirname(f) if f else tempfile.gettempdir()
        self.file = os.path.join(log_folder, "Dhelpers_ThisScript_" + self.name)
        self.process = psutil.Process()
        if update: self.update()
        if register: self.register()
    
    
    def remove_file(self):
        try:
            os.remove(self.file)
            return True
        except FileNotFoundError:
            return False
    
    def _register(self, process):
        with open(self.file, "a") as f:
            f.write("%d %f\n" % (process.pid, process.create_time()))
            # identifying a process needs pid AND creation time.
            # this is actually also stored in process._ident and used for
            # comparison checks in the __eq__ method of the process class of
            # psutil
    
    def register(self, pid=None):
        process = self.process if pid is None else psutil.Process(pid)
        if process not in self.registered_procs(): self._register(process)
    
    def update(self, pids=None):
        if pids:
            procs = tuple(psutil.Process(pid) for pid in pids)
        else:
            procs = self.registered_procs()
        self.remove_file()
        for proc in procs: self._register(proc)
        
    def registered_procs(self):
        L = []
        try:
            with open(self.file) as f:
                for line in f:
                    s = line.split(" ")
                    pid, create_time = int(s[0]), float(s[1])
                    try:
                        process = psutil.Process(pid)
                    except psutil.NoSuchProcess:
                        continue
                    if process.create_time() == create_time:
                        L += [process]
        except FileNotFoundError:
            pass  # yield nothing because not yet existing
        return L
    
    def other_instance_procs(self):
        return tuple(proc for proc in self.registered_procs() if proc !=
                                                                 self.process)
    
    def terminate_other_instances(self):
        terminate_process(*self.other_instance_procs())
        self.update()
    
    def terminate(self):
        terminate_process(self.process)
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return self.process == other.process and self.file == other.file
        return NotImplemented
    
    def __hash__(self):
        return hash((self.process,self.file))