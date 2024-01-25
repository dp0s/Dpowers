Adaptive Classes
*****************


.. autoclass:: Dpowers.AdaptiveClass

    .. attribute:: adaptor

        *Class attribute.* This is an instance of a subclass of
        :class:`Dpowers.Adaptor`. It determines the backends available for
        this AdaptiveClass and
        is shared among all created instances. This Adaptor instance is used
        internally to access all backend specific functions. Usually you shouldn't
        use this attribute, but prefer the AdaptiveClass' methods.

    .. automethod:: adapt

        Changes the backend for all instances of this AdaptiveClass,
        including already created instances (unless
        :func:`~AdaptiveClass.adapt_instance` was used).

        For parameters see :func:`Dpowers.Adaptor.adapt`.

    .. automethod:: adapt_instance

        Changes the backend for this instance only.

        For parameters see :func:`Dpowers.Adaptor.adapt`.


Win / Win.Search
----------------

.. adaptiveclass:: Dpowers.Win
    :exclude-members: Search

    .. automethod:: __init__

    .. autodoc_members:: Dpowers.windowpower.WindowObject

.. class:: Dpowers.Win.Search

   Subclass of :class:`Dpowers.windowpower.windowobjects.WindowSearch`, using
   the same adaptor instance (and thus the same backend) as :class:`Dpowers.Win`.




Icon
----

.. adaptiveclass:: Dpowers.Icon

    .. autodoc_members:: Dpowers.iconpower.IconHandler




TriggerManager
------------------


.. adaptiveclass:: Dpowers.TriggerManager
    :exclude-members: max_thread_num




KeyWaiter
-------------------

.. adaptiveclass:: Dpowers.KeyWaiter