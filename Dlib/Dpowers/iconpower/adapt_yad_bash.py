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
from Dhelpers.launcher import launch
from Dhelpers.adaptor import DependencyManager


with DependencyManager(__name__) as tester:
    tester.test_shellcommand("yad", pkg="yad")




def start(IconObject):
    cmd = tuple(create_yad_cmd(IconObject))
    #print(cmd)
    child = launch(cmd, stdout=True)
    launch.thread(waiter, IconObject, child.stdout)
    return child.pid

def create_yad_cmd(IconObject):
    # the default behavior when clicking on the icon is to close the  Can be
    # changed with click_cmd
    # if menu=="":
    #            menu=standard_menu
    yield "yad"
    yield "--notification"
    yield "-- listen"
    if IconObject.path:
        yield "--image=" + IconObject.path
    #if click_cmd:
     #   yield " --command=" + shlex.quote(click_cmd)
    if IconObject.tooltip:
        yield "--text=" + IconObject.tooltip
    items = IconObject.items
    if items:
        text="--menu="
        for item in items:
            text+= item[0] +"!echo "+item[0]+"|"
        text=text[:-1]
        yield text


def waiter(Iconobject, stdout):
    for line in stdout:
        # this is executed, each time we receive a message from YAD
        for i in Iconobject.items:
            if line == i[0] + "\n":
                # print("execute: "+str(i[1]))
                launch.thread(i[1])
    if Iconobject.left_click:
        Iconobject.left_click()