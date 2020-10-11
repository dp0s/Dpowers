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
from inspect import signature, Signature, Parameter as Param


class ArgSaver:
    def __init__(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs



### changing signatures:

def _get_sig(sig_or_func):
    if isinstance(sig_or_func, Signature): return sig_or_func
    if callable(sig_or_func): return signature(sig_or_func)
    raise TypeError

def remove_first_arg(sig_or_func):
    sig = _get_sig(sig_or_func)
    args_without_first = list(sig.parameters.values())[1:]
    # #this removes the self argument from the cls_func parameters
    return sig.replace(parameters=args_without_first)

def add_kw_only_arg(sig_or_func, name,*,default=Param.empty, annotation=Param.empty):
    sig = _get_sig(sig_or_func)
    param = list(sig.parameters.values())
    new_param = Param(name, Param.KEYWORD_ONLY, default=default,
            annotation=annotation)
    if param:
        p = param[-1]
        if p.kind == Param.VAR_KEYWORD:
            param.insert(-1, new_param)
        else:
            param.append(new_param)
    else:
        param.append(new_param)
    return sig.replace(parameters=param)


# =======================================================================
# argument handling
# =======================================================================

def unpack_if_single(iterobj):
    if isinstance(iterobj, (list, tuple, set)):
        if len(iterobj) == 1:
            return iterobj[0]
    return iterobj

def pack_single(iterobj):
    if isinstance(iterobj, (list, tuple, set)):
        return iterobj
    return [iterobj]


def extract_if_single_collection(star_args):
    if len(star_args) == 1:
        x = star_args[0]
        if isinstance(x,(list, tuple, set, dict)):
            return x
    elif len(star_args) == 0:
        raise SyntaxError
    return star_args



# =======================================================================
# checking paramter types and values
# =======================================================================


def check_type(allowed_types, *objs, allowed=(), suppress_error=False):
    if len(objs) == 0: raise SyntaxError
    allowed_types = tuple(pack_single(allowed_types))
    # for a in allowed_types: if type(type(a)) is not type: # type(a) can be
    # a metaclass, but type(type(a)) is the equal to type
    # raise SyntaxError("allowed_types must contain a type or class.")
    for obj in objs:
        if isinstance(obj, allowed_types): continue
        if obj in allowed: continue
        break
    else:
        return True  # if all objs passed the test
    if suppress_error: return False
    raise TypeError("Got object %s of type "
                    "%s.\nallowed_types: %s\nallowed_additional:%s"%(
                        obj, type(obj), str(allowed_types), str(allowed)))


class _BoundedNumberMeta(type):
    def __instancecheck__(cls, instance):
        # print("checking",instance, cls.allowed_number_types)
        if isinstance(instance, cls.allowed_number_types):
            if cls.minval is not None:
                if instance < cls.minval: return False
            if cls.maxval is not None:
                if instance > cls.maxval: return False
            return True
        return False

# raise ValueError("Got obj %s of type %s.\nExpected minimum
# value: %s" % (
#                            str(obj), type(obj), min))
# raise ValueError("Got obj %s of type %s.\nExpected "
#                "maximum value: %s" % (
#                   str(obj), type(obj), max))

def BoundedNumber(minval=None, maxval=None, allowed_number_types=(int, float),
        name="BoundedNumberClass"):
    allowed_number_types = tuple(pack_single(allowed_number_types))
    return _BoundedNumberMeta(name, (), locals())

PositiveInt = BoundedNumber(minval=1, allowed_number_types=int,
        name="PositiveInt")
NonNegativeInt = BoundedNumber(minval=0, allowed_number_types=int,
        name="NonNegativeInt")
NonNegativeNumber = BoundedNumber(minval=0, name="NonNegativeNumber")



class _CollectionWithPropsMeta(type):
    def __instancecheck__(cls, instance):
        if not isinstance(instance, cls.allowed_collection_types): return False
        l = len(instance)
        if l < cls.minlen: return False
        if cls.maxlen is not None:
            if l > cls.maxlen: return False
        for item in instance:
            if cls.allowed_item_types is not None:
                if isinstance(item, cls.allowed_item_types): continue
            if item in cls.allowed_items: continue
            return False
        return True  # if all items passed the test

#
# raise ValueError("Got obj %s of type %s with length "
#                  "%s.\nExpected minimum length: %s" % (
#                      str(obj), type(obj), l, lmin))
# raise ValueError("Got obj %s of type %s with length "
#                                      "%s.\nExpected maximum length: %s" % (
#                                          str(obj), type(obj), l, lmax))

def CollectionWithProps(allowed_item_types=None, len=None, minlen=0,
        maxlen=None, allowed_items=(), allow_list=True, allow_tuple=True,
        allow_set=True, name="CollectionWithPropsClass"):
    if len: minlen, maxlen = len, len
    allowed_collection_types = \
        (list,)*allow_list + (tuple,)*allow_tuple + (set,)*allow_set
    return _CollectionWithPropsMeta(name, (), locals())



def make_tuple(obj, ty):
    if not isinstance(obj, (tuple, list, set)):
        if obj is None: return tuple()
        check_type(ty,obj)
        return (obj,)
    obj = tuple(obj)
    check_type(CollectionWithProps(ty),obj)
    return obj
