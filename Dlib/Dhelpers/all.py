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


Dhelperspath = os.path.split(os.path.realpath(__file__))[0]

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
        dir = os.path.join(folder,modname)
        if "__init__.py" not in os.listdir(dir): continue
        try:
            yield modname, __import__(modname, globals=globals, level=1)
        except ModuleNotFoundError as e:
            if raise_error: raise
            warnings.warn(f"Subpackage {modname} not loaded because of error: {e}")

def extract_all(mod, globals, all):
    try:
        names = mod.__all__
    except AttributeError:
        names = tuple(name for name in mod.__dict__ if not name.startswith(
                "__"))
    for name in names:
        if name in globals: continue
        globals[name] = getattr(mod, name)
        all.append(name)

__all__ = []
for _,_mod in import_all(Dhelperspath, globals()):
    extract_all(_mod, globals(), __all__)
    
del _,_mod, os, warnings