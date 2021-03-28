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
from .... import launch, DependencyManager

with DependencyManager(__name__) as manager:
    manager.test_shellcommand("xdotool", pkg="xdotool")

names = (
    'BackSpace', 'Tab', 'Linefeed', 'Escape', 'space', 'exclam', 'quotedbl',
    'numbersign', 'dollar', 'percent', 'ampersand', 'apostrophe', 'parenleft',
    'parenright', 'asterisk', 'plus', 'comma', 'minus', 'period', 'slash',
    'colon', 'semicolon', 'less', 'equal', 'greater', 'question', 'at',
    'bracketleft', 'backslash', 'asciicircum', 'underscore', 'grave',
    'braceleft', 'bar', 'braceright', 'asciitilde', 'Delete', 'nobreakspace',
    'exclamdown', 'cent', 'sterling', 'currency', 'yen', 'brokenbar', 'section',
    'diaeresis', 'copyright', 'ordfeminine', 'guillemotleft', 'notsign',
    'hyphen', 'registered', 'macron', 'degree', 'plusminus', 'twosuperior',
    'threesuperior', 'acute', 'mu', 'paragraph', 'periodcentered', 'cedilla',
    'onesuperior', 'masculine', 'guillemotright', 'onequarter', 'onehalf',
    'threequarters', 'questiondown', 'Agrave', 'Aacute', 'Acircumflex',
    'Atilde', 'Adiaeresis', 'Aring', 'AE', 'Ccedilla', 'Egrave', 'Eacute',
    'Ecircumflex', 'Ediaeresis', 'Igrave', 'Iacute', 'Icircumflex',
    'Idiaeresis', 'ETH', 'Ntilde', 'Ograve', 'Oacute', 'Ocircumflex', 'Otilde',
    'Odiaeresis', 'multiply', 'Ooblique', 'Ugrave', 'Uacute', 'Ucircumflex',
    'Udiaeresis', 'Yacute', 'THORN', 'ssharp', 'agrave', 'aacute',
    'acircumflex', 'atilde', 'adiaeresis', 'aring', 'ae', 'ccedilla', 'egrave',
    'eacute', 'ecircumflex', 'ediaeresis', 'igrave', 'iacute', 'icircumflex',
    'idiaeresis', 'eth', 'ntilde', 'ograve', 'oacute', 'ocircumflex', 'otilde',
    'odiaeresis', 'division', 'oslash', 'ugrave', 'uacute', 'ucircumflex',
    'udiaeresis', 'yacute', 'thorn', 'ydiaeresis', 'Home', 'Insert', 'End',
    'Prior', 'Next', 'Help', 'Pause', 'VoidSymbol', 'Return', 'Break',
    'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'KP_Subtract', 'KP_End', 'KP_Add',
    'KP_Delete', 'KP_Right', 'KP_Insert', 'KP_Page_Up', 'KP_Divide',
    'KP_Page_Down', 'KP_Multiply', 'KP_Up', 'KP_Down', 'KP_Next', 'KP_Begin',
    'KP_Left', 'KP_Home', 'dead_grave', 'dead_acute', 'dead_circumflex',
    'dead_tilde', 'dead_diaeresis', 'dead_cedilla', 'Down', 'Left', 'Right',
    'Up', 'Shift', 'Control', 'Alt')


# def convert_kwargs(windowID=None, delay=5, clearmodifiers=False):
#     if windowID:
#         yield "--window"
#         yield windowID
#     if delay >= 0:
#         yield '--delay'
#         yield delay
#     if clearmodifiers:
#         yield "--clearmodifiers"

def text(character):
    return launch.get("xdotool", "type", "--delay", "0", character)

#
# def key(string: str, **kwargs):
#     #print("xdootol", string)
#     return launch.get("xdotool", "key", *convert_kwargs(**kwargs), string)

def press(string: str):
    return launch.get("xdotool", "keydown", "--delay", "0", string)


def rls(string: str):
    return launch.get("xdotool", "keyup", "--delay", "0", string)
