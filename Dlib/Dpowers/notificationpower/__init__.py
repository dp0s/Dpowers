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
from .. import Adaptor, adaptionmethod


class NotificationAdaptor(Adaptor):
    
    active = True
        
    def __call__(self, title: str, timeout=3, text: str = ""):
        if self.active:
            title = str(title)
            text=str(text)
            if title == "": title = " "
            self.post_notification(title,timeout,text)
            return True
        return False
        
    @adaptionmethod
    def post_notification(self, title, timeout, text):
        return self.post_notification.target_with_args()
    
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def toggle(self):
        self.__call__("Notifications turned off.")
        self.active = not self.active
        self.__call__("Notifications turned on.")