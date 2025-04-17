#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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
import functools

def _add_tty_disable_option(func):
    @functools.wraps(func)
    def new_func(*args, disable_if_tty=False, **kwargs):
        if sys.stdout.isatty() and disable_if_tty:
            print("%s was ignored as stdout is a tty"%func.__name__)
            return
        return func(*args, **kwargs)
    return new_func


from .customprint import *
from .error_warning import *