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
"""This module is intended as a single namespace where all of Dhelpers' objects
can be found.
Usage: from Dhelpers.all import ...

Do NOT use this kind of import if you want to distribute your code
 -- in this case explicitely state the module you want to import from.
"""


import os, warnings



from .importtools import import_all, extract_all

Dhelperspath = os.path.split(os.path.realpath(__file__))[0]


__all__ = []
for _,_mod in import_all(Dhelperspath, globals()):
    extract_all(_mod, globals(), __all__)
    
del _,_mod, os, warnings