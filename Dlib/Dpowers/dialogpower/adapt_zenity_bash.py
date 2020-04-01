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
from .. import Win
import os

check_bash_cmd("zenity")

def run_zenity(arg1, *args, allow_retCodes=(0, 1), check_err=False):
    cmd = ("zenity", "--" + arg1, *args)
    # print(cmd)
    stderr = True if check_err else None
    process = launch(cmd, stdout=True, stderr=stderr)
    Win(pid=process.pid).wait_exist_activate()
    out, err = process.communicate()
    retCode = process.returncode
    if retCode != 0 and retCode not in allow_retCodes:
        raise launch.CalledProcessError(retCode, process.args)
    if check_err and err:
        if err != "Gtk-Message: GtkDialog mapped without a transient parent. " \
                  "This is discouraged.\n":
            raise launch.SubprocessError(
                    "Subprocess {process.args} returned error:\n{"
                    "err}".format_map(locals()))
    if out.endswith("\n"): out = out[:-1]
    return out, err, retCode


def kwargs_helper(**kwargs):
    kwargs["no_markup"] = kwargs.get("no_markup", True)
    # we want to use the no_markup_option by default to make sure that the
    # zenity ability for pango markup is disabled by default.
    for param, value in kwargs.items():
        if "_" in param:
            param = param.replace("_", "-", 1)
        if value is True:
            # print(param,value)
            yield "--" + param
        elif value not in (None, False):
            yield "--%s=%s"%(param, str(value))



def date(selected, **kwargs):
    if selected:
        kwargs["day"], kwargs["month"], kwargs["year"] = selected
    out, err, retCode = run_zenity("calendar",
            *kwargs_helper(date_format="%d/%m/%Y", **kwargs))
    if retCode == 0: return tuple(int(x) for x in out.split("/"))


def path(selected, multi, dir, **kwargs):
    if selected:
        if not os.path.lexists(selected):
            raise ValueError("File %s does not exist!"%selected)
        kwargs['filename'] = selected
    out, err, retCode = run_zenity('file-selection',
            *kwargs_helper(multiple=multi, separator="|", directory=dir,
                    **kwargs))
    if retCode == 0: return out.split("|") if multi else out


def savepath(selected, overwrite, **kwargs):
    out, err, retCode = run_zenity('file-selection',
            *kwargs_helper(filename=selected, save=True,
                    confirm_overwrite=not overwrite, **kwargs))
    if retCode == 0: return out


def msg(text, title, error, warning, **kwargs):
    if error:
        cmd = "error"
    elif warning:
        cmd = "warning"
    else:
        cmd = "info"
    out, err, retCode = run_zenity(cmd,
            *kwargs_helper(text=text, title=title, **kwargs))
    if retCode == 0: return out


def quest(text, title, **kwargs):
    out, err, retCode = run_zenity("question",
            *kwargs_helper(text=text, title=title, **kwargs))
    return retCode == 0


def inp(text, title, **kwargs):
    out, err, retCode = run_zenity("entry",
            *kwargs_helper(text=text, title=title, **kwargs))
    if retCode == 0: return out


def table(column_names, data, autoheight=True, text=None, title=None,
        select_col=None, multi=False, **kwargs):
    if column_names.count("") == len(column_names):
        # this is true if column_names only contains empty strings
        kwargs["hide_header"] = True
    if autoheight:
        pixel = 160
        pixel += (len(data) - 1)//len(column_names)*28
        if text:
            pixel += text.count("\n")*20
        kwargs["height"] = pixel
    if select_col: kwargs["print_column"] = True
    
    args = []
    for column in column_names: args.append('--column=%s'%column)
    
    args += list(kwargs_helper(text=text, title=title, separator="|",
            checklist=multi, **kwargs))
    
    for datum in data:
        args.append(str(datum))
    
    out, err, retCode = run_zenity("list", *args)
    if retCode == 0: return out.split("|") if multi else out



def choose(options, defaults, text, title, multi, **kwargs):
    data = []
    for i in range(len(options)):
        x = options[i]
        if not isinstance(x, str):
            raise TypeError("Options must all be of type str.")
        data.append((i in defaults) or (x in defaults))
        # This determines the default values marked.
        data.append(x)
    if not multi: kwargs["radiolist"] = True
    return table(column_names=("", ""), data=data, autoheight=True, text=text,
            title=title, multi=multi, **kwargs)
