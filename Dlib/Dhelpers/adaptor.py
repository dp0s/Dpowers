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


import importlib, inspect, functools, types, os, pkgutil, sys, logging, \
    traceback, warnings, operator
from .baseclasses import RememberInstanceCreationInfo, KeepInstanceRefs
from .arghandling import (check_type, remove_first_arg, ArgSaver)



class AdaptionError(Exception):
    pass


def adaptionmethod(target_name=None, require=False):
    """this is a decorator to turn methods into adaptionmethods"""
    if callable(target_name):
        # if target_name is callable that means that @adaptionmethod was used
        #  without argument. in this case, target_name is actually the
        # decorated method, and we directly return the result of decoration
        return AdaptionFuncPlaceholder(cls_func=target_name, target_name=None,
                require_target=require)
    elif target_name is None or isinstance(target_name, str):
        # in this case we want to return another decorator to apply to the
        # cls_func:
        return functools.partial(AdaptionFuncPlaceholder,
                target_name=target_name, require_target=require)
    raise TypeError



class AdaptionFuncPlaceholder:
    def __init__(self, cls_func, target_name, require_target):
        self.cls_func = cls_func
        self.__name__ = cls_func.__name__
        self.target_name = self.__name__ if target_name is None else target_name
        self.target_modifier_func = None
        self.require_target = require_target
        self.modifier_argnum = None
        self.__signature__ = inspect.signature(cls_func)
    
    def __call__(self, adaptioninstance, *args, **kwargs):
        """ Usage example: HookAdaptor.keyb(instance,*args,**kwargs) instead
        of instance.keyb(*args,**kwargs)"""
        check_type(AdaptorBase, adaptioninstance)
        amethod = getattr(adaptioninstance, self.__name__)
        check_type(AdaptionMethod, amethod)
        return amethod(*args, **kwargs)
    
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



class AdaptionMethod:
    def __init__(self, placeholder, Adaptor_instance):
        check_type(AdaptionFuncPlaceholder, placeholder)
        check_type(AdaptorBase, Adaptor_instance)
        self.placeholder = placeholder
        self.cls_func = placeholder.cls_func
        functools.update_wrapper(self, self.cls_func)
        # this will copy __doc__, __name__ and __module__, as well as signature
        self.Adaptor_instance = Adaptor_instance
        self.__self__ = Adaptor_instance
        self.impl_info = None
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
    
    
    
    def adapt(self, impl_info):
        impl = self.Adaptor_instance.implementation
        name = self.__name__
        impl.update_target_spaces(method_infos={name: impl_info})
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
            raise AdaptionError("No implementation chosen for "
                                "following adaptor:\n%s"%self.Adaptor_instance)
        try:
            ret = self.cls_func(self.Adaptor_instance, *args, **kwargs)
        except TypeError as e:
            if str(e).endswith("object is not callable") and self.target in (
                    None, NotImplemented):
                raise AdaptionError("target of adaptionmethod %s is "
                                    "%s."%(self.__name__, self.target)) from e
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
        impl = self.Adaptor_instance.implementation
        name = self.__name__
        target_space = impl.method_target_spaces.get(name)
        if target_space is None:
            self.target = None
            self.target_space = None
            self.impl_info = None
            return
        try:
            target = getattr(target_space, self.target_name)
        except AttributeError:
            if self.require_target:
                raise AdaptionError(f"Required function '{self.__name__}' "
                f"was not found.\ntartget namespace: "
                f" {target_space}\nimplementation: {impl}")
            target = NotImplemented
        self.target_space = target_space
        self.impl_info = impl.method_infos.get(name, impl.main_info)
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
        if isinstance(obj, AdaptionFuncPlaceholder):
            yield name
    for basecls in cls.__bases__:
        for name in _get_AdaptionFuncPlaceholders(basecls):
            try:
                obj = getattr(cls, name)
            except AttributeError:
                continue
            if isinstance(obj, AdaptionFuncPlaceholder):
                yield name
                

