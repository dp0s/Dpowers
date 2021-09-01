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

.. _AdaptiveClass label:

AdaptiveClasses
----------------

- :class:`Dpowers.Win`: Find and manipulate windows on your screen.
- :class:`Dpowers.Icon`: Create and display tray icons, including context menu.
- :class:`Dpowers.Image`: Edit and assemble image files.
- :class:`Dpowers.KeyWaiter`: Collect key events until a condition is fullfilled.
- :class:`Dpowers.TriggerManager`: Define event patterns (such as key or
  button sequences) to trigger your own functions.

An AdaptiveClass is a subclass of the common baseclass
:class:`Dpowers.AdaptiveClass`. All instances created by this class will share
the same backend.



Basic Examples
************************************



.. example:: Display a tray icon with customized menu
    Dpowers.ntfy
    Dpowers.Icon

.. code::

    from Dpowers import autoadapt, Icon, ntfy
    myicon = Icon()

    @myicon.additem
    def my_custom_menu_item():
        ntfy("You clicked the custom menu item.")

    myicon.start()





.. example:: Define a key sequence to trigger a function
    Dpowers.TriggerManager

.. code::

    from Dpowers import TriggerManager, sleep
    TriggerManager.adapt()
    MyTriggers = TriggerManager().hook_keys()

    @MyTriggers.sequence("ctrl d d_rls")
    def myfunction():
        print("Control + d was pressed")

    MyTriggers.start()
    sleep(30)
    MyTriggers.stop()




.. example:: Define a combined key / button sequence as trigger
    Dpowers.TriggerManager

.. code::

    from Dpowers import TriggerManager
    TriggerManager.adapt(keys="evdev", buttons="pynput")

    CombinedTriggers = TriggerManager(timeout = None)
    Keys = CombinedTriggers.hook_keys()
    Buttons = CombinedTriggers.hook_buttons()

    @Keys.sequence("ctrl d")
    def myfunction():
        print("Control + d was pressed")

    @Buttons.sequence("mleft")
    def myfunction2():
        print("Left mouse button was pressed.")

    @CombinedTriggers.sequence("Ctrl mleft")
    def myfunction3():
        print("Ctrl + left mouse button was pressed")

    CombinedTriggers.start()
    # this will run in background until CombinedTriggers.stop()


Advanced Examples
********************




.. example:: Click on a window to paste its properties to the clipboard
    Dpowers.ntfy
    Dpowers.dlg
    Dpowers.clip
    Dpowers.Win


.. code::

    from Dpowers import autoadapt, ntfy, Win, dlg, clip


    def display_win_info():
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

    display_win_info()

This function is pre-defined in the module `Dpowers.Dfuncs.py
<https://github.com/dp0s/Dpowers/tree/master/Dlib/Dpowers/Dfuncs.py>`_::

    from Dpowers import autoadapt, Dfuncs
    Dfuncs.display_win_info()






.. example:: Launch the browser and simultaneously redirect key presses
    Dpowers.launch
    Dpowers.Win
    Dpowers.KeyWaiter

.. code::

        from Dpowers import autoadapt, launch, Win, KeyWaiter, ntfy

        def firefox_launch():

            with KeyWaiter(100, 15, endevents="Return", capture=True) as address:
                FirefoxWindows = Win("^Mozilla Firefox$")  # the ^ and $
                # mark that we want an exact title match  (regular expression)
                launch("firefox", "-P", "default", check=True, check_err=False)
                newWin = FirefoxWindows.wait_num_change(+1, timeout=10)

            if not newWin: return
            if newWin.num != 1: raise ValueError
            newWin.activate()

            code = address.exitcode
            if code not in  ("endevent", "__exit__"):
                raise ValueError(f"Wrong exitcode: {code}")
            address.reinject(delay=1)