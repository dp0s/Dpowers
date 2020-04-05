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
from Dhelpers.all import (check_type, PositiveInt, CollectionWithProps,
    NonNegativeInt, AdditionContainer)

import inspect, time, functools
from abc import ABC, abstractmethod


class WindowNotFoundError(Exception):
    pass
    
class WindowObject(ABC):
    
    adaptor = NotImplemented
    
    def _FoundWindows(self,*args,**kwargs):
        return FoundWindows(*args,adaptor=self.adaptor, **kwargs)

    def _WindowSearch(self, *args, **kwargs):
        return WindowSearch(*args, adaptor=self.adaptor, **kwargs)
    
    @abstractmethod
    def IDs(self):
        raise NotImplementedError
    
    @abstractmethod
    def existing_IDs(self):
        raise NotImplementedError
    
    def ID(self):
        return self._make_single_val(self.IDs())
    
    @staticmethod
    def _make_single_val(list_of_vals):
        if inspect.isgenerator(list_of_vals):
            try:
                val = list_of_vals.__next__()
            except StopIteration:
                return  # return None if no matching window found
            try:
                list_of_vals.__next__()
            except StopIteration:
                return val  # return the found val if exactly one found
        else:
            l = len(list_of_vals)
            if l == 0: return
            if l == 1: return list_of_vals[0]
        raise ValueError("More than one matching window found.")
    
    @property
    def num(self):
        return len(self.IDs())
  
    def __bool__(self):
        # This allows to use if win("test"): do_something
        return bool(self.IDs())
    
    def titles_(self):
        for ID in self.IDs():
            x = self.adaptor._property_from_ID(ID, "title")
            check_type(str, x)
            yield x
    def titles(self):
        return tuple(self.titles_())
    def title(self):
        return self._make_single_val(self.titles_())
    
    
    def wclasses_(self):
        for ID in self.IDs():
            x = self.adaptor._property_from_ID(ID, "wcls")
            check_type(str, x)
            yield x
    def wclasses(self):
        return tuple(self.wclasses_())
    def wcls(self):
        return self._make_single_val(self.wclasses_())
    
    
    def pids_(self):
        for ID in self.IDs():
            x = self.adaptor._property_from_ID(ID, "pid")
            check_type(PositiveInt, x)
            yield x
    def pids(self):
        return tuple(self.pids_())
    def pid(self):
        return self._make_single_val(self.pids_())
    
    
    def geometries_(self):
        for ID in self.IDs():
            x = self.adaptor._property_from_ID(ID, "geometry")
            check_type(CollectionWithProps(NonNegativeInt, len=4), x)
            yield x
    def geometries(self):
        return tuple(self.geometries_())
    def geometry(self):
        return self._make_single_val(self.geometries_())
    
    
    def infos_(self):
        for a in zip(self.titles_(), self.wclasses_()): yield a
    def infos(self):
        return tuple(self.infos_())
    def info(self):
        return self._make_single_val(self.infos_())
    
    
    def all_infos_(self):
        for a in zip(self.IDs(), self.titles_(), self.wclasses_(), self.pids_(),
                self.geometries_()): yield a
    def all_infos(self):
        return tuple(self.all_infos_())
    def all_info(self):
        return self._make_single_val(self.all_infos_())
    
    def print_all_infos(self):
        print(*self.all_infos(), sep="\n")
    
    

    def activate(self, all=False):
        if all:
            for ID in self.IDs(): self.adaptor._activate(ID)
        else:
            return self.adaptor._activate(self.ID())
        
    
    def set_prop(self, action: str, prop: str, prop2: str = False, all=False):
        if all:
            for ID in self.IDs():
                self.adaptor._set_prop(ID, action, prop, prop2)
        else:
            return self.adaptor._set_prop(self.ID(), action, prop, prop2)
        
    

    
    def move(self, x=-1, y=-1, width=-1, height=-1, all=False):
        if all:
            for ID in self.IDs(): self.adaptor._move(ID, x, y, width, height)
        else:
            return self.adaptor._move(self.ID(), x, y, width, height)
        
    
    def close(self, all=False):
        if all:
            for ID in self.IDs(): self.adaptor._close(ID)
        else:
            return self.adaptor._close(self.ID())
        
    
    def kill(self, all=False):
        if all:
            for ID in self.IDs(): self.adaptor._kill(ID)
        else:
            return self.adaptor._kill(self.ID())
        
    
    def minimize(self, all=False):
        if all:
            for ID in self.IDs(): self.adaptor._minimize(ID)
        else:
            return self.adaptor._minimize(self.ID())
        
    def maximize(self, all=False):
        sr = self.adaptor.screen_res()
        self.move(0,0,*sr, all=all)
        
    def max_left(self, all=False):
        a,b = self.adaptor.screen_res()
        self.move(0,0,a/2,b, all=all)
    
    def max_right(self, all=False):
        a,b = self.adaptor.screen_res()
        self.move(a/2,0,a/2,b, all=all)
    
    def wait_active(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            reverse=False):
        waited = 0
        while waited <= timeout:
            awin = self._WindowSearch()
            # this WindowSearch Object is refreshed everytime
            if awin in self.IDs():
                if not reverse:
                    time.sleep(pause_when_found)
                    return awin.find()
            elif reverse:
                return True
            if timeout == 0:
                break  # zero length timeout: if not matched go straight to end
            time.sleep(timestep)
            waited += timestep
        return False
    
    def wait_not_active(self, timeout=5, timestep=0.2):
        return self.wait_active(timeout, timestep=timestep, reverse=True)
    
    
    def wait_exist(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            min_wincount=1, max_wincount=None):
        """
        waits until number of matching windows is between min_wincount and
        max_wincount. Returns the IDs of matching windows.
        """
        waited = 0
        while waited <= timeout:
            IDs = self.existing_IDs()
            if len(IDs) >= min_wincount:
                if max_wincount is None or len(IDs) <= max_wincount:
                    # if appropriate number of existing windows was found,
                    # return the IDs
                    time.sleep(pause_when_found)
                    if IDs: return self._FoundWindows(IDs, at_least_one=True)
                    return True
            if timeout == 0:
                break  # zero length timeout, if not matched go straight to end
            time.sleep(timestep)
            waited += timestep
        return False
    
    
    def wait_not_exist(self, timeout=5, timestep=0.2):
        ret = self.wait_exist(timeout, 0, timestep, min_wincount=0,
                max_wincount=0)
        check_type(bool, ret)
        return ret
    
    def wait_exist_activate(self, timeout=5, timestep=0.2):
        found_win = self.wait_exist(timeout=timeout, timestep=timestep,
                pause_when_found=0)
        if found_win:
            found_win.activate()
            found_win.wait_active()
            return found_win
    
    
    def __eq__(self, other):
        if isinstance(other, WindowObject):
            return set(self.IDs()) == set(other.IDs())
        if isinstance(other, PositiveInt):
            return other == self.ID()
        if isinstance(other, str):
            return self.title() == other
        return NotImplemented
    
    def __hash__(self):
        if self.num == 0: return 0
        return max(self.IDs())
    
    def __contains__(self, item):
        if isinstance(item, PositiveInt):
            return item in self.IDs()
        if isinstance(item, WindowObject):
            return item.ID() in self.IDs()
        if isinstance(item, str):
            for t in self.titles_():
                if item in t: return True
            return False
        return NotImplemented
        



