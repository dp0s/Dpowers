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
from .adaptor_classes import AdaptorBase, AdaptionError
from ..arghandling import check_type, ArgSaver
from .dependency_testing import BackendDependencyError, import_adapt_module, DependencyManager
import warnings

class Backend:
    
    def __repr__(self):
        s = f"<Backend('{self.main_info}'"
        if self.method_infos:
            s += f", {self.method_infos})"
        s += f") for {self.adaptorcls.__name__}>"
        return s
    
    def __str__(self):
        s = str(self.main_info)
        if self.method_infos:
            s += f", {self.method_infos}"
        return s
    
    def __info__(self):
        return self.adaptorcls, self.main_target_space, \
            self.method_target_spaces
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__info__() == other.__info__()
        return NotImplemented
    
    def __hash__(self):
        return hash(str(self.__info__()))
    
    def show_target_spaces(self):
        if self.method_infos: return self.method_target_spaces
        return self.main_target_space
    
    
    def __init__(self, adaptorclass=None, main_info=None, method_infos={}):
        if not issubclass(adaptorclass, AdaptorBase): raise TypeError
        self.adaptorcls = adaptorclass
        self.dependency_folder = adaptorclass.dependency_folder
        self.main_target_space = None
        self.method_target_spaces = {}
        self.main_info = None  # will be set in update method
        self.method_infos = {}  # will be set in update method
        self.manager = None #set as soon as module was imported
        self.update_target_spaces(main_info, method_infos)
    
    def update_target_spaces(self, main_info=None, method_infos={}):
        main_info, method_infos = self._resolve_arguments(main_info,
                method_infos)
        for name in method_infos:
            if name not in self.adaptorcls.adaptionmethod_names:
                raise NameError(f"Non-valid name for adaptionmethod of class "
                                f"{self.adaptorcls}: {name}.")
            check_type((str, list, tuple), method_infos[name])
        if main_info is not None:
            check_type((str, list, tuple), main_info)
            self.main_target_space, self.main_info = self.get_targetspace(
                    main_info)
        for name in self.adaptorcls.adaptionmethod_names:
            if name in method_infos:
                m = method_infos[name]
                r1, r2 = self.get_targetspace(m)
                self.method_target_spaces[name] = r1
                self.method_infos[name] = r2
            elif self.main_target_space is not None:
                self.method_target_spaces[name] = self.main_target_space
    # note: after using update_target_space (giving info arguments), the
    # self.method_target_spaces will contain all method names. while the
    # self.method_infos dict will only contain those infos explicitly  given.
    # This is why you should use  exactly the following expressions to query:
    # self_or_cls.method_target_spaces.get(name) and
    # self_or_cls.method_infos.get(name,self_or_cls.main_info)
    
    def refresh_target_spaces(self):
        return self.update_target_spaces(self.main_info, **self.method_infos)
    
    
    def _resolve_arguments(self, main_info, method_infos):
        old1, old2 = main_info, method_infos
        for _ in range(50):
            new1, new2 = self._find_arguments(old1, old2)
            if new1 == old1 and new2 == old2: break
            old1, old2 = new1, new2
        else:
            raise RecursionError
        return new1, new2
    
    def _find_arguments(self, main_info, method_infos):
        # returns the resolved main_info, method_infos pair
        if isinstance(main_info, self.__class__):
            new1, new2 = main_info.main_info, main_info.method_infos
        elif isinstance(main_info, ArgSaver):
            if len(main_info.args) == 1:
                new1 = main_info.args[0]
            elif len(main_info.args) == 0:
                new1 = None
            else:
                raise ValueError("Argsaver object has too many postional args.")
            new2 = main_info.kwargs
        else:
            return self._resolve_name(main_info), {k: self._resolve_name(v) for
                k, v in method_infos.items()}
        ret2 = new2.copy()
        ret2.update(method_infos)
        return new1, ret2
    
    def _resolve_name(self, obj):
        if isinstance(obj, (list, tuple)): return obj
        for _ in range(50):
            try:
                obj = self.adaptorcls.added_backend_names[obj]
            except KeyError:
                break
        else:
            raise RecursionError
        return obj
    
    @property
    def pydependencies(self):
        if self.manager is None: return
        return self.manager.pydependencies

    @property
    def shelldependencies(self):
        if self.manager is None: return
        return self.manager.shelldependencies
    
    @property
    def dependencies(self):
        if self.manager is None: return
        return self.manager.dependencies
    
    def get_targetspace(self, info):
        if isinstance(info, str):
            # TODO: add option to give full path of module instead
            module_name = ".adapt_" + info
            module_location = self.adaptorcls.__module__
            module_full_name = module_location + module_name
            try:
                mod, manager = import_adapt_module(module_full_name,
                        self.dependency_folder)
            except Exception as e:
                if isinstance(e, BackendDependencyError): raise
                raise AdaptionError from e
            self.manager = manager
            return mod, info
        elif isinstance(info, (list, tuple)):
            # this is usueful to give a list of possible backends. If one
            # fails to import, the next one is tried.
            last_error = None
            for subinfo in info:
                try:
                    ret_tuple = self.get_targetspace(subinfo)
                except AdaptionError as e:
                    this_error = e.__cause__
                    if last_error: this_error.__cause__ = last_error
                    last_error = this_error
                    continue
                else:
                    return ret_tuple
            raise AdaptionError from last_error
        # this way, all the errors that lead here, will be visible.
        else:
            raise TypeError(f"Require string, but got {info}.")