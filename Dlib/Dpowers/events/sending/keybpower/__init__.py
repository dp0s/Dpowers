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

from ... import adaptionmethod, hotkeys, NamedKey
from ..event_sender import AdaptivePressReleaseSender


class KeyboardAdaptor(AdaptivePressReleaseSender):
    """Send key events to the system via the chosen backend."""
    
    
    #Following adaptionmethods are mandatory in adapt_*.py:
    # press
    # rls
    
    @adaptionmethod("text")
    def _text(self, character, **kwargs):
        self._text.target(character, **kwargs)
    
    default_delay = 0
    """
    .. exec::

        event_sender.default_delay_doc("keys")
    """

    default_duration = 1
    """
    .. exec::

        event_sender.default_duration_doc("key")
    """
    

    @property
    def NamedClass(self):
        return self.NamedKeyClass
    @NamedClass.setter
    def NamedClass(self, val):
        if not issubclass(val, NamedKey): raise TypeError
        self.NamedKeyClass = val
        self._update_stand_dicts()


    @hotkeys.add_pause_option(True)
    def send(self, string, auto_rls=True, delay=None):
        """
        Convenience method to send several kind of key patterns in one
        command. It integrates the functionality of :func:`tap`, :func:`comb`
        and :func:`text`.

        :param str string: Content to be sent, format see below.
        :param bool auto_rls: If ``True``, send press and release events for
            all keys specified inside ``< >``. If ``False``, normal key names
            are
            interpreted as press events and you must attach ``_rls`` to a key
            name to send the corresponding release event.
        :param int delay: Time (in milliseconds) to wait between tapping
            keys. Defaults to :attr:`default_delay`.

        The **string** parameter will be parsed from left to right according to
        the following rules:

        - There are two special characters: ``<`` and ``>``.
          All content between them will be interpreted as key
          names (as if called by the :func:`tap` method)::

            keyb.send("<return>") # is equivalent to
            keyb.tap("return")

        - Everything outside of a ``< >`` block will be sent literally using
          the :func:`text` method::

            keyb.send("normal text input..") # is equivalent to
            keyb.text("normal text input..")

        - Use ``<key1+key2>`` to send key combinations::

            keyb.send("<ctrl+s>") # is equivalent to
            keyb.comb("ctrl","s") # is equivalent to
            keyb.send("<ctrl s s_rls ctrl_rls>", auto_rls=False)
        - Chain keys and texts as in the following examples::

            keyb.send("<home>hello world<return end>") # equivalent to
            keyb.tap("home","h","e","l","l","o"," ","w","o","r","l","d",
            "return", "end")

            keyb.send("<key1 key2 key3>") # equivalent to
            keyb.send("<key1><key2><key3>")

            keyb.send("<shift+home backspace>this line was deleted")
            # is equivalent to
            keyb.comb("shift","home")
            keyb.tap("backspace")
            keyb.text("this line was deleted")

        - If not paired, ``<`` and ``>`` are interpreted literally.
        - Use ``<><something>`` to send literal *<something>* as text output.

        """
        super().send(string, auto_rls=auto_rls, delay=delay)
    
    @hotkeys.add_pause_option(True)
    def tap(self, key, *keys, delay=None, duration=None, repeat=1):
        """Simulate a key tap (i.e. send a press event followed by a release
        event of the same key), or multiple key taps in a row.

        :param str key: Name of the (first) key to be sent.
        :param str keys: Further names of keys to be sent in sequence.
        :param int delay: Time (in milliseconds) to wait after tapping a key.
            Defaults to :attr:`default_delay`.
        :param int duration: Time (in milliseconds) to wait between each press
            and release event. Defaults to :attr:`default_duration`.
        :param repeat: Number of times this sequence should be repeated.

        Examples::
        
            keyb.tap("a")
            keyb.tap(1)
            keyb.tap("esc")
            keyb.tap("f9")
        """
        return super().tap(key, *keys, delay=delay, duration=duration,
                repeat=repeat)

    @hotkeys.add_pause_option(True)
    def press(self, key, *keys, delay=None):
        """Send key press event(s) to the system. You need to manually send
        the corresponding release event(s) afterwards.

        :parameters: See :func:`tap`.
        """
        return super().press(key, *keys, delay=None)

    @hotkeys.add_pause_option(True)
    def rls(self, key, *keys, delay=None):
        """Send key release event(s) to the system.

        :parameters: See :func:`tap`.
        """
        return super().rls(key, *keys, delay=None)
    


    @hotkeys.add_pause_option(True)
    def comb(self, key1, key2, *keys, delay=None, duration=None):
        """Simulates a key combination, such as *Control+S* or *Shift+Alt+F5*.
        Sends all the press events first and then the release events in
        reverse order.
        
        :param str key1: The is the name of the first key to be pressed (and
            hence the last to be released.)
        :param str key2: The name of the second key in the combination.
        :param str keys: Further key names.
        :param int delay: Time (in milliseconds) to wait between
            pressing/releasing the sequence of keys. Defaults to
            :attr:`default_delay`.
        :param int duration: Time (in milliseconds) to wait between sending
            the press and release event of the final key. Defaults to
            :attr:`default_duration`.
        
        Examples::
        
            keyb.comb("ctrl","s")
            keyb.comb("shift","alt","f5")
        """
        return super().comb(key1, key2, *keys, delay=delay, duration=duration)

    custom_text_method = True
    """Default value for parameter **custom** of method :func:`text`."""


    @hotkeys.add_pause_option(True)
    def text(self, text, delay=None, custom=None, **kwargs):
        """Send a plain text string to the system as if the user would type it.
        
        :param str text: Any text you want to send. Depending on the backend,
             not all symbols might be supported.
        :param int delay: Time (in milliseconds) to wait between sending
            single characters. Defaults to :attr:`default_delay`.
        :param bool custom: If set to ``True``, prefer the backend's special text
            method if implemented. Otherwise use :func:`tap` for sending
            single characters via the backend's press/rls methods.
        :param kwargs: Custom keyword arguments to pass to the backend's
            text method.
        """
        return super().text(text,delay=delay, custom=custom, **kwargs)


    @property
    def key(self):
        """This object allows accessing Dpowers' internal key objects and key
        groups. Find a key object by calling it's name:

        .. activecode::
            
            > keyb.key("a")
            repr(keyb.key("a"))
            > keyb.key("ctrl")
            repr(keyb.key("ctrl"))
            > keyb.key(1)
            repr(keyb.key(1))

        You can find key groups via the **.group** attribute and check if a
        key belongs to it:

        .. activecode::
            > keyb.key.group.arrow_keys
            keyb.key.group.arrow_keys
            > "up" in keyb.key.group.arrow_keys
            True
            > 0 in keyb.key.group.arrow_keys
            False
            > 0 in keyb.key.group.digits
            True
        """
        return self.NamedKeyClass.NameContainer