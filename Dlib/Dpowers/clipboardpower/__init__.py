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
from .. import Adaptor, adaptionmethod, ntfy, keyb
import time


class ClipboardAdaptor(Adaptor):
    selection_names = {
        0: "clipboard", 1: "primary selection", 2: "secondary selection"
        }
    
    @adaptionmethod
    def get(self, selection=0) -> str:
        """Retrieves the content
        
        :param selection: The selection to be retrieved. Defaults to 0,
            i.e. the standard clipboard.
        :returns str: retrieved content
        """
        return self.get.target_with_args()
    
    @adaptionmethod
    def fill(self, content:str, selection=0, notify=False):
        content=str(content)
        self.fill.target(content,selection)
        # now we check that the content was successfully pasted into the
        # selection:
        after = self.get(selection)
        if content.endswith("\n") and not after.endswith("\n"):
            after += "\n"
            # this is necessary because the use of launch.get in the xsel and
            #  xclip adaptions, will remove the last "\n" in the returned
            # after value in this case
        if after != content:
            raise ValueError("Failed to set clipboard content.\nExpected: '{"
                             "content}'\nActually: '{after}'".format_map(
                    locals()))
        if notify:
            ntfy("Saved to " + self.selection_names[selection], 3,after)
    
    
    def remove(self, selection=0):
        s = self.get(selection)
        self.fill("",selection)
        return s
    
    def monitor(self, selection=0, duration=60):
        for i in range(duration):
            ntfy("Monitoring " + self.selection_names[selection], 1,
                    self.get(selection))
            time.sleep(1)
    
    def saved(self,selection=0):
        return SelectionSaver(self,selection)
    
    def paste(self, string):
        with self.saved():
            self.fill(string)
            keyb.comb("ctrl", "v")



class SelectionSaver:
    """
    Saves the value of the clipboard inside a with clause is executed,
    and restores it automatically afterwards
    Usage:
    with saved() as s:
        some code(s)
        more code
    """
    
    def __init__(self, clipboardadaptor, selection=0):
        self.clipboardadaptor = clipboardadaptor
        self.selection = selection
    
    def __enter__(self):
        self.save = self.clipboardadaptor.remove(self.selection)
        return self.save
    
    def __exit__(self, *ignore_these_args):
        self.clipboardadaptor.fill(self.save, self.selection)