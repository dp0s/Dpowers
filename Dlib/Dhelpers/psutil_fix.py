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
import os,sys, warnings

#this fixes an annoying error message on termux/android where /proc
# permission is not given
# see https://stackoverflow.com/questions/62640148

sys.stderr = open(os.devnull, "w")
try:
  import psutil
except ModuleNotFoundError as e:
  warnings.warn(str(e))
  psutil = None
finally:
  sys.stderr = sys.__stderr__
