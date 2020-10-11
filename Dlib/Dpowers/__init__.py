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



__all__ = ["Dpowers","autoadapt","sleep","launch","ThisScript","Icon","Win",
    "keyb", "mouse","ntfy","dlg","hotkeys","hook","sendwait","nfsendwait",
    "clip", "Dfuncs","events", "KeyWaiter"]

import os

from time import sleep

from Dhelpers import __version__
from Dhelpers.all import (always_print_traceback, restore_print_func,
    launch, ThisScript, AdaptorBase, adaptionmethod, AdaptionError, ArgSaver,
    Layout)

    
try:
    always_print_traceback()

    dpowers_folder = os.path.dirname(os.path.realpath(__file__))
    dpowers_startup_working_dir = os.getcwd()
    #dependency_folder = os.path.join(dpowers_folder, "dependencies")
    #dependency_package = __name__ + ".dependencies"

    from .default_implementations import default_implementations

    class Adaptor(AdaptorBase):
        #dependency_folder = dependency_folder
        implementation_source = default_implementations
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


    from .windowpower import WindowAdaptor
    Win = WindowAdaptor(_primary=True)


    from .dialogpower import DialogAdaptor
    dlg = DialogAdaptor(_primary=True)


    from . import events
    from .events import keyb,mouse,hotkeys,hook, KeyWaiter, \
        KeyboardAdaptor, MouseAdaptor, HookAdaptor

    from .clipboardpower import ClipboardAdaptor
    clip = ClipboardAdaptor(_primary=True)


    from .iconpower import IconAdaptor, IconBase
    class Icon(IconBase):
        adaptor = IconAdaptor(_primary=True)

    from . import Dfuncs
    from .Dfuncs import sendwait, nfsendwait

finally:
    restore_print_func()

import Dpowers  # this is to allow from Dpowers import * to also import the
                # Dpowers variable itself

#clean up this namespace
del os, AdaptorBase, adaptionmethod, always_print_traceback, \
    restore_print_func, IconBase, default_implementations
