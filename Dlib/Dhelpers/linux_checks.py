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
from Dhelpers.launcher import launch
from warnings import warn
import inspect

class BashDependencyError(Exception):
    pass

def check_bash_cmd(cmd, msg=None, expected_return=None, warning=False,
        run_command=None):
    module = inspect.currentframe().f_back.f_globals["__name__"]
    def warn_or_error(specific_msg):
        m = "\nTrying to load the following module: %s\n%s" % (module,specific_msg)
        if msg: m += "\n--> " + msg
        if warning:
            warn(m)
            return False
        else:
            raise BashDependencyError(m)

    first = cmd.split(" ")[0]
    try:
        out = launch.get("which "+ first)
    except launch.CalledProcessError:
        return warn_or_error(
                "The following required bash command could not be found: "
                "'%s'"%first)

    if (first != cmd and run_command is None) or run_command is True:
        try:
            out = launch.get(cmd)
        except launch.CalledProcessError:
            return warn_or_error("The test bash command '{cmd}' returned non "
                               "zero exit status.".format_map(locals()))
        
    if expected_return is not None and out != expected_return:
        return warn_or_error(
                "The test bash command '{cmd}'\n returned the value '{out}', "
                "\n but it should return '{expected_return}'.".format_map(
                        locals()))
    
    return out