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



import inspect, functools, types, os, pkgutil, warnings
from ..baseclasses import KeepInstanceRefs, iter_all_vars
from ..arghandling import (check_type, remove_first_arg, ArgSaver)
from ..platform import PlatformChecker
from types import FunctionType
from collections import defaultdict
from .dependency_testing import DependencyManagerBase, InstallInstruction
from abc import ABC

# also see the IMPORTS AT THE END OF THIS FILE. (avoiding circular import)


class AdaptionError(Exception):
    pass

def _get_AdaptionFuncPlaceholders(cls):
    return set(iter_all_vars(cls, lambda obj: hasattr(obj, "_placeholder")))
    
    

class AdaptorBase(KeepInstanceRefs):
    backend_defaults = None  # set in first level subclass
    # adapt_on_first_use = False
    autoadapt_active = False
    dependency_folder = None  # set in first level subclass
    _subclass_level = 0
    _first_level_subclass = None
    adaptionmethod_names = set()
    baseclass = True
    AdaptiveClass = None
    _primary_instances = dict()
    DependencyManager = None
    
    
    class PlatformChecker(PlatformChecker):
        pass
    
    
    def __init_subclass__(cls):
        cls._subclass_level += 1
        cls.__visible_module__ = None
        cls.__visible_name__ = None
        amethod_names = _get_AdaptionFuncPlaceholders(cls)
        if amethod_names:
            # this means that this subclass can actually create instances
            if cls._subclass_level < 2:
                raise SyntaxError("First-level Subclass of AdaptorBase is  "
                                  "not allowed to have adaptionmethods.")
            cls.adaptionmethod_names = amethod_names
                #this will inherit names already defined
            #cls.backend_classes = None
            cls.added_backend_names = {}
            if "baseclass" not in vars(cls):
                cls.baseclass = False
                cls.AdaptiveClass = type("AdaptiveClass",
                        (AdaptiveClass,), dict(adaptor_class=cls))
                c = cls._first_level_subclass
                add = f"Subclass of :class:`{c.__module__}.{c.__name__}`."
                doc = cls.__doc__ if cls.__doc__ else ""
                cls.__doc__ = doc + "\n\n    " + add
        elif cls._subclass_level == 1:
            cls._first_level_subclass = cls
            cls.DependencyManager = type("DependencyManager",
                    (DependencyManagerBase,),{})
            
                
            
    
    def __init__(self, main_info=None, *, group="default", _primary_name=False,
            **method_infos):
        """
        Usually, you do not need to create Adaptor instances yourself as
        a default instance is already available for each subclass (see
        below).
       
        
        :param str main_info: Name of the backend to be used, passed on to
            :func:`adapt`.
        :param str group: Name of the instance group to which the new
            instance will belong.
        :param _primary_name: Used only for internal documentation purposes. It
            allows specifiying the primary/default instance for each instance group.
        :param method_infos: Passed on to :func:`adapt`.
        
        
        If the *main_info* and/or *method_infos* parameter is given, the new
        instance is immediately adapted using its :func:`adapt` method.
        
        If neither *main_info* nor *method_infos* is specified (default),
        and :attr:`Adpator.autoadapt_active` is ``True``,
        choose the default backend according to the instance group and
        `Dpowers.default_backends.py
        <https://github.com/dp0s/Dpowers/tree/master/Dlib/Dpowers
        /default_backends.py>`_.
        
        Otherwise an unadapted instance is created.
        
        """
        
        cls = self.__class__
        super().__init__()
        
        check_type((str, int), group, allowed=(None,))
        self.primary = False
        self.instance_group = group
        
        if _primary_name is not False:
            if group is None: raise ValueError
            prim_inst = self.get_primary_instance()
            if prim_inst:
                raise ValueError(f"Primary instance for this instance group "
                                 f"already set:\n{prim_inst}")
            # the following is a way of conditionally subclassing:
            self.creation_name = _primary_name
            self.primary = True
            self._primary_instances[self.creation_name]=self
            if group == "default":
                self.__doc__ = f"Default instance of {cls.__name__} class.\n\n"
                self.__doc__ += self._create_import_instr(self.creation_name)
        self.backend = Backend(cls)
        
        for name in self.adaptionmethod_names:
            placeholder = getattr(cls, name)._placeholder
            amethod = AdaptionMethod(placeholder, self)
            setattr(self, name, amethod)
        
        
        if main_info or method_infos:
            if group not in ("default", None): raise ValueError
            self.instance_group = None
            self.adapt(main_info, **method_infos)
        elif self.autoadapt_active and self.instance_group is not None:
            self.adapt()
    
    
    
    def adaptionmethods(self):
        return tuple(getattr(self, name) for name in self.adaptionmethod_names)
    
    def adapt(self, main_info=None, *, raise_error=True,
            require_backend=True, **method_infos):
        """Choose the backend for this Adaptor instance. If neither
        *main_info* nor *method_infos* is specified, the
        default backend for this instance group is selected, as defined in
        the module `Dpowers.default_backends.py
        <https://github.com/dp0s/Dpowers/tree/master/Dlib/Dpowers
        /default_backends.py>`_.
        
        :param str main_info: Name of the backend to be used.
        :param bool raise_error: If set to ``False``, exceptions caused
            during backend import are suppressed. A warning is printed instead.
        :param bool require_backend: If set to ``True`` (default), a
            ``ValueError`` will be raised if no default backend could be
            found.
        :param method_infos: Explanation to be added    .
        :return: - The module object of the backend's adapt_*.py file.
                 - ``False`` if an exception occurs but is suppressed (see
                   parameters *raise_error* and *require_backend*).
        :raises:
            - ``Dpowers.AdaptionError`` if there is an exception during
              importing the backend.
            - ``ValueError`` if used without arguments and no default backend
              could be found (you can disable this via *require_backend=False*).
            
        """
        try:
            if isinstance(main_info, Backend):
                backend = main_info
                if method_infos: backend.update_target_spaces(None, method_infos)
            else:
                if main_info is None and not method_infos:
                    main_info = self.get_from_backend_source()
                backend = Backend(self.__class__, main_info, method_infos)
        except AdaptionError as e:
            if raise_error: raise
            text = f"Encountered an Exception trying to adapt\n{self}\n"
            for _ in range(10):
                if str(e):
                    text += type(e).__name__ + ": " + str(e) + "\n"
                e = e.__cause__
                if e is None: break
                text += "caused by\n"
            warnings.warn(text)
            return False
        if not backend:
            if require_backend:
                raise ValueError("Given backend information not "
                            "valid and none found in default backends.")
            return False
        self.backend = backend
        for amethod in self.adaptionmethods(): amethod.set_target()
        return backend.show_target_spaces()
        
    
    def __repr__(self):
        r = super().__repr__()[:-1]
        if self.primary:
            r += f" with creation_name {self.creation_name}, " \
                 f"primary instance of group"
        else:
            r += ", instance group:"
        r += " '" + str(self.instance_group) + "', backend: " + str(
                self.backend) + ">"
        return r
    
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__): return NotImplemented
        return self.backend == other.backend
        
    @property
    def is_adapted(self):
        return bool(self.backend)
    
    @classmethod
    def deactivate_autoadapt(cls):
        cls.autoadapt_active = False
    
    @classmethod
    def activate_autoadapt(cls):
        ### TODO: activate_autoadapt and exception handling.
        cls.autoadapt_active = True
    
    
    @classmethod
    def _adapt_all(cls, omit_adapted_inst=False, raise_error=True,
            backend_source=None):
        for inst in cls.get_instances():
            if inst.is_adapted and omit_adapted_inst: continue
            bakcend_info = inst.get_from_backend_source(
                    backend_source=backend_source)
            inst.adapt(bakcend_info, raise_error=raise_error,
                    require_backend=False)
    
    @classmethod
    def adapt_all(cls, *args, **kwargs):
        cls._adapt_all(*args, **kwargs)
        for subcls in cls.__subclasses__(): subcls.adapt_all(*args, **kwargs)
    
    
    @classmethod
    def check_adapted(cls, raise_error=True, warn=True):
        text = "The following instance is not adapted: "
        missing_inst = []
        for subcls in [cls] + cls.__subclasses__():
            for inst in subcls.get_instances():
                if not inst.is_adapted:
                    if raise_error: raise ValueError(text + str(inst))
                    if warn: warnings.warn(text + str(inst))
                    missing_inst.append(inst)
        return missing_inst
    
    
    @classmethod
    def set_default_backends(cls, module_or_class, evaluate_platform = False):
        if not evaluate_platform: cls.backend_defaults = module_or_class
        if isinstance(evaluate_platform, dict):
            platform_info = evaluate_platform
        else:
            platform_info = cls.PlatformChecker().val_dir
        value = None
        for condition_name, obj in vars(module_or_class).items():
            if isinstance(obj, type):
                state = platform_info.get(condition_name, False)
                if state: value = obj
        cls.backend_defaults = value
        
    
    
    @classmethod
    def update_group_backend(cls, apply=True, **new_group_infos):
        if not hasattr(cls, "adaptionmethod_names"): raise SyntaxError
        for group, backend_info in new_group_infos.items():
            x = getattr(cls.backend_defaults, cls.__name__)
            setattr(x, group, backend_info)
            if apply:
                for inst in cls._get_group_instances(group): inst.adapt()
    
    
  
    @classmethod
    def _get_group_instances(cls, group_or_instance="default"):
        group = group_or_instance.instance_group if isinstance(
                group_or_instance, cls) else group_or_instance
        check_type((str, int), group)
        for instance in cls.get_instances():
            if instance.instance_group == group: yield instance
    
    @classmethod
    def _get_primary_instance(cls, group_or_instance="default"):
        for instance in cls._get_group_instances(group_or_instance):
            if instance.primary is True: return instance
        return None
    
    @classmethod
    def _get_from_backend_source(cls, group_or_instance="default",
            Adaptor_class_or_name=None, backend_source=None):
        if backend_source is None: backend_source = cls.backend_defaults
        if Adaptor_class_or_name is None:
            Adaptor_subclass_name = cls.__name__
        elif issubclass(Adaptor_class_or_name, cls):
            Adaptor_subclass_name = Adaptor_class_or_name.__name__
        else:
            Adaptor_subclass_name = Adaptor_class_or_name
        check_type(str, Adaptor_subclass_name)
        try:
            subclass_info_class = getattr(backend_source, Adaptor_subclass_name)
        except AttributeError:
            return
        if group_or_instance is None:
            raise ValueError
        elif isinstance(group_or_instance, cls):
            group = group_or_instance.instance_group
        else:
            group = group_or_instance
        check_type(str, group)
        try:
            main_info = getattr(subclass_info_class, group)
        except AttributeError:
            try:
                main_info = subclass_info_class.default
                #if no backend for this instance group specified, use the
                #default one
            except AttributeError:
                return  # it's ok to return main_info as None
        check_type((str, tuple, list, Backend, ArgSaver, dict), main_info)
        return main_info
    
    def get_group_instances(self):
        return self._get_group_instances(self.instance_group)
    
    def get_primary_instance(self):
        return self._get_primary_instance(self.instance_group)
    
    def get_from_backend_source(self, backend_source=None):
        return self._get_from_backend_source(self.instance_group,
                backend_source=backend_source)
    
    @classmethod
    def _iter_subclasses(cls):
        yield cls
        for subclass in cls.__subclasses__():
            for subcls in subclass._iter_subclasses(): yield subcls
    
    @classmethod
    def iter_subclasses(cls, ignore_baseclasses=True):
        for subcls in cls._iter_subclasses():
            if not (ignore_baseclasses and subcls.baseclass): yield subcls
    
    @classmethod
    def backend_names(cls):
        if cls.baseclass: raise TypeError
        path = os.path.dirname(inspect.getfile(cls))
        for submodule in pkgutil.iter_modules([path]):
            #print(submodule)
            name = submodule[1]
            if not name.startswith("adapt_"):
                continue
            yield name[6:]
            
    @classmethod
    def find_modules(cls):
        for name in cls.backend_names():
            yield cls.__module__ + ".adapt_" + name
        
            
    @classmethod
    def backend_dict(cls, check=True):
        # use check=False if you don't need to know if the dependency is
        # actually available on this system.
        dependency_dict = defaultdict(list)
        for subclass in cls.iter_subclasses():
            for module_name in subclass.find_modules():
                manager = cls.DependencyManager.get_module_dependencies(
                        module_name, check)
                dependency_dict[subclass].append(manager)
        return dependency_dict
    
    @classmethod
    def install_instructions(cls, as_str=True):
        global_instructions = InstallInstruction()
        for subcls, managerlist in cls.backend_dict(check=False).items():
            for m in managerlist:
                if m is None: continue
                for d in m.dependencies:
                    global_instructions.update(d.install_instructions[''])
        if as_str: return str(global_instructions)
        return global_instructions
    
    @classmethod
    def _print_all_infos(cls, check=True):
        global_instructions = InstallInstruction()
        for subclass in cls.iter_subclasses():
            print("___________________________________________")
            print("subclass:", subclass)
            path = os.path.dirname(inspect.getfile(subclass))
            for submodule in pkgutil.iter_modules([path]):
                name = submodule[1]
                if not name.startswith("adapt_"):
                    continue
                print("backend:", name[6:])
                full_name = subclass.__module__ + "." + name
                # mod=sys.modules[subclass.__module__+"."+name]
                manager = cls.DependencyManager.get_module_dependencies(
                        full_name,
                        perform_check=check)
                for d in manager.dependencies:
                    print(d)
                    if check:
                        error = d.error
                        if not error: continue
                        print("error:",d.error)
                    global_instructions.update(d.install_instructions[''])
            for i in subclass.get_instances():
                print("")
                print("instance: ", i)
                if i.primary:
                    print("defined in:", i.creation_module)
                    print("on line:", i.creation_line)
            print("")
            print("")
        if global_instructions: print(global_instructions)

    @classmethod
    def _create_import_instr(cls, name):
        doc =  "How to import::\n\n\tfrom Dpowers import "+name
        default_backends = cls._get_from_backend_source()
        if default_backends is not None:
            doc += "\n\n\t# choose the default backend for your system:"
            doc += f"\n\t{name}.adapt()"
        doc += "\n\n\t# alternatively, choose one of the following " \
               "backends:"
        for backend_name in cls.backend_names():
            doc += f"\n\t{name}.adapt('{backend_name}')"
        install_instr = cls.install_instructions()  # this works
        # already because it is a classmethod
        if install_instr:
            doc += f"\n\n\nHow to install dependencies for available backends::" \
                   f"\n\n\t>>> print({name}.install_instructions())"
            for line in str(install_instr).split("\n"):
                doc += f"\n\t{line}"
        doc+= "\n\n"
        return doc
    
    @classmethod
    def _set_effective_paths(cls, globals, modname, create_docs=True):
        # a function to create effective paths for documentation purposes
        items = globals.items()
        for subcls in cls.iter_subclasses():
            try:
                for name, obj in items:
                    if obj is subcls:
                        subcls.__visible_module__ = modname
                        subcls.__visible_name__  = name
                        subcls.__visible_fullname__ = modname + "." + name
                        break
            except:
                pass
            finally:
                if create_docs: subcls.AdaptiveClass._create_subclass_docs()



from .backend_class import Backend
from .adaptive_class import AdaptiveClass
from .adaption_method import AdaptionMethod