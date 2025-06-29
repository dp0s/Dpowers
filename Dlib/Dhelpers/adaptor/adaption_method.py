import inspect, functools, types
from ..baseclasses import iter_all_vars
from ..arghandling import (check_type, remove_first_arg, ArgSaver)
from types import FunctionType
from .adaptor_base import AdaptorBase, AdaptionError



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
        def func(adaptor_inst, val):
            check_type(ty, val, allowed=(None, False, True))
            setattr(adaptor_inst, custom, val)
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
                if inspect.isclass(check_ty): check_type(check_ty, attr_obj)
            setattr(self.Adaptor_instance, "_backend_" + attr_name, attr_obj)
        
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
            self.target_param_num = len(
                    self.target_signature.parameters)  # print( self.target, self.target_signature, self.signature_to_pass)
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


