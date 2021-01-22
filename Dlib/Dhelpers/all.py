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
import os, warnings
import os.path as p




Dhelperspath = p.split(p.realpath(__file__))[0]


def import_all(folder, globals, raise_error=False):
    _, folders, files = os.walk(folder).__next__()
    for file in files:
        if not file.endswith(".py"): continue
        modname = file[:-3]
        try:
            yield modname, __import__(modname, globals=globals, level=1)
        except ModuleNotFoundError as e:
            if raise_error: raise
            warnings.warn(f"Module {modname} not loaded because of error: {e}")
    for modname in folders:
        dir = p.join(folder,modname)
        if "__init__.py" not in os.listdir(dir): continue
        try:
            yield modname, __import__(modname, globals=globals, level=1)
        except ModuleNotFoundError as e:
            if raise_error: raise
            warnings.warn(f"Subpackage {modname} not loaded because of error: {e}")


for modname,mod in import_all(Dhelperspath, globals()):
    g = globals()
    for name,value in mod.__dict__.items():
        if name in g:
            #warnings.warn(f"Name {name} already defined: {g[name]}")
            continue
        g[name] = value
        #print(name, " from ", mod)

del g, mod, name, value, p