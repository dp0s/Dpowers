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
import functools

def extend_to_collections(simple_func):
    @functools.wraps(simple_func)
    def collection_func(arg, *args, **kwargs):
        if isinstance(arg, list):
            return [simple_func(a, *args, **kwargs) for a in arg]
        elif isinstance(arg, tuple):
            return tuple(simple_func(a, *args, **kwargs) for a in arg)
        elif isinstance(arg, set):
            return set(simple_func(a, *args, **kwargs) for a in arg)
        else:
            return simple_func(arg, *args, **kwargs)
    return collection_func


def extend_to_collections_dirs(simple_func):
    collection_func = extend_to_collections(simple_func)
    @functools.wraps(simple_func)
    def flexible_func(arg, *args, dict_keys=True, dict_vals=False, **kwargs):
        if isinstance(arg, dict):
            if dict_keys and not dict_vals:
                return {collection_func(k, *args, **kwargs): v for (k, v) in
                    arg.items()}
            elif dict_vals and not dict_keys:
                return {k: collection_func(v, *args, **kwargs) for (k, v) in
                    arg.items()}
            elif dict_vals and dict_keys:
                return {collection_func(k, *args, **kwargs): collection_func(v,
                        *args, **kwargs) for (k, v) in arg.items()}
            else:
                return arg
        return collection_func(arg, *args, **kwargs)
    return flexible_func


def ignore_first_arg(decorator):
    def new_decorator(func):
        @functools.wraps(func)
        def func2(firstarg, *args, **kwargs):
            pfunc = functools.partial(func, firstarg)
            return decorator(pfunc)(*args, **kwargs)
        return func2
    return new_decorator