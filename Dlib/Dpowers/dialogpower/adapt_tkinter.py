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
import tkinter as tk
import functools


def popup(*buttons, xpos: int, ypos: int, x_rel_mouse: bool,y_rel_mouse: bool):
    """
    Function to show popup Menu with tkinter.
    _ can be used to specifiy hotkey characters.
    """
    
    root = tk.Tk()
    root.wm_attributes('-type', 'splash')
    root.focus_force()
    
    if x_rel_mouse:
        xpos = root.winfo_pointerx() - root.winfo_rootx() + xpos
        if xpos < 1: xpos = 1
    if y_rel_mouse:
        ypos = root.winfo_pointery() - root.winfo_rooty() + ypos
        if ypos < 1: ypos = 1
    root.geometry('+%s+%s'%(xpos, ypos))
    
    pressed_num = None
    
    def return_val(button_num, event=None):
        nonlocal pressed_num
        pressed_num = button_num
        root.destroy()
    
    root.bind_all("<FocusOut>", functools.partial(return_val, None))
    
    for num in range(len(buttons)):
        root.bind_all(str(num + 1), functools.partial(return_val, num))
        root.bind_all("<KP_%s>"%str(num + 1)
                ,functools.partial(return_val, num))
        
        i = str(num + 1) + " " + buttons[num]
        pos = i.find("_")
        if pos != -1 and pos + 1 < len(i):
            i = i[:pos] + i[pos + 1:]
            root.bind_all(i[pos].lower(), functools.partial(return_val, num))
        
        b = tk.Button(root, text=i, command=functools.partial(return_val, num),
                underline=pos, anchor="w")
        b.pack(fill="x")
    
    tk.mainloop()
    if pressed_num is not None:
        return buttons[pressed_num]