class AdaptorBase(KeepInstanceRefs):
    implementation_source = None  # set in first level subclass
    # adapt_on_first_use = False
    autoadapt_active = False
    dependency_folder = None  # set in first level subclass
    _subclass_level = 0
    adaptionmethod_names = set()
    
    
    def __init_subclass__(cls):
        cls._subclass_level += 1
        l = tuple(_get_AdaptionFuncPlaceholders(cls))
        if l:
            # this means that this subclass can actually create instances
            if cls._subclass_level < 2:
                raise SyntaxError("First-level Subclass of AdaptorBase is  "
                                  "not allowed to have adaptionmethods.")
            cls.adaptionmethod_names = set(l)
                #this will inherit names already defined
            cls.implementation_classes = None
            cls.added_impl_names = {}
            
    
    def __init__(self, main_info=None, *, group="default", _primary=False,
            **method_infos):
        
        super().__init__()
        
        check_type((str, int), group, allowed=(None,))
        self.primary = False
        self.instance_group = group
        
        if _primary is True:
            if group is None: raise ValueError
            prim_inst = self.get_primary_instance()
            if prim_inst:
                raise ValueError("Primary instance for this instance group "
                                 "already set:\n" + str(prim_inst))
            # the following is a way of conditionally subclassing:
            RememberInstanceCreationInfo.__init__(self)
            self.primary = True  # self.adapt_on_first_use = True #overrides
            # class default
        self.implementation = None
        
        for name in self.adaptionmethod_names:
            placeholder = getattr(self.__class__, name)
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
    
    
    
    def adapt(self, main_info=None, *, warn=True, raise_error=True,
            check_adapted=True, **method_infos):
        """main_info can be string, Implementation or ArgSaver object."""
        try:
            if isinstance(main_info, Implementation):
                impl = main_info
                if method_infos: impl.update_target_spaces(None, method_infos)
            else:
                if main_info is None and not method_infos:
                    main_info = self.get_from_impl_dict()
                impl = Implementation(self.__class__, main_info, method_infos)
        except AdaptionError as e:
            if raise_error: raise
            if warn:
                text = f"Encountered an Exception trying to adapt\n{self}\n"
                for _ in range(10):
                    if str(e):
                        text += type(e).__name__ + ": " + str(e) + "\n"
                    e = e.__cause__
                    if e is None: break
                    text += "caused by\n"
                warnings.warn(text)
            return False
        if impl.main_info is None and not impl.method_infos:
            if check_adapted:
                raise AdaptionError("Given implementation information not "
                            "valid and none found in default implementations")
        self.implementation = impl
        for amethod in self.adaptionmethods(): amethod.set_target()
        return impl.show_target_spaces()
    
    
    
    def __repr__(self):
        if self.primary:
            r = RememberInstanceCreationInfo.__repr__(self)[
                :-1] + ", primary instance of group '"
        else:
            r = super().__repr__()[:-1] + ", instance group: '"
        r += str(self.instance_group) + "', implementation: " + str(
                self.implementation) + ">"
        return r
    
    
    @property
    def is_adapted(self):
        return self.implementation is not None
    
    @classmethod
    def deactivate_autoadapt(cls):
        cls.autoadapt_active = False
    
    @classmethod
    def activate_autoadapt(cls):
        cls.autoadapt_active = True
    
    
    @classmethod
    def _adapt_all(cls, omit_adapted_inst=False, raise_error=True, warn=True,
            impl_source=None):
        for inst in cls.get_instances():
            if inst.is_adapted and omit_adapted_inst: continue
            impl_info = inst.get_from_impl_dict(impl_source=impl_source)
            inst.adapt(impl_info, raise_error=raise_error, warn=warn,
                    check_adapted=False)
    
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
    
    
    
    # @property
    # def implementation(self):
    #     if self._implementation is None and self.adapt_on_first_use and not \
    #             self.autoadapt_active:
    #         try:
    #             self.adapt()
    #         except AdaptionError:
    #             self.adapt_on_first_use = False
    #     return self._implementation
    
    @classmethod
    def update_group_implementation(cls, apply=True, **new_group_infos):
        if not hasattr(cls, "adaptionmethod_names"): raise SyntaxError
        for group, impl_info in new_group_infos.items():
            x = getattr(cls.implementation_source, cls.__name__)
            setattr(x, group, impl_info)
            if apply:
                for inst in cls._get_group_instances(group): inst.adapt()
    
    
    # @classmethod
    # def implementation_class(cls, impl_class):
    #     """a class decorator"""
    #     check_type(type, impl_class)
    #     cls.added_impl_names[impl_class.__name__] = impl_class
    #     if cls.implementation_classes is None: cls.implementation_classes =
    #     set()
    #     cls.implementation_classes |= {impl_class}
    #     return impl_class
    
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
    def _get_from_impl_dict(cls, group_or_instance="default",
            Adaptor_class_or_name=None, impl_source=None):
        if impl_source is None: impl_source = cls.implementation_source
        
        if Adaptor_class_or_name is None:
            Adaptor_subclass_name = cls.__name__
        elif issubclass(Adaptor_class_or_name, cls):
            Adaptor_subclass_name = Adaptor_class_or_name.__name__
        else:
            Adaptor_subclass_name = Adaptor_class_or_name
        check_type(str, Adaptor_subclass_name)
        
        try:
            subclass_info_class = getattr(impl_source, Adaptor_subclass_name)
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
        check_type((str, tuple, list, Implementation, ArgSaver), main_info)
        return main_info
    
    def get_group_instances(self):
        return self._get_group_instances(self.instance_group)
    
    def get_primary_instance(self):
        return self._get_primary_instance(self.instance_group)
    
    def get_from_impl_dict(self, impl_source=None):
        return self._get_from_impl_dict(self.instance_group,
                impl_source=impl_source)
    
    # @classmethod
    # def import_dependency(cls, dependency_name):
    #     check_type(str, dependency_name)
    #     check_type(dict, cls.dependency_dict)
    #     # the following tries to find a user defined dependency module in the
    #     #  dependency dict:
    #     dependency_module = cls.dependency_dict.get(dependency_name)
    #     if not dependency_module:
    #         # otherweise look up the dependency in the default dependency
    #         folder
    #         try:
    #             dependency_package = cls.default_dependency_folder
    #         except AttributeError as e:
    #             raise AttributeError(
    #                     "Could not find default dependency package location. "
    #                     "This should be set by the {"
    #                     "cls}.default_dependency_package"
    #                     " class attribute.".format_map(locals())) from e
    #         dependency_module = importlib.import_module(
    #                 dependency_package + "." + dependency_name)
    #     return dependency_module
    
    @classmethod
    def print_all_infos(cls):
        for subclass in cls.__subclasses__():
            print("subclass:", subclass)
            path = os.path.dirname(inspect.getfile(subclass))
            for submodule in pkgutil.iter_modules([path]):
                name = submodule[1]
                if not name.startswith("adapt_"):
                    continue
                print("implementation:", name[6:])
                full_name = subclass.__module__ + "." + name
                # mod=sys.modules[subclass.__module__+"."+name]
                try:
                    mod = importlib.import_module(full_name)
                except NotImplementedError:
                    print("-- NotImplementedError")
                    continue
                try:
                    dfl = mod.dependency_full_name
                except AttributeError:
                    dfl = None
                else:
                    print("dependency module:", dfl)
            for i in subclass.get_instances():
                print("")
                print("instance: ", i)
                print("defined in:", i.creation_module)
                print("on line:", i.creation_line)
            print("")
            print("")
            
            
            
    @classmethod
    def coupled_class(cls):
        """Immediately creates a baseclass to be used"""
        return type(cls.__name__ + ".CoupledClass", (CoupledClass,),
                dict(adaptor_class = cls))