class WindowSearch(AdditionContainer.Addend, WindowObject):
  
    def find(self):
        return self._FoundWindows(self)
    
    def update_properties(self, **kwargs):
        new_kwargs = self.creation_kwargs.copy()
        new_kwargs.update(kwargs)
        return self._WindowSearch(*self.creation_args,**new_kwargs)
    
    def __init__(self, *args, adaptor, **kwargs):
        self.adaptor = adaptor
        self.creation_args = args
        self.creation_kwargs = kwargs
        self.init(*args, **kwargs)
    
    def init(self, title_or_ID=None, loc=None, limit=None, **properties):
        check_type(PositiveInt, limit, allowed=(None,))
        self.location = loc
        self.fixed_IDs = None
        if loc is not None:
            if properties or title_or_ID or limit:
                raise SyntaxError("Parameter loc cannot be combined with "
                                  "other parameters.")
        else:
            self.limit = limit
            if isinstance(title_or_ID, PositiveInt):
                self.fixed_IDs = (title_or_ID,)
            elif isinstance(title_or_ID, CollectionWithProps(PositiveInt)):
                self.fixed_IDs = tuple(title_or_ID)
            elif isinstance(title_or_ID, str):
                properties["title"] = title_or_ID
            elif not title_or_ID:
                if not properties:
                    self.location = "active"
                    # if no parameters specified, use the active window
            else:
                raise TypeError("First parameter title_od_ID: %s\nhas wrong "
                                "type: %s"%(title_or_ID, type(title_or_ID)))
            self._properties = properties
    
    
    def IDs(self):
        if self.location and not self.fixed_IDs:
            return (self.adaptor._ID_from_location(self.location),)
        
        else:
            winlist = None
            if self.fixed_IDs:
                winlist = set(ID for ID in self.fixed_IDs if
                    self.adaptor.id_exists(ID))
            
            for prop, prop_val in self._properties.items():
                matching_ids = set(
                        self.adaptor._IDs_from_property(prop, prop_val))
                if winlist is None:
                    winlist = matching_ids
                else:
                    winlist &= matching_ids  # make intersection
                if winlist is set():
                    break
            out = tuple(winlist) if winlist else tuple()
            if self.limit: out = out[:self.limit]
        return out
    
    def existing_IDs(self):
        return self.IDs()
    
    
    # the following redefinitions are necessary because this way,
    # the self.IDs() search will only be executed once.
    def infos_(self):
        return WindowObject.infos_(self.find())
    
    def all_infos_(self):
        return WindowObject.all_infos_(self.find())
    
    def wait_num_change(self, *args, **kwargs):
        return self.find().wait_num_change(*args,**kwargs)




