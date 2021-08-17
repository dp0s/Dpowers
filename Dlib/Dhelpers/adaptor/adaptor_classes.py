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



### TODO: activate_autoadapt and exception handling.
import importlib
import inspect, functools, types, os, pkgutil, warnings
from ..baseclasses import RememberInstanceCreationInfo, KeepInstanceRefs
from ..arghandling import (check_type, remove_first_arg, ArgSaver)
from types import FunctionType
from collections import defaultdict

class AdaptionError(Exception):
    pass



def adaptionmethod(target_name=None, require=False):
    """this is a decorator to turn methods into adaptionmethods"""
    if isinstance(target_name, FunctionType):
        assert require is False
        func = target_name
        # if target_name is callable that means that @adaptionmethod was used
        #  without argument. in this case, target_name is actually the
        # decorated method, and we directly return the result of decoration
        func._placeholder = AdaptionFuncPlaceholder(cls_func=func)
        return func
    elif target_name is None or isinstance(target_name, str):
        def decorator(func):
            placeholder = AdaptionFuncPlaceholder(func, target_name, require)
            func._placeholder = placeholder
            return func
        return decorator
    raise TypeError


class AdaptionFuncPlaceholder:
    def __init__(self, cls_func, target_name=None, require_target=False):
        cls_func.target_modifier = self.target_modifier
        cls_func.adaptive_property = self.adaptive_property
        self.cls_func = cls_func
        self.__name__ = cls_func.__name__
        self.target_name = self.__name__ if target_name is None else target_name
        self.target_modifier_func = None
        self.require_target = require_target
        self.modifier_argnum = None
        self.__signature__ = inspect.signature(cls_func)
        self.coupled_attrs = {}
    
    # def __call__(self, adaptioninstance, *args, **kwargs):
    #     """ Usage example: HookAdaptor.keyb(instance,*args,**kwargs) instead
    #     of instance.keyb(*args,**kwargs)"""
    #     check_type(AdaptorBase, adaptioninstance)
    #     amethod = getattr(adaptioninstance, self.__name__)
    #     check_type(AdaptionMethod, amethod)
    #     return amethod(*args, **kwargs)
    
    def target_modifier(self, func):
        """This is a decorator to specify a function as target_modifer."""
        if not callable(func): raise TypeError
        self.target_modifier_func = func
        self.modifier_argnum = len(inspect.signature(func).parameters)
        if not (2 <= self.modifier_argnum <= 3):
            raise SyntaxError("2 or 3 parameters required for target_modifier"
                              "func: self, target(, adaptionmethod)")
        if func.__defaults__ is not None:
            raise SyntaxError("""target_modifer func must not have any
            default argument values.""")
        return func
    
    def adaptive_property(self, name, default=None, ty=None):
        self.coupled_attrs[name] = (default, ty)
        custom = "_custom_" + name
        backend = "_backend_" + name
        def func(adaptor_inst):
            try:
                custom_val = getattr(adaptor_inst, custom)
                if custom_val is not None: return custom_val
            except AttributeError:
                pass
            try:
                backend_val = getattr(adaptor_inst, backend)
            except AttributeError:
                pass
            else:
                if backend_val not in (None, NotImplemented): return backend_val
            if default == NotImplementedError:
                raise NotImplementedError(f"No value for attribute {name} of "
                              f"{adaptor_inst} found.")
            return default
        func.__name__ = name
        func = property(func)
        @func.setter
        def func(adaptor_inst,val):
            check_type(ty, val, allowed=(None,False,True))
            setattr(adaptor_inst,custom,val)
        return func





        

