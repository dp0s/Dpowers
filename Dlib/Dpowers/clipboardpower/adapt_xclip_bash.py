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
from Dhelpers.all import launch, check_bash_cmd

check_bash_cmd("xclip")

xclip_names = {0: "c", 1: "p", 2: "s"}

def get(selection=0) -> str:
    try:
        return launch.get("xclip", "-o", "-selection", xclip_names[selection])
    except launch.SubprocessError:
        return ""

def fill(content: str, selection=0):
    launch.wait("xclip", "-i", "-selection", xclip_names[selection],
            input=content)