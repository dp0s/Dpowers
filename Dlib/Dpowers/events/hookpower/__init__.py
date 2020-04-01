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
from .. import Adaptor, adaptionmethod
from .baseclasses import CallbackHook

class HookAdaptor(Adaptor):
    
    @adaptionmethod("Keyhook")
    def keys(self, callback = False, timeout = 60, *, capture = False,
            reinject_func = None, priority: int  = 0, dedicated_thread=
            False,  press=True, release=True, allow_multipress=False,
            write_rls=True, **custom_kwargs):
        return self.keys.target_with_args()
    
    @adaptionmethod("Buttonhook")
    def buttons(self, callback = False, timeout = 60, *, capture = False,
            reinject_func = None, priority: int  = 0,  dedicated_thread =
            False, press=True, release=True, write_rls=True, **custom_kwargs):
        return self.buttons.target_with_args()

    @adaptionmethod("Cursorhook")
    def cursor(self, callback = False, timeout = 60, *, capture = False,
            reinject_func = None, priority: int  = 0, dedicated_thread =
            False, **custom_kwargs):
        return self.cursor.target_with_args()


    @adaptionmethod("Customhook")
    def custom(self, callback = False, timeout=60, *, capture=False,
            reinject_func=None, priority: int = 0, dedicated_thread = False,
            **custom_kwargs):
        return self.custom.target_with_args()
    
    

    @keys.target_modifier
    def _km(self, target):
        self.Keyhook_class = target
        target.NamedClass = self.NamedKeyClass
        target.update_active_dict()
        self.key_translation_dicts = target.name_translation_dicts
        return target

    def add_key_translation(self, dic):
        self.key_translation_dicts += [dic]
        self.Keyhook_class.update_active_dict()


    @buttons.target_modifier
    def _bm(self, target):
        self.Buttonhook_class = target
        target.NamedClass = self.NamedButtonClass
        target.update_active_dict()
        self.button_translation_dicts = target.name_translation_dicts
        return target

    def add_button_translation(self, dic):
        self.button_translation_dicts += [dic]
        self.Buttonhook_class.update_active_dict()
    
    
    def keysbuttons(self, keybfunc=False, timeout=60, *, mousefunc=False,
            allow_multipress = False, **hookkwargs):
        # returns a HookContainer instance
        if mousefunc is False: mousefunc = keybfunc
        return  self.keys(keybfunc, timeout, allow_multipress= allow_multipress,
                 **hookkwargs) + self.buttons(mousefunc, timeout, **hookkwargs)
    
    def keyboard_mouse(self, keybfunc=False, timeout=60, *, cursorfunc=False,
            mousefunc=False, **hookkwargs):
        if cursorfunc is False: cursorfunc = keybfunc
        return self.keysbuttons(keybfunc, timeout, mousefunc=mousefunc,
                **hookkwargs) + self.cursor(cursorfunc, timeout)
    
    
    
# from Dhelpers.baseclasses import AdditionContainer
#
# class HookAdaptorContainer(AdditionContainer):
#     basic_class = HookAdaptor
#
#     @functools.wraps(HookAdaptor.keys)
#     def keys(self,*args,**kwargs):
#         return sum(m.keys(*args,**kwargs) for m in self.members)
#
#     @functools.wraps(HookAdaptor.buttons¹23#)
#     def buttons(self,*args,**kwargs):
#         return sum(m.buttons(*args,**kwargs) for m in self.members)
#
#     @functools.wraps(HookAdaptor.cursor)
#     def cursor(self,*args,**kwargs):
#         return sum(m.cursor(*args,**kwargs) for m in self.members)
#
#     @functools.wraps(HookAdaptor.keysbuttons)
#     def keysbuttons(self,*args,**kwargs):
#         return sum(m.keysbuttons(*args,**kwargs) for m in self.members)
#
#     @functools.wraps(HookAdaptor.keyboard_mouse)
#     def keyboard_mouse(self,*args,**kwargs):
#         return sum(m.keyboard_mouse(*args,**kwargs) for m in self.members)
    
    
    