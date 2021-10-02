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
    
    pass



class ImageBase(SingleResource, ImageAdaptor.AdaptiveClass):
    
    compression = resource_property("compression", "compr")
    compr_quality = resource_property("compr_quality", "compression_quality",
            "cquality", "cqu", "cqual")
    resolution = resource_property("resolution", "res")
    colortype = resource_property("colortype", "ctype", "type")
    size = resource_property("size")
    colorspace = resource_property("colorspace", "cspace", "color")

    @resource_func("res")
    def resample(self,value_x, value_y=None, *args,**kwargs):
        if value_y is None: value_y = value_x
        return (value_x, value_y, *args), kwargs



@ImageBase.make_multi_base
class MultiImage(MultiResource):
    # created as a subclass of ImageBase.Sequence (see above)
    allowed_file_extensions = [".pdf",".tif", ".tiff"]
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        super().__init__(file,resolution=resolution,**load_kwargs)
        
        
        
        
        
Values_for_Property = ImageAdaptor.Values_for_Property


class CommonColorTypeNames:
    gray = "gray", "grayscale", "g"
    
@Values_for_Property("colortype")
class ColortypeNames(CommonColorTypeNames):
    pass

@Values_for_Property("colorspace")
class ColorspaceNames(CommonColorTypeNames):
    pass


@Values_for_Property("compression")
class CompressionNames:
    jpg = "jpg", "jpeg", "j"
    zip = "zip", "z"