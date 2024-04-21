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


# usage:
# from .psutil_fix import psutil


# this fixes an annoying error message on termux/android where /proc
# permission is not given
# see https://stackoverflow.com/questions/62640148

# it also introduces a placeholder so that if psutil is not installed,
# do not raise an exception when importing it, but only when actually using it.

import os,sys, warnings


class PsutilPlaceholder:
  
  def __init__(self, error):
    self.error = error
  
  def __getattr__(self, item):
    raise self.error



sys.stderr = open(os.devnull, "w")
# send error messages to the void to supress annoying error on termux


try:
  import psutil
except ModuleNotFoundError as e:
  warnings.warn(str(e))
  psutil = PsutilPlaceholder(e)
finally:
  # reset the stderr to normal
  # it makes sure that normal error messages inside psutil are still printed
  # because they are raised after the finally statement.
  # the annoying termux error is raised in a seperate thread during import
  # and thus is raised before the finally statement (and thus supressed)
  sys.stderr = sys.__stderr__
