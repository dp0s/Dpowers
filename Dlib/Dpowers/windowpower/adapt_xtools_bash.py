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
import shlex, re
from Dhelpers.arghandling import CollectionWithProps, NonNegativeInt

from .. import DependencyManager, launch

with DependencyManager(__name__) as manager:
    current_id = manager.test_shellcommand("xdotool",test_cmd ="xdotool "
                                   "getactivewindow", pkg="xdotool")
    #checks if xdotool is installed and if getactivewindow works

    manager.test_shellcommand("wmctrl", pkg="wmctrl")

    manager.test_shellcommand("xprop", f"xprop -id {current_id} WM_CLASS")
    # checks if xprop is installed and if it gets the current window's class



def screen_res():
    command = "xdotool getdisplaygeometry"
    a, b = launch.get(command).split(" ")
    return int(a), int(b)


def _xdo_cmd(title=None, cl=None, cl_name=None, pid=None, ID=None,
        all_param=True, onlyvisible=False, limit=0, add_final=None):
    cmd = ["xdotool"]
    if ID:
        cmd += shlex.split(add_final) + [ID]
    else:
        if title == ":ACTIVE:":
            cmd += ["getactivewindow"]
        elif title == ":SELECT:":
            cmd += ["selectwindow"]
        else:
            cmd += ["search"]
            if onlyvisible:
                cmd += ["--onlyvisible"]
            if limit > 0:
                cmd += ["--limit", limit]
            if all_param:
                cmd += ["--all"]
            if cl_name:
                cmd += ["--classname", cl_name]
            if cl:
                cmd += ["--class", cl]
            if pid:
                cmd += ["--pid", pid]
            if title:
                cmd += ["--name", "--", title]
                # the additional -- are important to make clear that title
                # can start with - and is still not a parameter
        if add_final:
            cmd += shlex.split(add_final)
    # print(cmd)
    return cmd

# sometimes executing xdotool results in a X Error of failed request:
# BadWindow (invalid Window parameter). (
# Somehow always when I use ntfy)
# In this case xdotool does not find a window although it exists. So we will
#  use a cheap workaround:


# def _bash_wait_workaround(command, **unimportant):
#     # if the window exists, but is not found due to an X Error, we can try up
#     #  to three times.
#     for j in range(3):
#         x = launch.get(command, check=False, check_stderr=False)
#         if x:
#             return x
#         if j > 2:
#             time.sleep(0.01)
#     print(x)
#     return x



def _xdo_get_from_single_id(ID, add_final):
    # add_final contains the information about which information to retrieve
    # from window with given ID
    x = launch.get(_xdo_cmd(ID=ID, add_final=add_final), check=False,
            check_err=False)
    if x: return x

# find all window ids matching the given pattern

def _xdo_get_ids(*win_args, **win_kwargs):
    cmd = _xdo_cmd(*win_args,  **win_kwargs, add_final=None)
        # add_final=None makes sure that IDs are returned
    try:
        x = launch.get(cmd)
    except launch.CalledProcessError:
        return set()
    if type(x) is str:
        return [int(i) for i in x.split("\n")]



def ID_from_location(param):
    if isinstance(param,
            CollectionWithProps(NonNegativeInt, len=2, allow_set=False)):
        x, y = param
        command = ["xdotool", "mousemove", x, y, "getmouselocation",
            "mousemove", "restore"]
        return int(re.split('[\s:]', launch.get(command))[7])
    elif isinstance(param, str):
        param = param.lower()
        if param in ("m", "mouse"):
            command = ["xdotool", "getmouselocation"]
            return int(re.split('[\s:]', launch.get(command))[7])
        elif param in ("a", "act", "active"):
            return _xdo_get_ids(title=":ACTIVE:")[0]
        elif param in ("s", "sel", "select"):
            return _xdo_get_ids(title=":SELECT:")[0]
    raise NotImplementedError

allowed_properties = "title", "wcls", "pid"

def IDs_from_property(prop_name, prop_val, visible):
    if prop_name == "title":
        return _xdo_get_ids(title=prop_val, onlyvisible=visible)
    elif prop_name == "wcls":
        wcls = prop_val
        if "." in wcls:
            cl_name, cl = wcls.split(".")
            # cls is a string of pattern "cl_name.cl" usually
            return tuple(set(_xdo_get_ids(cl=cl, onlyvisible=visible)) & set(
                    _xdo_get_ids(cl_name=cl_name, onlyvisible=visible)))
        else:
            return _xdo_get_ids(cl=wcls, onlyvisible=visible)
    elif prop_name == "pid":
        return _xdo_get_ids(pid=prop_val, onlyvisible=visible)
    raise NotImplementedError


def property_from_ID(ID, prop_name):
    if prop_name == "title":
        return _xdo_get_from_single_id(ID, "getwindowname")
    elif prop_name == "wcls":
        x = re.split('"', launch.get("xprop", "-id", ID, "WM_CLASS"))
        return x[-4] + '.' + x[-2]
    elif prop_name == "pid":
        p = _xdo_get_from_single_id(ID, "getwindowpid")
        if p is None: return
        return int(p)
    elif prop_name == "geometry":
        g = _xdo_get_from_single_id(ID, "getwindowgeometry -shell")
        x = re.split("[\n=”]", g)
        return int(x[3]), int(x[5]), int(x[7]), int(x[9])
        # pos x, posy, width, height
    raise NotImplementedError


def activate(ID):
    return _xdo_get_from_single_id(ID, "windowactivate --sync")

def map(ID):
    return _xdo_get_from_single_id(ID,"windowmap --sync")

def unmap(ID):
    return _xdo_get_from_single_id(ID,"windowunmap --sync")

def set_prop(ID, action: str, prop: str, prop2):
    cmd = ["wmctrl", "-i", "-r", ID, "-b", action + "," + prop]
    if prop2:
        cmd[-1] += "," + prop2
    return launch.get(cmd)


def move(ID, x, y, width, height):
    # print("wmctrl -r -i %s -e '0,%s,%s,%s,%s'" % (winID,x,y,width,height))
    return launch.get("wmctrl -i -r %s -e '0,%s,%s,%s,%s'"%(
        ID, int(x), int(y), int(width), int(height)))


def close(ID):
    return _xdo_get_from_single_id(ID, "windowclose")


def kill(ID):
    return _xdo_get_from_single_id(ID, "windowkill")


def minimize(ID):
    return _xdo_get_from_single_id(ID, "windowminimize")
