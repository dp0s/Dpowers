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
from Dhelpers.adaptor import DependencyManager

with DependencyManager(__name__) as tester:
    im_mod = tester.import_module("wand.image", pkg="wand")

Image = im_mod.Image

obj_class = Image


def load(file, **kwargs):
    with Image(filename=file, **kwargs) as im:
        s = im.sequence
        if len(s) == 0: raise ValueError
        if len(s) == 1: return im.clone()
        raise ValueError(f"More than one image in file {file}.")
    
def load_multi(file, **kwargs):
    with Image(filename=file, **kwargs) as im:
        s = im.sequence
        if len(s) == 0: raise ValueError
        return tuple(Image(i) for i in s)
    

def construct_multi(sequence_of_objs):
    im  = Image()
    for o in sequence_of_objs:
        im.sequence.append(o)
    return im

def save(obj, destination):
    obj.save(filename = destination)
    
def close(obj):
    obj.destroy()

def compression(obj, value):
    if value is None: return obj.compression
    obj.compression = value

def compr_quality(obj, value):
    if value is None: return obj.compression_quality
    obj.compression_quality = value
    
def resolution(obj, value):
    if value is None: return obj.resolution
    obj.resolution = value

def size(obj, value):
    if value is None: return obj.size
    obj.size = value
    
def colortype(obj, value):
    if value is None: return obj.type
    obj.type = value

# def set_value(backend_obj, name, value = None):
#     val_before = getattr(backend_obj, name)
#     if value is None: return val_before
#     return setattr(backend_obj, name, value)