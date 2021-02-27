Installation and Dependencies
*****************************

Install from PyPI::

    pip install Dpowers

(This will automatically install the package 'Dhelpers' as a
necessary dependency. All of Dhelpers' functions and classes can be used
independently for your own projects, i.e. without the Dpowers package
installed, via ``pip install Dhelpers``.)

.. note:: The pip install command does NOT install any of the backend
    dependencies. You need to manually install the dependencies for the backends you want to
    use.



The following prints a list of all dependencies for all backends on your
system:


.. activecode::

        >>> import Dpowers
        >>> print(Dpowers.Adaptor.install_instructions())
        Dpowers.Adaptor.install_instructions()

Execute these lines in your shell and you should be ready to go.





Importing and Adapting
************************