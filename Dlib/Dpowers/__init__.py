#
#
# Copyright (c) 2020-2024 DPS, dps@my.mail.de
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


__all__ = ["autoadapt", "keyb", "mouse", "ntfy", "dlg", "hook", "Icon", "Win",
    "sendwait", "nfsendwait", "clip", "Dfuncs", "events", "KeyWaiter",
    "TriggerManager", "Image", "mp3tag", "sleep", "sound","hotkeys","launch",
    "Layout","Dpowers", "Dhelpers"]

import os, sys
from time import sleep

dpowers_folder = os.path.dirname(os.path.realpath(__file__))
dpowers_startup_working_dir = os.getcwd()

try:
    import Dpowers  # this is to allow from Dpowers import * to also import the
                    # Dpowers variable itself
    import Dhelpers
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(dpowers_folder))
    import Dpowers
    import Dhelpers
    

__version__ = "0.1.5rc2"
#Dpowers and Dhelpers share version number
if __version__ != Dhelpers.__version__:
    import warnings
    warnings.warn("Dpowers and Dhelpers packages do not share same version "\
                  "number")

from Dhelpers.adaptor import (AdaptorBase, adaptionmethod, AdaptionError,
    AdaptorBase, adaptionmethod, AdaptiveClass)
from Dhelpers.launcher import launch
from Dhelpers.builtin_manipulation import always_print_traceback, \
    restore_print_func
from Dhelpers.arghandling import ArgSaver
from Dhelpers.KeyboardLayouts import Layout

    
try:
    always_print_traceback()

    from . import default_backends

    class Adaptor(AdaptorBase):
        """Abstract baseclass for all of Dpower's Adaption classes."""
        #dependency_folder = dependency_folder
        NamedKeyClass = None  #set later
        NamedButtonClass = None  #set later
    
    Adaptor.set_default_backends(default_backends, evaluate_platform=True)
    
    DependencyManager = Adaptor.DependencyManager
    activate_autoadapt = Adaptor.activate_autoadapt
    adapt_all = Adaptor.adapt_all
    deactivate_autoadapt = Adaptor.deactivate_autoadapt
    check_adapted = Adaptor.check_adapted


    from .notificationpower import NotificationAdaptor
    ntfy = NotificationAdaptor(_primary_name="ntfy")


    from .windowpower import WindowAdaptor, WindowHandler
    class Win(WindowHandler):
        adaptor = WindowAdaptor(_primary_name="Win.adaptor")

    
    from .dialogpower import DialogAdaptor
    dlg = DialogAdaptor(_primary_name="dlg")


    from . import events
    from .events import keyb,mouse,hotkeys,hook, KeyWaiter, \
        KeyboardAdaptor, MouseAdaptor, HookAdaptor, SenderAdaptor, TriggerManager

    from .clipboardpower import ClipboardAdaptor
    clip = ClipboardAdaptor(_primary_name="clip")


    from .iconpower import IconAdaptor, IconHandler
    class Icon(IconHandler):
        adaptor = IconAdaptor(_primary_name="Icon.adaptor")
    
    from . import editing
    from .editing import Image, ImageAdaptor, mp3tag, mp3tagAdaptor
    
    from . import sound

    from . import Dfuncs
    from .Dfuncs import sendwait, nfsendwait
    
    from . import winapps

finally:
    restore_print_func()

#clean up this namespace
del os, AdaptorBase, adaptionmethod, always_print_traceback, \
    restore_print_func

Adaptor._set_effective_paths(globals(),__name__)