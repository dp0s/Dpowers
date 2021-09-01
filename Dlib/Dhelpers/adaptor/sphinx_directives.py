from ..sphinx import Ref_to_Examples, CustomTextDirective
from .adaptor_classes import AdaptorBase


class AdaptiveClassDirective(CustomTextDirective):
    
    def create_text(self):
        name = self.content[0].strip()
        rest = self.content[1:]
        text = Ref_to_Examples.create_example_refs(name)
        text += ".. autoclass:: " + name + "\n"
        for line in rest:
            text += "\t" + line
        return text
    
    
class AdaptorDirective(CustomTextDirective):
    
    def create_text(self):
        fullname = self.content[0].strip()
        rest = self.content[1:]
        assert not rest
        s = fullname.split(".")
        name = s[-1]
        for cls in AdaptorBase.iter_subclasses():
            if cls.__qualname__ == name: break
        else:
            raise NameError(name)
        cls.adapt.__doc__ = "Choose the backend for this instance. See " \
                            ":func:`Adaptor.adapt`."
        pname = cls.__visible_module__ + "."  \
                + cls._get_primary_instance().creation_name
        
        text = Ref_to_Examples.create_example_refs(pname)
        text += \
f"""
.. autodata:: {pname}
    :no-value:
    
.. autoclass:: {cls.__visible_fullname__}

    .. automethod:: adapt


.. class:: {cls.__visible_fullname__}.AdaptiveClass

    A baseclass to create your own AdaptiveClasses. See \
            :class:`Dpowers.AdaptiveClass`.

"""
        return text