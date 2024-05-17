#
#
# Copyright (c) 2020-2024 DPS, dps@my.mail.de
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
    SingleResource, resource_property, resource_func
from types import GeneratorType
iter_types = (list,tuple,GeneratorType)



class ImageAdaptor(EditorAdaptor):
    
    pass
    


class ImageBase(ImageAdaptor.AdaptiveClass, SingleResource):
    
    
    
    def load(self, **kwargs):
        if self.ext in self.adaptor.multi_page_extensions:
            if "resolution" not in kwargs: kwargs["resolution"] = 300
        super().load(**kwargs)
        
        
    compression = resource_property("compression",
            jpg = ("jpeg", "j"),
            zip = "z")
    compr = compression
    
    compr_quality = resource_property("compr_quality")
    compression_quality = cquality = cqu = cqual = compression
    
    resolution = resource_property("resolution")
    res = resolution
    
    size = resource_property("size")
    
    colortypenames = {"gray": ("grayscale", "g")}
    colortype = resource_property("colortype", **colortypenames)
    ctype = type = colortype
    
    colorspace = resource_property("colorspace", **colortypenames)
    cspace = color = colorspace
    
    @resource_func
    def resample(self,value_x, value_y=None, *args,**kwargs):
        if value_y is None: value_y = value_x
        return (value_x, value_y, *args), kwargs



# @ImageBase.make_multi_base
# class MultiImage(MultiResource):
#     # created as a subclass of ImageBase.Sequence (see above)
#
#     pass