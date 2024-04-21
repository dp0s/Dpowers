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
from Dhelpers.baseclasses import (check_type, AdditionContainer)
from Dhelpers.arghandling import (PositiveInt, CollectionWithProps)

import inspect, time, functools
from abc import ABC, abstractmethod


class WindowNotFoundError(Exception):
    pass


def doc_single(prop):
    def dec(func):
        doc=(f"Returns the {prop} of this window if exactly one "
                "match was found. Returns ``None`` if no match was "
              "found. Raises ``ValueError`` if there was more than one "
                  "matching window.")
        # doc = (f":return: - The {prop} of this window if exactly one "
        #        "match was found. \n \t - ``None`` if no match was "
        #        "found. \n :raise ValueError: If there was more than one "
        #        "matching window.")
        try:
            add = func.__doc__
        except AttributeError:
            pass
        else:
            if add:
                #add = add.replace("\t","")
                #while "  " in add: add = add.replace("  "," ")
                doc += "\n" + add
        func.__doc__ = doc
        return func
    return dec

def doc_multi(prop, no_gen=False):
    def dec(func):
        func.__doc__=(f"Returns a tuple of length :data:`num` containing "
                      f"the {prop} of all found windows.")
        if no_gen is False:
            func.__doc__ += (f" Use :func:`{func.__name__}_gen` to create a "
                      f"generator instead of a tuple.")
        return func
    return dec




