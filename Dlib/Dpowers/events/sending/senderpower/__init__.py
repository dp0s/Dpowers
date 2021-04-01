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

from ... import adaptionmethod
from ..event_sender import AdaptiveSender, AdaptivePressReleaseSender


class SenderAdaptorMixin:
    
    
    default_delay = 0
    """
    .. exec::

        event_sender.default_delay_doc("events")
    """
    
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.selected_devs = []
        
    @adaptionmethod
    def select_device(self, **kwargs):
        devices = self.select_device.target(**kwargs)
        if not devices: raise ValueError
        self.selected_devs+= devices
        return self.selected_devs
    
    
class SenderAdaptor(SenderAdaptorMixin, AdaptiveSender):
    # inherits adaptionmethod _press
    pass

class PressReleaseSenderAdaptor(SenderAdaptorMixin, AdaptivePressReleaseSender):
    
    # inherits adaptionmethods _press and _rls
    
    default_duration = 1
    """
    .. exec::

        event_sender.default_duration_doc("event object")
    """