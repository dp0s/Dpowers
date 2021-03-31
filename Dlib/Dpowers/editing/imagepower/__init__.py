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
from types import GeneratorType
iter_types = (list,tuple,GeneratorType)



class ImageAdaptor(EditorAdaptor):
    
    @adaptionmethod
    def compression(self, backend_obj, value=None):
        return self.compression.target_with_args()
    
    @adaptionmethod
    def compr_quality(self, backend_obj, value=None):
        return self.compr_quality.target_with_args()


    @adaptionmethod
    def resolution(self, backend_obj, value=None):
        return self.resolution.target_with_args()

    @adaptionmethod
    def size(self, backend_obj, value=None):
        return self.size.target_with_args()
    
    @adaptionmethod
    def colortype(self, backend_obj, value=None):
        return self.colortype.target_with_args()



class ImageBase(Resource, ImageAdaptor.AdaptiveClass):
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.multipage = type("multipage", (multipage_mixin, cls.Sequence),{})
        cls.multipage.__module__ = cls.__module__


ImageBase.set_prop("compression", "compr")
ImageBase.set_prop("compr_quality", "compression_quality", "comprqu",
        "compr_q", "compr_qu", "comprq")
ImageBase.set_prop("size")
ImageBase.set_prop("resolution", "res")
ImageBase.set_prop("colortype", "color","type")



class multipage_mixin:
    # created as a subclass of ImageBase.Sequence (see above)
    
    def __init__(self, file=None, resolution=300, **load_kwargs):
        self.file=file
        if isinstance(file,iter_types): raise ValueError
        self.file = file
        self.filepath_split()
        backend_objs = self.adaptor.load_multi(file,
                resolution= resolution, **load_kwargs)
        images = tuple(self.SingleClass(backend_obj=bo) for bo in backend_objs)
        super().__init__(images=images)
        #self.compr("jpeg")
    
    def save(self, destination=None, combine=True):
        return super().save(destination, combine)