Installation and Dependencies
*****************************

Install from PyPI::

    $ pip install -U Dpowers

(This will automatically install the package 'Dhelpers' as a
necessary dependency. All of Dhelpers' functions and classes can be used
independently for your own projects, i.e. without the Dpowers package
installed, via ``pip install -U Dhelpers``.)

After first installation, you should try::

    >>> import Dpowers

This should never raise an exception, otherwise please file a bug report.

.. note:: The pip install command does NOT install any of the backend
    dependencies. You need to manually install the dependencies for the backends you want to
    use.



The following prints a list of all dependencies for all backends on your
system (given example is for Debian/Ubuntu/Linux Mint):


.. activecode::

        >>> import Dpowers
        >>> print(Dpowers.Adaptor.install_instructions())
        Dpowers.Adaptor.install_instructions()

Execute the output lines in your shell and you should be able to use all backends.


Importing and Adapting
************************

Step 1: Import
------------------------

This is done as usual. Examples::

    import Dpowers
    from Dpowers import keyb, ntfy


By default the imported objects are unadapted, i.e. there's no backend chosen yet. If you try using them, you'll get an exception::

    >>> from Dpowers import keyb
    >>> keyb.tap("a")
    AdaptionError: No backend chosen for following adaptor:
    <Dpowers.events.sending.keybpower.KeyboardAdaptor object at 0x7fedf46e00b8 with creation_name 'keyb', primary instance of group 'default', backend: None>


Step 2: Adapt
------------------------------
    
For each object, choose a backend by calling its :func:`~Dpowers.Adaptor.adapt` method. If you call it without any arguments, the default backend for your platform will be chosen depending on your system::

    >>> from Dpowers import keyb
    >>> keyb.adapt()  # pynput is the default backend in this example
    <module 'Dpowers.events.sending.keybpower.adapt_pynput'>
    >>> keyb.adapt("pynput") # another way to select pynput
    <module 'Dpowers.events.sending.keybpower.adapt_pynput'>
    >>> keyb.adapt("evdev")  # manually chose another backend
    <module 'Dpowers.events.sending.keybpower.adapt_evdev'>
    >>> keyb.tap("a") # check if it works
    >>> a

.. note:: Calling the adapt method will import the corresponding backend module (if it hasn't been imported before). It raises an exception if the backend is not supported on your system or the backend's dependencies could not be found.

Alternative: autoadapt
-----------------------

You can perform the two steps (import and adapt) in only one line::

    import Dpowers.autoadapt
    # which is equivalent to
    import Dpowers
    Dpowers.activate_autoadapt()

This will try to adapt ALL adaptable objects to their default backend if
possible, and prints a warning for each exception encountered. The list of
default backends is defined in `Dpowers .default_backends.py
<https://github.com/dp0s/Dpowers/tree/master/Dlib/Dpowers/default_backends.py>`_


Alternatively, the wildcard import also activates autoadapt::

    >>> from Dpowers import *
    >>> keyb.tap("a") # check if it works
    >>> a

 
A list of all names imported this way:

.. activecode:: 

    >>> Dpowers.__all__
    Dpowers.__all__