class AdaptionMethod:
    def __init__(self, placeholder, Adaptor_instance):
        check_type(AdaptionFuncPlaceholder, placeholder)
        check_type(AdaptorBase, Adaptor_instance)
        self.placeholder = placeholder
        self.cls_func = placeholder.cls_func
        self.coupled_attrs = placeholder.coupled_attrs
        functools.update_wrapper(self, self.cls_func)
        # this will copy __doc__, __name__ and __module__, as well as signature
        self.Adaptor_instance = Adaptor_instance
        self.__self__ = Adaptor_instance
        self.backend_info = None
        self.target_space = None
        self.dependency_dict = None
        self.target = None
        self.target_name = placeholder.target_name
        self.target_modifier = placeholder.target_modifier_func
        self.require_target = placeholder.require_target
        self.target_signature = None
        self.target_param_num = None
        
        self.__signature__ = remove_first_arg(self.cls_func)
        
        # print(self.__name__, self.signature, self.signature_to_pass)
        
        self._called_args = None
        self._called_kwargs = None
    
    
    
    def adapt(self, backend_info):
        backend = self.Adaptor_instance.backend
        name = self.__name__
        backend.update_target_spaces(method_infos={name: backend_info})
        self.set_target()
        return self.target_space
    
    
    def __call__(self, *args, **kwargs):
        self._called_args = args
        self._called_kwargs = kwargs
        # logging.info("  Method %s of %s called from:\n%s%s", self.__name__,
        #       self.Adaptor_instance.__class__.__name__,
        #      *traceback.format_stack(limit=3)[:2])
        if not self.Adaptor_instance.is_adapted:
            # this will automatically adapt the Adaptor_instance if
            # adapt_on_first_use is True
            raise AdaptionError("No backend chosen for "
                                "following adaptor:\n%s"%self.Adaptor_instance)
        try:
            ret = self.cls_func(self.Adaptor_instance, *args, **kwargs)
        except TypeError as e:
            if str(e).endswith("object is not callable") and self.target in (
                    None, NotImplemented):
                raise NotImplementedError("target of adaptionmethod %s is "
                                    "%s."%(self.__name__, self.target))
            else:
                raise
        self._called_args = None
        self._called_kwargs = None
        return ret
    
    # Usual execution frames for AdaptionMethods:
    #  __call__ ( saves arguments)
    # --> cls_func (=function decorated with @adaptionmethod)
    # --> target_with_args (can automatically pass arguments)
    # --> target
    
    def target_with_args(self):
        if self.target_param_num == 0: return self.target()
        if self._called_args is None:
            raise SyntaxError("""target_with_args() called from outside
                                adaptionmethod.""")
        bound = self.__signature__.bind(*self._called_args,
                **self._called_kwargs)
        bound.apply_defaults()
        return self.target(*bound.args, **bound.kwargs)
        
    
    def set_target(self):
        backend = self.Adaptor_instance.backend
        name = self.__name__
        target_space = backend.method_target_spaces.get(name)
        if target_space is None:
            self.target = None
            self.target_space = None
            self.backend_info = None
            return
        self.target_space = target_space
        self.backend_info = backend.get_info(name)
        
        for attr_name, tu in self.coupled_attrs.items():
            default, check_ty = tu
            try:
                attr_obj = getattr(target_space, attr_name)
            except AttributeError:
                attr_obj = NotImplemented
            else:
                if inspect.isclass(check_ty): check_type(check_ty,attr_obj)
            setattr(self.Adaptor_instance,"_backend_" + attr_name,attr_obj)
        
        try:
            target = getattr(target_space, self.target_name)
        except AttributeError:
            if self.require_target:
                raise AdaptionError(f"Required function '{self.__name__}' "
                f"was not found.\ntartget namespace: "
                f" {target_space}\nbackend: {backend}")
            target = NotImplemented
        obj, ty = target, type(target)
        if ty is types.MethodType:
            def turn_to_func(method):
                return lambda *args, **kwargs: method(*args, **kwargs)
            obj = turn_to_func(target)
        if self.target_modifier:
            add = (self,) if self.placeholder.modifier_argnum == 3 else ()
            obj = self.target_modifier(self.Adaptor_instance, obj, *add)
        if obj is not target and callable(target):
            assert callable(obj)
            functools.update_wrapper(obj, target)
        if callable(obj):
            self.target_signature = inspect.signature(obj, follow_wrapped=False)
            self.target_param_num = len(self.target_signature.parameters)
            # print( self.target, self.target_signature, self.signature_to_pass)
        self.target = obj
        return self.target_space
    
    def __repr__(self):
        if self.target is None or self.target is NotImplemented:
            target = str(self.target)
        else:
            try:
                name = self.target.__name__
            except AttributeError:
                name = self.target_name
            try:
                mod = self.target.__module__
            except AttributeError:
                mod = str(self.target_space)
            target = mod + "." + name
        return "%s with target %s>"%(super().__repr__()[:-1], target)


# class AdaptionMethodContainer(AdditionContainer, basic_class=AdaptionMethod):
#     def __call__(self, *args, **kwargs):
#         return functools.reduce(operator.add, tuple(m(*args,**kwargs) for m
#             in self.members))