class WindowObject(ABC):
    
    @classmethod
    def cached(cls):
        return cls.adaptor.cached()
    
    @classmethod
    def cached_properties(cls):
        return cls.adaptor.cached_properties
    
    @classmethod
    def use_cache(cls, state=True):
        cls.adaptor.use_cache=state
    
    
    #to be set by subclasses:
    adaptor = None
    _FoundWinClass = None
    _WinSearchClass = None
    
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
        """Number (*int*) of windows found to match the given criteria. Equals
            zero if there was no match at all."""
        return len(self.IDs())
    
    
    def __bool__(self):
        # This allows to use if win("test"): do_something
        return bool(self.IDs())
    
    @abstractmethod
    def existing_IDs(self):
        raise NotImplementedError
    
    @doc_single("identification number (*int*)")
    def ID(self):
        return self._make_single_val(self.IDs())
    
    @abstractmethod
    @doc_multi("IDs", no_gen=True)
    def IDs(self):
        raise NotImplementedError
    
    @doc_single("title (*str*)")
    def title(self):
        return self._make_single_val(self.titles_gen())
    @doc_multi("titles")
    def titles(self):
        return tuple(self.titles_gen())
    def titles_gen(self):
        for ID in self.IDs():
            x = self.adaptor.property_from_ID(ID, "title")
            check_type(str, x, allowed=(None,))
            yield x
    
    @doc_single("window class (*str*)")
    def wcls(self):
        return self._make_single_val(self.wclasses_gen())
    @doc_multi("window classes")
    def wclasses(self):
        return tuple(self.wclasses_gen())
    def wclasses_gen(self):
        for ID in self.IDs():
            x = self.adaptor.property_from_ID(ID, "wcls")
            check_type(str, x, allowed=(None,))
            yield x
    
    
    @doc_single("process ID (*int*)")
    def pid(self):
        return self._make_single_val(self.pids_gen())
    @doc_multi("process IDs")
    def pids(self):
        return tuple(self.pids_gen())
    def pids_gen(self):
        for ID in self.IDs():
            x = self.adaptor.property_from_ID(ID, "pid")
            check_type(PositiveInt, x, allowed=(None,))
            yield x
    
    @classmethod
    def screen_res(cls):
        """Returns the screen resolution in pixels as a
            tuple (*screen_width, screen_height*)."""
        return cls.adaptor.screen_res()
    
    def widths_gen(self):
        for geom in self.geometries_gen(): yield geom[2] - geom[0]
    @doc_single("width in pixels (*int*)")
    def width(self):
        return self._make_single_val(self.widths_gen())
    @doc_multi("widths")
    def widths(self):
        return tuple(self.widths_gen())
    
    
    @doc_single("height in pixels (*int*)")
    def height(self):
        return self._make_single_val(self.widths_gen())
    def heights_gen(self):
        for geom in self.geometries_gen(): yield geom[3] - geom[1]
    @doc_multi("heights")
    def heights(self):
        return tuple(self.widths_gen())
    
    
    @doc_single("4 border coordinates")
    def geometry(self):
        """
        The return value is a 4-element tuple containing the window's
        border coordinates as *int* in pixels as follows: (left, top,
        right, bottom) = (Xmin, Ymin, Xmax, Ymax).
        """
        return self._make_single_val(self.geometries_gen())
    def geometries_gen(self):
        for ID in self.IDs():
            x = self.adaptor.property_from_ID(ID, "geometry")
            check_type(CollectionWithProps(int, len=4), x)
            yield x
    @doc_multi("geometries")
    def geometries(self):
        return tuple(self.geometries_gen())
    
    
    @doc_single("2-element tuple (:func:`title`, :func:`wcls`)")
    def info(self):
        return self._make_single_val(self.infos_gen())
    def infos_gen(self):
        for a in zip(self.titles_gen(), self.wclasses_gen()): yield a
    @doc_multi(":func:`info` tuples")
    def infos(self):
        return tuple(self.infos_gen())
    
    
    
    def all_infos_gen(self):
        for a in zip(self.IDs(), self.titles_gen(), self.wclasses_gen(),
                self.pids_gen(), self.geometries_gen()): yield a
    @doc_single("5-element tuple (:func:`ID`, :func:`title`, :func:`wcls`, "
                ":func:`pid`, :func:`geometry`)")
    def all_info(self):
        return self._make_single_val(self.all_infos_gen())
    @doc_multi(":func:`all_info` tuples")
    def all_infos(self):
        return tuple(self.all_infos_gen())
    
    def print_all_infos(self):
        print(*self.all_infos(), sep="\n")
        return self
    
    def close(self, all=False):
        """Closes this window.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
           window matches.
        """
        if all:
            for ID in self.IDs(): self.adaptor.close(ID)
        else:
            return self.adaptor.close(self.ID())
        return self
    
    
    def map(self, all=False):
        if all:
            for ID in self.IDs(): self.adaptor.map(ID)
        else:
            return self.adaptor.map(self.ID())
        return self
    
    def set_prop(self, action: str, prop: str, prop2: str = False, all=False):
        if all:
            for ID in self.IDs():
                self.adaptor.set_prop(ID, action, prop, prop2)
        else:
            return self.adaptor.set_prop(self.ID(), action, prop, prop2)
        return self
    
    
    def kill(self, all=False):
        """Kill (force close) this window.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than
            one  window matches.
        """
        if all:
            for ID in self.IDs(): self.adaptor.kill(ID)
        else:
            return self.adaptor.kill(self.ID())
        return self
    
    def minimize(self, all=False):
        """Minimize this window.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches.
        """
        if all:
            for ID in self.IDs(): self.adaptor.minimize(ID)
        else:
            return self.adaptor.minimize(self.ID())
        return self
    
    def maximize(self, all=False):
        """Maximize this window.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches."""
        sr = self.adaptor.screen_res()
        self.move(0, 0, *sr, all=all)
        return self
    
    def max_left(self, all=False):
        """Maximize this window to the left side of the screen.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches."""
        try:
            self.set_prop("remove", "maximized_horz", prop2="maximized_vert")
        except Exception:
            pass
        a, b = self.adaptor.screen_res()
        self.move(0, 0, a/2, b, all=all)
        return self
    
    def max_right(self, all=False):
        """Maximize this window to the right side of the screen.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches."""
        try:
            self.set_prop("remove", "maximized_horz", prop2="maximized_vert")
        except Exception:
            pass
        a, b = self.adaptor.screen_res()
        self.move(a/2, 0, a/2, b, all=all)
        return self
    
    def move(self, x=-1, y=-1, width=-1, height=-1, all=False):
        """Move and resize this window. Specifying -1 for one of the
        coordinates will keep the current value (default).

        :param int x: New coordinate of left border.
        :param int y: New cordinate of top border
        :param int width: New width of window.
        :param int height: New hight of window.
        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches.
        """
        if all:
            for ID in self.IDs(): self.adaptor.move(ID, x, y, width, height)
        else:
            return self.adaptor.move(self.ID(), x, y, width, height)
        return self
    
    def activate(self, all=False):
        """Activates this window.

        :param all: If set ``True``, apply this command to all found windows.
        :raise ValueError: If *all* is ``False`` (default) and more than one
         window matches.
        """
        if all:
            for ID in self.IDs(): self.adaptor.activate(ID)
        else:
            return self.adaptor.activate(self.ID())
        return self
    
    def wait_active(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            reverse=False):
        """Wait until the specified window is active. If several windows
        are matching, wait until any of them is active.

        :param float timeout: Seconds to wait before returning anyway.
        :param float pause_when_found: Time to sleep after success.
        :param float timestep: Interval how often the condition is checked.
        :return: - The :func:`Win` object for the active window in case of success.
                - ``False`` in case of a timeout.

        """
        waited = 0
        while waited <= timeout:
            awin = self._FoundWinClass()
            # this WindowSearch Object is refreshed everytime
            if awin.ID() in self.IDs():
                if not reverse:
                    time.sleep(pause_when_found)
                    return awin
            elif reverse:
                return True
            if timeout == 0:
                break  # zero length timeout: if not matched go straight to end
            time.sleep(timestep)
            waited += timestep
        return False
    
    def wait_not_active(self, timeout=5, timestep=0.2):
        """Same as :func:`wait_active`, but reversed. It waits until the
        specified window(s) is (are) not active anymore.

        :return: - ``True`` in case of success.
                - ``False`` in case of a timeout.
        """
        return self.wait_active(timeout=timeout, timestep=timestep,
                reverse=True)
    
    
    def wait_exist(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            min_wincount=1, max_wincount=None):
        """Waits until the number of matching windows is between
        *min_wincount* and *max_wincount*. By default, this means at least
        one matching window must exist.

        :param float timeout: Seconds to wait before returning anyway.
        :param float pause_when_found: Time to sleep after success.
        :param float timestep: Interval how often the condition is checked.
        :param int min_wincount: Minimum number of matching windows
            necessary to continue.
        :param max_wincount: Maximum number of matching windows to continue.
            If set to ``None`` (default), there is no maximum.
        :return: - The :func:`Win` object containing all matching windows in case of success.
             - ``False`` in case of a timeout.
        """
        waited = 0
        while waited <= timeout:
            IDs = self.existing_IDs()
            if len(IDs) >= min_wincount:
                if max_wincount is None or len(IDs) <= max_wincount:
                    # if appropriate number of existing windows was found,
                    # return the IDs
                    time.sleep(pause_when_found)
                    if IDs: return self._FoundWinClass(IDs, at_least_one=True)
                    return True
            if timeout == 0:
                break  # zero length timeout, if not matched go straight to end
            time.sleep(timestep)
            waited += timestep
        return False
    
    
    def wait_not_exist(self, timeout=5, timestep=0.2):
        """Wrapper for :func:`wait_exist` with *min_wincount* =
        *max_wincount* = 0.

        :return: - ``True`` in case of success.
                - ``False`` in case of a timeout."""
        ret = self.wait_exist(timeout, 0, timestep, min_wincount=0,
                max_wincount=0)
        check_type(bool, ret)
        return ret
    
    def wait_exist_activate(self, timeout=5, timestep=0.2):
        """Wait until at least one matching window exists and activate it immediately.

        :return: - The :func:`Win` object for the found window.
            - ``False`` in case of timeout or if activate failed.
        """
        found_win = self.wait_exist(timeout=timeout, timestep=timestep,
                pause_when_found=0)
        if found_win:
            found_win.activate()
            return found_win.wait_active(timeout=1)
        return False


