Overview of adaptable objects
*********************************

An adaptable object can be coupled to a specific backend by calling its
:func:`~Dpowers.Adaptor.adapt` method. There are two kinds of adaptable objects
within Dpowers - Adaptors and AdaptiveClasses.


Adaptors
----------------------

- :data:`Dpowers.keyb`: Send key events.
- :data:`Dpowers.mouse`: Send mouse events.
- :data:`Dpowers.hook`: Receive events from keyboard, mouse and other devices.
- :data:`Dpowers.clip`: Access and modify the clipboard content.
- :data:`Dpowers.ntfy`: Post notifcations on the desktop.
- :data:`Dpowers.dlg`: Show dialog boxes and wait for user confirmation.

An Adaptor is an instance of the common baseclass :class:`Dpowers.Adaptor`.
Each Adaptor provides a collection of methods which automatically call the
corresponding backend's functions.


AdaptiveClasses
----------------

- :class:`Dpowers.Win`: Find and manipulate windows on your screen.
- :class:`Dpowers.Icon`: Create and display tray icons, including context menu.
- :class:`Dpowers.Image`: Edit and assemble image files.
- :class:`Dpowers.KeyWaiter`: Collect key events until a condition is fullfilled.

An AdaptiveClass is a subclass of the common baseclass
:class:`Dpowers.AdaptiveClass`. All instances created by this class will share
the same backend.



Examples
************************************



Dispaly a tray icon with customized menu
-----------------------------------------

Reference:
:data:`Dpowers.ntfy`
:class:`Dpowers.Icon`

.. code::

    from Dpowers import autoadapt, Icon, ntfy
    myicon = Icon()

    @myicon.additem
    def my_custom_menu_item():
        ntfy("You clicked the custom menu item.")

    myicon.start()


Click on a window to paste its properties to the clipboard
----------------------------------------------------------
Taken from module `Dpowers.Dfuncs.py <https://github
.com/dp0s/Dpowers/blob/93ecd73e19307abee248af4b90509931747e54e8/Dlib/Dpowers
/Dfuncs.py#L224>`_.

Reference:
:data:`Dpowers.ntfy`
:data:`Dpowers.dlg`
:data:`Dpowers.clip`
:class:`Dpowers.Win`


.. code::

    from Dpowers import autoadapt, ntfy, Win, dlg, clip

    ntfy("Click on a window", 3)

    x = Win(loc="SELECT").all_info()
    winprops = x[:3] + ((x[1], x[2]),) + x[3:]

    show = [str(winprops[0]) + " [ID]", str(winprops[1]) + " [TITLE]",
        str(winprops[2]) + " [CLASS]", str(winprops[3]),
        str(winprops[4]) + " [PID]",
        str(winprops[5]) + " [GEOMETRY] (x,y,width,height)"]

    ret = dlg.choose(show, default=3, title="Window information",
            text="Save to clipboard:", width=700)

    if ret is not None:
        for i in range(len(show)):
            if ret == show[i]:
                clip.fill(winprops[i], notify=True)
                break