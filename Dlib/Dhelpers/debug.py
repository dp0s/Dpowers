#
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
#
import builtins,time

def replace_import_func():
  builtins.__import = __import__
  it={}
  def my_import(*args,**kwargs):
    start=time.time()
    ret = __import(*args,**kwargs)
    duration=time.time() - start
    if ret not in it: it[ret.__name__]=duration
    return ret
  builtins.__import__ = my_import
  return lambda: sorted(it.items(),key=lambda item:item[1])




import threading, traceback

class ThreadNode:
  def __init__(self, parent, child):
    self.parent = parent
    if hasattr(parent,"child_nodes"):
      parent.child_nodes.append(self)
    else:
      parent.child_nodes = [self]
    self.child = child
    self.tb = traceback.format_stack()[:-2]
  
  def print_tb(self, lines=None):
    tb = self.tb if lines is None else self.tb[-lines:]
    for line in tb: print(line,end="")

def replace_threading_start():
  start_original = threading.Thread.start
  def start(self):
    self.parent_node = ThreadNode(threading.current_thread(),self)
    self.child_nodes = []
    return start_original(self)
  threading.Thread.start = start