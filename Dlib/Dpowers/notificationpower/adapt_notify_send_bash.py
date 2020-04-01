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

check_bash_cmd("notify-send")

def post_notification(title,timeout,text):
    text = text.replace("<", "&lt;").replace(">","&gt;")
    # necessary because otherwise < and > will be interpreted as html mark-up tags
    

    launch.get('notify-send', '-t', int(timeout * 1000), title, text)