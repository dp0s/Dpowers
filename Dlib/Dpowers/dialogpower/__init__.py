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
from .. import Adaptor, adaptionmethod


class DialogAdaptor(Adaptor):
    @adaptionmethod
    def date(self, selected=None, **kwargs):
        """selected_date must be of form (dd,mm,yyyy). returns the same
        format."""
        return self.date.target_with_args()
    
    @adaptionmethod
    def path(self, selected=None, multi=False, dir=False, **kwargs):
        return self.path.target_with_args()
    
    @adaptionmethod
    def savepath(self, selected=None, overwrite=False, **kwargs):
        return self.savepath.target_with_args()
    
    @adaptionmethod
    def msg(self, text, title="Message dialog", error=False, warning=False,
            **kwargs):
        if title == "Message":
            if error:
                title = "Error dialog"
                if warning: raise ValueError
            elif warning:
                title = "Warning dialog"
        return self.msg.target(text, title, error, warning, **kwargs)
    
    
    @adaptionmethod
    def quest(self, text, title="Question dialog", **kwargs):
        return self.quest.target_with_args()
    
    
    @adaptionmethod
    def inp(self, text="Enter a new text:", title="Text input dialog"):
        return self.inp.target_with_args()
    
    
    @adaptionmethod
    def choose(self, options, default=None, text="Select an option:",
            title="Select dialog", multi=False, **kwargs):
        if not isinstance(default, (list, tuple)): default = (default,)
        if not multi and len(default) > 1: raise ValueError(
                "Only one default value allowed unless multi=True.")
        return self.choose.target(options, default, text, title, multi,
                **kwargs)

    
    @adaptionmethod
    def popup(self,*buttons, xpos: int = 2, ypos: int = -25, x_rel_mouse: bool\
        = True,y_rel_mouse: bool = True):
        return self.popup.target_with_args()