class WindowSearchContainer(AdditionContainer, WindowSearch,
        basic_class = WindowSearch):
    
    def IDs(self):
        ids = set()
        for winsearch in self.members: ids |= set(winsearch.IDs())
        # create the union of all found window IDs
        return tuple(ids)



class FoundWindows(WindowObject):
    
    
    def __init__(self, *args, adaptor, at_least_one=False, **kwargs):
        self.adaptor = adaptor
        if len(args) == 1 and not kwargs and isinstance(args[0], WindowSearch):
            WinSearch_instance = args[0]
            if WinSearch_instance.adaptor is not self.adaptor: raise TypeError
            self.winsearch_object = WinSearch_instance
            # reuse the WindwoSearch object
        else:
            self.winsearch_object = self._WindowSearch(*args, **kwargs)
            # this will initialize instance attributes according to
            # WindowSearch init method.
        self.found_IDs = self.winsearch_object.IDs()
        if not self.found_IDs:
            self.found_IDs = ()
            if at_least_one:
                raise WindowNotFoundError(
                        "\nCould not find windows of specified "
                        "properties. Please use WindowSearch / "
                        "WindowSearch class instead.")
    
    def IDs(self):
        # careful: these IDs might not be existing any more
        return self.found_IDs
    
    def update(self):
        self.found_IDs = self.winsearch_object.IDs()
        
    def update_parameter(self,**kwargs):
        new_winsearch = self.winsearch_object.update_properties(**kwargs)
        return new_winsearch.find()
    
    def find(self):
        return self.winsearch_object.find()
    
    def existing_IDs(self):
        return tuple(ID for ID in self.IDs() if self.adaptor.id_exists(ID))
    
    def remove_non_existing_IDs(self):
        self.found_IDs = self.existing_IDs()
    
    
    def wait_active(self, timeout=5, pause_when_found=0.05, timestep=0.2):
        if self.found_IDs:
            return super().wait_active(timeout, pause_when_found, timestep)
        return self.winsearch_object.wait_active(timeout, pause_when_found, timestep)
    
    def wait_exist(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            min_wincount=1, max_wincount=None):
        if self.num >= min_wincount:
            # this means that this instane of FoundWindows contains
            # enough window IDs to theoretically satisfy the condition
            return super().wait_exist(timeout, pause_when_found, timestep,
                    min_wincount, max_wincount)
            # raise ValueError("FoundWindows does not contain enough IDs "
            #                "to satisfy condition.")
        # if this FoundWindow instance does not contain enough windows,
        # then just use the windowsearch used to define this instance
        # this way we can write win("title").wait_exist() even if the title
        # does not yet exist. Instead fo win.Search("title").wait_exist()
        return self.winsearch_object.wait_active(timeout, pause_when_found, timestep)
    
    
    def wait_num_change(self, num_change, timeout=5, pause_when_found=0.05,
            timestep=0.2):
        check_type(int, num_change)
        kwargs = {}
        if num_change >= 0:
            kwargs["min_wincount"] = self.num + num_change
        if num_change <= 0:
            kwargs["max_wincount"] = self.num + num_change
        windows_after = self.winsearch_object.wait_exist(timeout, pause_when_found,
                timestep, **kwargs)
        if windows_after is not False:
            if num_change >= 0:
                return windows_after - self
            return self - windows_after
        return False
    
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self._FoundWindows(set(self.IDs()) | set(other.IDs()))
        return NotImplemented
    __or__ = __add__
    
    
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self._FoundWindows(set(self.IDs()) - set(other.IDs()))
        return NotImplemented
    # def __rsub__(self, other):
    #     if isinstance(other, self.__class__):
    #         return other.__sub__(self)
    #     return NotImplemented
    
    def __and__(self, other):
        if isinstance(other, self.__class__):
            return self._FoundWindows(set(self.IDs()) & set(other.IDs()))
        return NotImplemented
    
    
    def __repr__(self):
        return "%s with window ID(s) %s>"%(super().__repr__()[:-1], self.IDs())
