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



__all__ = ["Dpowers","autoadapt","sleep","launch","Icon","Win",
    "keyb", "mouse","ntfy","dlg","hotkeys","hook","sendwait","nfsendwait",
    "clip", "Dfuncs","events", "KeyWaiter", "Image", "mp3tag"]

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


__version__ = "0.1.0rc3"
from Dhelpers import __version__  as Dhelpers_version
#Dpowers and Dhelpers share version number
if __version__ != Dhelpers_version: raise ValueError

from Dhelpers.all import (always_print_traceback, restore_print_func,
    launch, AdaptorBase, adaptionmethod, AdaptionError, ArgSaver, Layout,
    AdaptorBase, adaptionmethod)

    
try:
    always_print_traceback()

    from .implementation_defs import implementations

    class Adaptor(AdaptorBase):
        #dependency_folder = dependency_folder
        implementation_source = implementations
        NamedKeyClass = None  #set later
        NamedButtonClass = None  #set later


    activate_autoadapt = Adaptor.activate_autoadapt
    adapt_all = Adaptor.adapt_all
    deactivate_autoadapt = Adaptor.deactivate_autoadapt
    check_adapted = Adaptor.check_adapted

        #def autoadapt(self):
            #"""this method allows to automatically choose the platform's standard
            #implementation for a single Adaptor instance"""
            #return self.lookup(impl_dict=default_impl_dict)

    # def apply_autoadapt():
    #     Adaptor.apply_implementation_dict(default_impl_dict)
    #     if Adaptor.implementation_dict != default_impl_dict: raise ValueError
    #     return Adaptor.implementation_dict


    from .notificationpower import NotificationAdaptor
    ntfy = NotificationAdaptor(_primary=True)


    from .windowpower import WindowAdaptor, WindowHandler
    class Win(WindowHandler):
        adaptor = WindowAdaptor(_primary=True)

    from .dialogpower import DialogAdaptor
    dlg = DialogAdaptor(_primary=True)


    from . import events
    from .events import keyb,mouse,hotkeys,hook, KeyWaiter, \
        KeyboardAdaptor, MouseAdaptor, HookAdaptor

    from .clipboardpower import ClipboardAdaptor
    clip = ClipboardAdaptor(_primary=True)


    from .iconpower import IconAdaptor, IconHandler
    class Icon(IconHandler):
        adaptor = IconAdaptor(_primary=True)
    
    from . import editing
    from .editing import Image, ImageAdaptor, mp3tag, mp3tagAdaptor

    from . import Dfuncs
    from .Dfuncs import sendwait, nfsendwait

finally:
    restore_print_func()

#clean up this namespace
del os, AdaptorBase, adaptionmethod, always_print_traceback, \
    restore_print_func, implementations
