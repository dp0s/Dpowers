#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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
from contextlib import contextmanager



class BooleanFunction:
    
    _cache_lvl = False
    _last_cache_lvl = 0
    
    @classmethod
    def getfunc(cls, func):
        if isinstance(func, cls): func = func._func
        assert callable(func)
        return func

    def __init__(self,name=None, func=None):
        self.name = name
        self._func = self.getfunc(func)
        self.cached_val=None
        
    def func(self, *args, **kwargs):
        cls_cache_lvl = self.__class__._cache_lvl
        if cls_cache_lvl is False:
            # this means cashing is disabled
            return bool(self._func(*args,**kwargs))
        if self.cached_val is None or self._cache_lvl <= cls_cache_lvl:
            self.cached_val = bool(self._func(*args,**kwargs))
            self._cache_lvl = cls_cache_lvl + 1
            # set this instance's cache level so it won't be re-evaluated
            # until the classe's cache level is increased again by calling
            # the cls._reset_cache function
        return self.cached_val
    
    __call__ = func
    
    
    @classmethod
    @contextmanager
    def use_cache(cls):
        # Usage: see FilelistCreator.find_files method below
        cls._cache_lvl = cls._last_cache_lvl + 1
        try:
            yield cls._reset_cache  #this will return a function from
            # the with statement that can be called to reset the cache
            # while inside the with statement
        finally:
            # when the with statement is finished, disable the cash
            cls._last_cache_lvl = cls._cache_lvl
            cls._cache_lvl = False
    
    @classmethod
    def _reset_cache(cls):
        cls._cache_lvl += 1
        
    
    
    def negate(self):
        return self.__class__(
                func=lambda *args, **kwargs: not self.func(*args, **kwargs))
    def __and__(self, other):
        assert callable(other)
        return self.__class__(func=lambda *args, **kwargs:
                self.func(*args, **kwargs) & bool(other(*args, **kwargs)))
    def __or__(self, other):
        assert callable(other)
        return self.__class__(func=lambda *args, **kwargs:  self.func(*args,
                **kwargs) | bool(other(*args, **kwargs)))