def _get_AdaptionFuncPlaceholders(cls):
    for name, obj in vars(cls).items():
        if hasattr(obj,"_placeholder"): yield name
    for basecls in cls.__bases__:
        for name in _get_AdaptionFuncPlaceholders(basecls):
            try:
                obj = getattr(cls, name)
            except AttributeError:
                continue
            if hasattr(obj,"_placeholder"): yield name
                

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
    
    
    def __init_subclass__(cls):
        cls._subclass_level += 1
        cls.__visible_module__ = None
        cls.__visible_name__ = None
        l = tuple(_get_AdaptionFuncPlaceholders(cls))
        if l:
            # this means that this subclass can actually create instances
            if cls._subclass_level < 2:
                raise SyntaxError("First-level Subclass of AdaptorBase is  "
                                  "not allowed to have adaptionmethods.")
            cls.adaptionmethod_names = set(l)
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
                
            
    
    def __init__(self, main_info=None, *, group="default", _primary=False,
            **method_infos):
        """
        Usually, you do not need to create Adaptor instances yourself as
        a default instance is already available for each subclass (see
        below).
       
        
        :param str main_info: Name of the backend to be used, passed on to
            :func:`adapt`.
        :param str group: Name of the instance group to which the new
            instance will belong.
        :param _primary: Used only for internal documentation purposes. It
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
        
        if _primary is True:
            if group is None: raise ValueError
            prim_inst = self.get_primary_instance()
            if prim_inst:
                raise ValueError(f"Primary instance for this instance group "
                                 "already set:\n{prim_inst}")
            # the following is a way of conditionally subclassing:
            RememberInstanceCreationInfo.__init__(self)
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
        if self.primary:
            r = RememberInstanceCreationInfo.__repr__(self)[
                :-1] + ", primary instance of group '"
        else:
            r = super().__repr__()[:-1] + ", instance group: '"
        r += str(self.instance_group) + "', backend: " + str(
                self.backend) + ">"
        return r
    
    
    @property
    def is_adapted(self):
        return bool(self.backend)
    
    @classmethod
    def deactivate_autoadapt(cls):
        cls.autoadapt_active = False
    
    @classmethod
    def activate_autoadapt(cls):
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
            return  # it's ok to return main_info as None
        check_type((str, tuple, list, Backend, ArgSaver), main_info)
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
                manager = get_module_dependencies(module_name, check)
                dependency_dict[subclass].append(manager)
        return dependency_dict
    
    @classmethod
    def install_instructions(cls):
        global_instructions = InstallInstruction()
        for subcls, managerlist in cls.backend_dict(check=False).items():
            for m in managerlist:
                for d in m.dependencies:
                    global_instructions.update(d.install_instructions[''])
        return global_instructions
    
    @classmethod
    def print_all_infos(cls, check=True):
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
                manager = get_module_dependencies(full_name,
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
    def _print_sphinx_docs(cls):
            cls.adapt.__doc__ = "Choose the backend for this instance. See " \
                               ":func:`Adaptor.adapt`."
            name = cls._get_primary_instance().creation_name
            print(".. autodata:: Dpowers." + name)
            print("\t:no-value:")
            print(".. autoclass:: Dpowers." + cls.__name__)
            print()
            print("\t.. automethod:: adapt")
            print()
            print(f".. class:: Dpowers.{cls.__name__}.AdaptiveClass")
            print()
            print("\t\tA baseclass to create your own AdaptiveClasses. See \
                :class:`Dpowers.AdaptiveClass`.")
            print()

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
                        break
            except:
                pass
            finally:
                if create_docs: subcls.AdaptiveClass._create_subclass_docs()
            


        
        

wrap = functools.wraps(AdaptorBase.adapt, assigned=())
class AdaptiveClass:
    
    adaptor_class = None
    adaptor = None


    @classmethod
    @wrap
    def adapt(cls, *args, **kwargs):
        if "adaptor" in cls.__dict__:
            #in this case, an adaptor instance was explicitly set for this
            # subclass before
            check_type(cls.adaptor_class, cls.adaptor)
        else:
            # in this case, the adaptor attribute is only inherited -- we
            # need to redefine it to avoid adapting the base class too
            group = None if not args and not kwargs else "default"
            cls.adaptor = cls.adaptor_class(group=group)
        return cls.adaptor.adapt(*args, **kwargs)
        
    @wrap
    def adapt_instance(self, *args, **kwargs):
        self.adaptor = self.adaptor_class()
        return self.adaptor.adapt(*args, **kwargs)
    
    
    @classmethod
    def install_instructions(cls):
        return cls.adaptor_class.install_instructions()


    @classmethod
    def _iter_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield subclass
            for subcls in subclass._iter_subclasses(): yield subcls

    @classmethod
    def _create_doc(cls):
        aclss = cls.adaptor_class
        aclss_ref = ":class:"
        if aclss.__visible_module__ is not None:
            aclss_ref += f"`{aclss.__visible_module__}.{aclss.__visible_name__}`"
        else:
            aclss_ref += f"`{aclss.__module__}.{aclss.__name__}`"
        doc = "Subclass of :class:`Dpowers.AdaptiveClass`.\n\n" \
              f"Adaptor subclass used internally: {aclss_ref}\n\n"
        doc += aclss._create_import_instr(cls.__name__)
        if cls.__doc__: doc += cls.__doc__ + "\n\n"
        doc += f".. data:: adaptor\n\n\t*Class attribute.* An instance of " \
               f"{aclss_ref}, as explained in :attr:`AdaptiveClass.adaptor`.\n\n"
        doc += ".. automethod:: adapt\n\n\tSee :func:`AdaptiveClass.adapt`." \
               " For parameters see :func:`Dpowers.Adaptor.adapt`."
        cls.__doc__ = doc
    
    @classmethod
    def _create_subclass_docs(cls):
        for subcls in cls._iter_subclasses(): subcls._create_doc()


from .backend_class import Backend
from .dependency_testing import BackendDependencyError, DependencyManager, \
    get_module_dependencies, InstallInstruction