class WindowSearch(AdditionContainer.Addend, WindowObject):
    
    # _FoundWinClass and _WinSearchClass are set by
    # init_subclass of FoundWindows
    
    @property
    def adaptor(self):
        return self._FoundWinClass.adaptor
    
    def find(self):
        return self._FoundWinClass(self)
    
    def update_properties(self, **kwargs):
        new_kwargs = self.creation_kwargs.copy()
        new_kwargs.update(kwargs)
        return self.__class__(*self.creation_args, **new_kwargs)
    
    def process_args(self, title_or_ID=None, wcls = None, *, loc=None,
            limit=None, visible=None, selection_func=None, **properties):
        if wcls is not None: properties["wcls"] = wcls
        check_type(int, limit, allowed=(None,))
        self.visible = visible
        self.location = loc
        self.fixed_IDs = None
        if selection_func:
            assert callable(selection_func)
            raise ValueError("selection_func not yet implemented")
        self.selection_func = selection_func
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
            elif isinstance(title_or_ID, (str, CollectionWithProps(str))):
                properties["title"] = title_or_ID
            elif not title_or_ID:
                if not properties:
                    self.location = "active"
                    # if no parameters specified, use the active window
            else:
                raise TypeError("First parameter title_od_ID: %s\nhas wrong "
                                "type: %s"%(title_or_ID, type(title_or_ID)))
            self._properties = properties

    @functools.wraps(process_args)
    def __init__(self, *winargs, **winkwargs):
        self.creation_args = winargs
        self.creation_kwargs = winkwargs
        self.process_args(*winargs, **winkwargs)
    
    def compare_args(self, *winargs,**winkwargs):
        new_instance = self.__class__(*winargs, **winkwargs)
        for attr in ("location", "fixed_IDs"):
            if getattr(self,attr) != getattr(new_instance, attr):
                return False
        for key, val in self._properties.items():
            newval = new_instance._properties.get(key)
            if isinstance(val, CollectionWithProps()):
                val = set(val)
                newval = set(newval)
            if newval != val: return False
        return True
    
    def IDs(self):
        if self.location:
            return (self.adaptor._ID_from_location(self.location),)
        
        winlist = None
        if self.fixed_IDs:
            winlist = set(ID for ID in self.fixed_IDs if
                self.adaptor.id_exists(ID))
        
        for prop, prop_val in self._properties.items():
            if isinstance(prop_val, CollectionWithProps()):
                matching_ids = set()
                for val in prop_val:
                    matching_ids |=  set(self.adaptor.IDs_from_property(prop,
                            val, visible=self.visible))
            else:
                matching_ids = set(self.adaptor.IDs_from_property(prop,
                        prop_val, visible=self.visible))
            if winlist is None:
                winlist = matching_ids
            else:
                winlist &= matching_ids  # make intersection
            if winlist is set(): break
        out = tuple(sorted(winlist))
        l = self.limit
        if l:
            if l > 0:
                out = out[:l]
            elif l < 0:
                out = out[l:]
            else:
                raise ValueError(self.limit)
        # if self.selection_func:
        #     out = tuple(ID for ID in out if self.selection_func(
        #             self._FoundWinClass(ID)))
        return out
    
    
    def check_single(self, win):
        # problem here: we don't know how to check whether win is visible..
        # so self.visible has no effect inside here.
        if isinstance(win, int):
            id = win
        elif isinstance(win,self._FoundWinClass):
            id = win.ID()
        else:
            raise TypeError
        if self.location: return id in self.IDs()
        # in other cases we don't want to run self.IDs() because it scans for
        # all possible matching IDs taking more time
        if self.fixed_IDs and id not in self.fixed_IDs: return False
        for prop, val in self._properties.items():
            winval = self.adaptor.property_from_ID(id, prop)
            if isinstance(val,CollectionWithProps()):
                if winval not in val: return False
            elif winval != val:
                return False
        return True
    
    def existing_IDs(self):
        return self.IDs()
    
    
    
    
    # the following redefinitions are necessary because this way,
    # the self.IDs() search will only be executed once.
    def infos_gen(self):
        return WindowObject.infos_gen(self.find())
    
    def all_infos_gen(self):
        return WindowObject.all_infos_gen(self.find())
    
    def wait_num_change(self, *args, **kwargs):
        return self.find().wait_num_change(*args,**kwargs)

    



