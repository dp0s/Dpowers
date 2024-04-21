#
#
# Copyright (c) 2020-2024 DPS, dps@my.mail.de
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