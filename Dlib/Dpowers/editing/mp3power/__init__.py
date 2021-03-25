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
from ..ressource_classes import EditorAdaptor, adaptionmethod, Resource


class mp3tagAdaptor(EditorAdaptor):
    
    @adaptionmethod
    def genre(self, backend_obj, value=None):
        return self.genre.target_with_args()
    
    
    
class mp3tagBase(Resource, mp3tagAdaptor.AdaptiveClass):
    allowed_file_extensions = [".mp3"]


mp3tagBase.set_prop("genre")