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
from ..ressource_classes import EditorAdaptor, adaptionmethod, \
    SingleResource, MultiResource, resource_property, resource_func
from types import GeneratorType
iter_types = (list,tuple,GeneratorType)



class ImageAdaptor(EditorAdaptor):
    
    @adaptionmethod
    def resample(self, backend_obj, value_x, value_y=None):
        if value_y is None: value_y = value_x
        return self.resample.target(backend_obj, value_x, value_y)
    
    

@ImageAdaptor.Values_for_Property("colortype")
class ColortypeNames:
    gray = "gray", "grayscale"
    

class ImageBase(SingleResource, ImageAdaptor.AdaptiveClass):
    
    compression = resource_property("compression", "compr")
    compr_quality = resource_property("compr_quality", "compression_quality",
            "quality", "qual")
    resolution = resource_property("resolution", "res")
    colortype = resource_property("colortype", "ctype", "color")
    size = resource_property("size")

    resample = resource_func("resample")
    







@ImageBase.make_multi_base
class MultiImage(MultiResource):
    # created as a subclass of ImageBase.Sequence (see above)
    allowed_file_extensions = [".pdf",".tif", ".tiff"]
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        super().__init__(file,resolution=resolution,**load_kwargs)