wrap = functools.wraps(AdaptorBase.adapt)
class CoupledClass:
    
    adaptor_class = None
    adaptor = None

    @classmethod
    @wrap
    def adapt(cls, *args, **kwargs):
        if "adaptor" in cls.__dict__:
            #in this case, an adaptor instance was explicitely set for this
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



class Implementation:
    
    def __repr__(self):
        s = f"<Implementation('{self.main_info}'"
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
        if isinstance(other,self.__class__):
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
                self.method_target_spaces[
                    name] = self.main_target_space
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
                obj = self.adaptorcls.added_impl_names[obj]
            except KeyError:
                break
        else:
            raise RecursionError
        return obj
    
    def get_targetspace(self, info):
        if isinstance(info, str):
            # TODO: add option to give full path of module instead
            module_name = ".adapt_" + info
            module_location = self.adaptorcls.__module__
            module_full_name = module_location + module_name
            if self.dependency_folder:
                sys.path.insert(0, self.dependency_folder)
                # this makes sure that packages inside the dependency folder
                # are found first. Unless the module has already been imported.
            try:
                ret = importlib.import_module(module_full_name)
            except Exception as e:
                raise AdaptionError from e
            if self.dependency_folder: sys.path.pop(0)
            return ret, info
        elif isinstance(info, (list, tuple)):
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
            raise TypeError(
                    f"Require string, but got {info}.")  # TODO: Add option
            # for implementation classes