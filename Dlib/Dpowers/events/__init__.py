#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
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
import functools
from .. import Adaptor, AdaptionError, adaptionmethod
from Dhelpers.arghandling import add_kw_only_arg

class hotkeys:
    @classmethod
    def add_pause_option(cls, default_pause_value, timeout=10):
        def wrapper_function(func):
            @functools.wraps(func)
            def function_with_hotkey_pause(*args, pause_hotkeys=default_pause_value, **kwargs):
                if pause_hotkeys is True:
                    with cls.paused(timeout): return func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            #function_with_hotkey_pause.__signature__ = add_kw_only_arg(func,
             #       "pause_hotkeys", default=default_pause_value)
            return function_with_hotkey_pause
        return wrapper_function
    
    def paused(self,*args,**kwargs):
        raise Exception("paused called too early")

    def TriggerManager(self,*args,**kwargs):
        raise Exception("TriggerManager called too early")

# a container for the TriggerManager switch
# this is necessary to avoid circular imports between modules
# this must be defined before the imports,
# because several modules need to import this
# the content is set later after the TriggerManager is defined

from .keybutton_classes import *
from .keybutton_names import *

Adaptor.NamedButtonClass = NamedButton
Adaptor.NamedKeyClass = NamedKey


from .event_classes import *




from .hookpower import *

hook = HookAdaptor(_primary=True)

from .sending import *

mouse = MouseAdaptor(_primary=True)
keyb = KeyboardAdaptor(_primary=True)

from .event_classes import *



from .sending.event_sender import *

from .waiter import *
from .trigman import *

hotkeys.TriggerManager = TriggerManager
hotkeys.paused = TriggerManager.paused
# usage: with hotkeys.paused(time)



del Adaptor, adaptionmethod, AdaptionError