import functools
from .adaptor_base import AdaptorBase
from ..arghandling import check_type



wraps = functools.wraps(AdaptorBase, assigned=())

class AdaptiveClass:
    adaptor_class = None
    adaptor = None
    
    @classmethod
    @wraps
    def adapt(cls, *args, **kwargs):
        if "adaptor" in cls.__dict__:
            # in this case, an adaptor instance was explicitly set for this
            # subclass before
            check_type(cls.adaptor_class, cls.adaptor)
        else:
            # in this case, the adaptor attribute is only inherited -- we
            # need to redefine it to avoid adapting the base class too
            group = None if not args and not kwargs else "default"
            cls.adaptor = cls.adaptor_class(group=group)
        return cls.adaptor.adapt(*args, **kwargs)
    
    @wraps
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
        doc = f"Subclass of :class:`Dpowers.AdaptiveClass`.\n\n" \
              f"Associated Adaptor class: {aclss_ref}\n\n"
        doc += aclss._create_import_instr(cls.__name__)
        if cls.__doc__: doc += cls.__doc__ + "\n\n"
        # doc += f".. data:: adaptor\n\n\t*Class attribute.* An instance of " \
        #        f"{aclss_ref}, as explained in :attr:`AdaptiveClass.adaptor`.\n\n"
        doc += ".. automethod:: adapt\n\n\tChoose the backend for this " \
               "class. See :func:`AdaptiveClass.adapt`." \
               " For parameters see :func:`Dpowers.Adaptor.adapt`."
        cls.__doc__ = doc
    
    @classmethod
    def _create_subclass_docs(cls):
        for subcls in cls._iter_subclasses(): subcls._create_doc()