class WindowSearchContainer(AdditionContainer, WindowSearch,
        basic_class = WindowSearch):
    
    def IDs(self):
        ids = set()
        for winsearch in self.members: ids |= set(winsearch.IDs())
        # create the union of all found window IDs
        return tuple(sorted(ids))
    
    @property
    def _FoundWinClass(self):
        return self.members[0]._FoundWinClass
    
    def compare_args(self, *winargs,**winkwargs):
        for member in self.members:
            if member.compare_args(*winargs, **winkwargs): return True
        return False

    def check_single(self, win):
        for member in self.members:
            if member.check_single(win): return True
        return False


class FoundWindows(WindowObject):
    """An object of this class represents one or more graphical windows of
    your operating system.
    
    When a new instance of this class is created, a search is
    performed to find all existing windows matching the given parameters.
    Each window is identified by a unique system-wide identification number (
    ID). The matching IDs are saved in ascending order as a static list. Use
    the :func:`IDs` method to see them. All methods below will operate on
    this list of initially found windows.
     
    Two :func:`Win` objects are considered identical if their list
    of :func:`IDs` are identical.
    
    """
    
    def __init_subclass__(cls):
        class Search(WindowSearch):
            pass
        Search.__module__ = __name__
        Search._FoundWinClass = cls
        Search._WinSearchClass = Search
        # winsearch.__init__=functools.wraps(WindowSearch.__init__)(winsearch.__init__)
        cls._FoundWinClass = cls
        cls._WinSearchClass = Search
        cls.Search = Search
        cls._search_activewin = Search()
        base_doc = cls.__base__.__doc__
        if base_doc:
            this_doc = cls.__doc__
            if not this_doc:
                new_doc = base_doc
            else:
                new_doc = this_doc + "\n\n" + base_doc
            new_doc = new_doc.replace("\n  ", "\n")
            cls.__doc__ = new_doc
            
            
    def _signature_def(self, title_or_ID =None, wcls = None, *, pid = None,
            loc = None, at_least_one = False, limit = None, visible = None):
        return
    
    def __init__(self, *winargs, at_least_one = False, **winkwargs):
        """
        :param title_or_ID:
            - A string is interpreted as the title to search for. The string
              can be contained anywhere in the window's title to
              be considered a match.
            - An integer is interpreted as a window ID. Specifying this
              directly will skip the search and all other parameters are hence
              ignored.
        :type title_or_ID: str, int
        :param str wcls: Window class to search for. This must be an exact
                match.
        :param int pid: Process ID of the window to search for.
        :param tuple loc: Specify screen coordinates (*x*,*y*) for this
            parameter to retrieve the top-most window at that location.
            Specifying this will ignore all other parameters.
        :param bool at_least_one: If set to ``True``, check that at least one
            matching window has been found.
        :param int limit: Maximum number of windows to include into the
            window object. If more matching windows exist, only the ones with
            the lowest IDs will be included.
        :param bool visible: If set to True, only visible windows will be
            considered.
        :raise WindowNotFoundError: If *at_least_one* is ``True`` and no
            matching window was found.
        
        In order to find the currently active (i.e. topmost) window,
        simply call this class without parameters::
            
            active_window = Win()
            
        Several different parameters can be
        passed at once to narrow down the search. A window must
        fullfill all specified parameters to be a match::
            
            dpowers_doc_win = Win('Dpowers documentation', 'Navigator.firefox')
            # searches for windows with
            # 'Dpowers documentation' contained in title
            # AND
            # window class is equal to 'Navigator.firefox' (Firefox browser)
            
        In place of passing a single value for the parameters *ID*, *title*,
        *wcls* or *pid*, it is possible to pass a
        list (or tuple or set) of allowed values instead, which will search
        for a wider scope of windows::
        
            dpowers_browser_win = Win('Dpowers documentation',
                ('Navigator.firefox','chromium-browser.Chromium-browser'))
            # searches for windows with
            # 'Dpowers documentation' contained in title
            #   AND
            # (window class is equal to 'Navigator.firefox'
            #  OR window class is equal to 'chromium-browser.Chromium-browser')

        In many cases it is desirable to make sure that exactly one
        matching window is found for each instance to avoid
        confusion. In other cases it might be useful to operate on a
        group of windows simultaneously.
        
        
        .. note:: If a window was initially found and closed in the meantime,
            its ID will still be in the internal list of the :func:`Win` object.
            This can result in an Exception when trying to interact with a
            non-existent window ID. The :func:`update` or
            :func:`remove_non_existing` methods can be used to avoid this
            problem.

        """
        if len(winargs) == 1 and not winkwargs and isinstance(winargs[0], WindowSearch):
            WinSearch_instance = winargs[0]
            if not isinstance(WinSearch_instance, WindowSearchContainer):
                if WinSearch_instance.adaptor is not self.adaptor:
                    raise TypeError
            self.winsearch_object = WinSearch_instance
            # reuse the WindwoSearch object
        elif not winargs and not winkwargs:
            self.winsearch_object = self._search_activewin
        else:
            self.winsearch_object = self._WinSearchClass(*winargs, **winkwargs)
            # this will initialize instance attributes according to
            # WindowSearch init method.
        self.found_IDs = self.winsearch_object.IDs()
        if not self.found_IDs:
            self.found_IDs = ()
            if at_least_one: raise WindowNotFoundError(
                "\nCould not find windows of specified properties. Please "
                "use WindowSearch class instead.")
    
    
    __init__.__signature__ = inspect.signature(_signature_def)
    
    def IDs(self):
        # careful: these IDs might not be existing any more
        return self.found_IDs
    
            
    
    def check(self, *winargs, **winkwargs):
        assert len(self) == 1
        first = winargs[0]
        id = self.ID()
        if isinstance(first, WindowSearch):
            assert not winkwargs
            for obj in winargs:
                if obj.check_single(id): return True
            return False
        search = self._WinSearchClass(*winargs,**winkwargs)
        return search.check_single(id)
    
    def update(self):
        """Re-perform the initial search for matching existing windows and
        update this window object's internal ID list. This removes
        non-existing windows and searches for new matches.
        """
        self.found_IDs = self.winsearch_object.IDs()
        
    def update_parameter(self,**kwargs):
        new_winsearch = self.winsearch_object.update_properties(**kwargs)
        return new_winsearch.find()
    
    def find(self):
        return self.winsearch_object.find()
    
    def existing_IDs(self):
        return tuple(ID for ID in self.IDs() if self.adaptor.id_exists(ID))
    
    def remove_non_existing(self):
        """Cleanse this window object's internal ID list by removing those
        that do not exist anymore."""
        self.found_IDs = self.existing_IDs()
    
    
    def wait_active(self, timeout=5, pause_when_found=0.05, timestep=0.2):
        if self.found_IDs:
            return super().wait_active(timeout, pause_when_found, timestep)
        return self.winsearch_object.wait_active(timeout, pause_when_found, timestep)
    
    def wait_exist(self, timeout=5, pause_when_found=0.05, timestep=0.2,
            min_wincount=1, max_wincount=None):
        if self.num >= min_wincount:
            # this means that this instane of WindowFinder contains
            # enough window IDs to theoretically satisfy the condition
            return super().wait_exist(timeout, pause_when_found, timestep,
                    min_wincount, max_wincount)
            # raise ValueError("WindowFinder does not contain enough IDs "
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
            return self._FoundWinClass(set(self.IDs()) | set(other.IDs()))
        return NotImplemented
    __or__ = __add__
    
    
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self._FoundWinClass(set(self.IDs()) - set(other.IDs()))
        return NotImplemented
    # def __rsub__(self, other):
    #     if isinstance(other, self.__class__):
    #         return other.__sub__(self)
    #     return NotImplemented
    
    def __and__(self, other):
        if isinstance(other, self.__class__):
            return self._FoundWinClass(set(self.IDs()) & set(other.IDs()))
        return NotImplemented
    
    
    def __repr__(self):
        return "%s with window ID(s) %s>"%(super().__repr__()[:-1], self.IDs())


    def __getitem__(self, item):
        return self.__class__(self.IDs()[item])
    
    def __iter__(self):
        def iterator():
            for id in self.IDs(): yield self.__class__(id)
        return iterator()
    
    def __len__(self):
        return len(self.IDs())


    def __eq__(self, other):
        if isinstance(other, WindowObject):
            return set(self.IDs()) == set(other.IDs())
        if isinstance(other, PositiveInt): return other == self.ID()
        if isinstance(other, str): return self.title() == other
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
            for t in self.titles_gen():
                if item in t: return True
            return False
        return NotImplemented
