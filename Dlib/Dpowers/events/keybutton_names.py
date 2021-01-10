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
from .keybutton_classes import NamedKey, NamedButton



@NamedButton.update_names
class StandardButtonNames:
    class standard:
        left = 'mouse_left', 'mleft', 'left', 'l', 'mouse_1', 'm1', 1
        middle = 'mouse_middle', 'mmiddle', 'middle', 'm', 'mouse_2', 'm2', 2
        right = 'mouse_right', 'mright', 'r', 'right', 'mouse_3', 'm3', 3
    class scrolling:
        scroll_up = 'scroll_up', 's_up', 'wheel_up', 'mouse_4', 'm4', 4
        scroll_down = 'scroll_down', 's_down', 'wheel_down', 'mouse_5', 'm5', 5
        scroll_left = 'scroll_left', 's_left', 'wheel_left', 'mouse_6', 'm6', 6
        scroll_right = 'scroll_right', 's_right', 'wheel_right', 'mouse_7', \
            'm7', 7
    class unnamed:
        mouse_0 = "mouse_0", "m0", 0
    # fill the unnamed class with following buttons names:
    for i in range(8, 40):
        name = f"mouse_{i}"
        setattr(unnamed, name, (name, f"m{i}", i))
    del i, name


@NamedKey.update_names
class StandardKeyNames:
    class small_letters:
        a = 'a'
        b = 'b'
        c = 'c'
        d = 'd'
        e = 'e'
        f = 'f'
        g = 'g'
        h = 'h'
        i = 'i'
        j = 'j'
        k = 'k'
        l = 'l'
        m = 'm'
        n = 'n'
        o = 'o'
        p = 'p'
        q = 'q'
        r = 'r'
        s = 's'
        t = 't'
        u = 'u'
        v = 'v'
        w = 'w'
        x = 'x'
        y = 'y'
        z = 'z'
    class capital_letters:
        A = 'A'
        B = 'B'
        C = 'C'
        D = 'D'
        E = 'E'
        F = 'F'
        G = 'G'
        H = 'H'
        I = 'I'
        J = 'J'
        K = 'K'
        L = 'L'
        M = 'M'
        N = 'N'
        O = 'O'
        P = 'P'
        Q = 'Q'
        R = 'R'
        S = 'S'
        T = 'T'
        U = 'U'
        V = 'V'
        W = 'W'
        X = 'X'
        Y = 'Y'
        Z = 'Z'
    class letters(small_letters, capital_letters):
        pass
    class digits:
        zero = '0', 'zero'
        one = '1', 'one'
        two = '2', 'two'
        three = '3', 'three'
        four = '4', 'four'
        five = '5', 'five'
        six = '6', 'six'
        seven = '7', 'seven'
        eight = '8', 'eight'
        nine = '9', 'nine'
    class alphanumeric(letters,digits):
        pass
    class special_text_keys:
        space = 'space', ' '
        enter = 'Enter', 'Return', 'ret'
        backspace = 'Backspace', 'bs', 'Control_h'
        delete = 'Delete', 'del'
        tab = 'Tab','Control_i'
    class numpad_dead:
        p_page_down = 'p_page_down', 'kp_page_down'
        p_page_up = 'p_page_up', 'kp_page_up'
        p_next = 'p_next', 'kp_next'
        p_begin = 'p_begin', 'kp_begin'
        p_up = 'p_up', 'kp_up'
        p_home = 'p_home', 'kp_home'
        p_subtract = 'p_subtract', 'kp_subtract', 'kpminus'
        p_multiply = 'p_multiply', 'kp_multiply', 'kpasterisk'
        p_add = 'p_add', 'kp_add', 'kpadd', 'kpplus'
        p_end = 'p_end', 'kp_end'
        p_delete = 'p_delete', 'kp_delete'
        p_divide = 'p_divide', 'kp_divide', 'kpslash'
        p_insert = 'p_insert', 'kp_insert', 'p_ins'
        p_right = 'p_right', 'kp_right'
        p_left = 'p_left', 'kp_left'
        p_down = 'p_down', 'kp_down'
        p_dot = 'p_dot', 'kp_dot', 'kpdot', 'kp_dec'
        p_enter = 'p_enter', 'kpenter'
    class numpad_digit:
        p_0 = 'p_0', 'kp_0', 'kp0'
        p_1 = 'p_1', 'kp_1', 'kp1'
        p_2 = 'p_2', 'kp_2', 'kp2'
        p_3 = 'p_3', 'kp_3', 'kp3'
        p_4 = 'p_4', 'kp_4', 'kp4'
        p_5 = 'p_5', 'kp_5', 'kp5'
        p_6 = 'p_6', 'kp_6', 'kp6'
        p_7 = 'p_7', 'kp_7', 'kp7'
        p_8 = 'p_8', 'kp_8', 'kp8'
        p_9 = 'p_9', 'kp_9', 'kp9'
    class numpad(numpad_dead, numpad_digit):
        pass
    class navigation:
        Home = 'Home', 'Find'
        End = 'End', 'Select'
        PageUp = 'PageUp', 'Prior', 'Page_Up'
        PageDown = 'PageDown', 'Next', 'Page_Down'
        Esc = 'Esc', 'Escape'
    class modifiers:
        ShiftR = 'ShiftR', 'Shift_R', 'rightshift'
        ShiftL = 'ShiftL', 'Shift', 'Shift_L', 'leftshift'
        CtrlL = 'CtrlL', 'Control_L', 'Ctrl', 'Ctrl_L', 'Control', 'leftcontrol',\
            'leftctrl'
        CtrlR = 'CtrlR', 'Control_R', 'Ctrl_R', 'rightcontrol', 'rightctrl'
        Alt = 'Alt', 'Alt_L', 'AltL', 'leftalt'
        AltGr = 'AltGr', 'Alt_R', 'AltR', 'rightalt', '65027'
        SControl = 'SControl', 'SCtrl'
        Win = 'Win', 'Super', 'Super_L', 'cmd', 'leftmeta'
    class state_lock:
        Num_Lock = 'Num_Lock', 'NLock', 'NumLock'
        Scroll_Lock = 'Scroll_Lock', 'SLock', 'ScrollLock'
        Caps_Lock = 'Caps_Lock', 'CLock', 'CapsLock'
        AltGr_Lock = 'AltGr_Lock', 'AltRLock'
        Alt_Lock = 'Alt_Lock', 'AltLLock', 'AltLock'
    class arrow_keys:
        up = 'up'
        down = 'down'
        left = 'left'
        right = 'right'
    class fkeys:
        F1 = 'F1'
        F2 = 'F2'
        F3 = 'F3'
        F4 = 'F4'
        F5 = 'F5'
        F6 = 'F6'
        F7 = 'F7'
        F8 = 'F8'
        F9 = 'F9'
        F10 = 'F10'
        F11 = 'F11'
        F12 = 'F12'
    class special_functions:
        wlan = 'wlan'
        volumeup = 'volumeup'
        volumedown = 'volumedown'
        play = 'play', 'playpause', "playcd", "player"
        stop = 'stop', 'stopcd'
        nextsong = 'nextsong'
        previoussong = 'previoussong'
        mute = 'mute', 'min_interesting'
        touchpad_on = 'touchpad_on'
        touchpad_off = 'touchpad_off'
        appselect = 'appselect'
        sleep = 'sleep'
        calc = 'calc'
    
    class dead_keys(fkeys, special_functions, arrow_keys,state_lock,
            modifiers,navigation, numpad_dead):
        compose = 'compose'
        Linefeed = 'Linefeed', 'Control_j'
        Menu = 'Menu'
        print = 'Print', 'print_screen', 'sysrq'
        pause = 'Pause'
        insert = 'Insert', 'ins'
        
        
    class symbols:
        exclam = 'exclam', '!'
        quotedbl = 'quotedbl', '"'
        numbersign = 'numbersign', '#'
        dollar = 'dollar', '$'
        percent = 'percent', '%'
        ampersand = 'ampersand', '&'
        apostrophe = 'apostrophe', "'"
        parenleft = 'parenleft', '('
        parenright = 'parenright', ')'
        asterisk = 'asterisk', '*'
        plus = 'plus', '+', 'add'
        comma = 'comma', ','
        minus = 'minus', '-', 'subtract'
        period = 'period', '.', 'dot'
        slash = 'slash', '/', 'divide'
        backslash = 'backslash', '\\'
        colon = 'colon', ':'
        semicolon = 'semicolon', ';'
        less = 'less', '<', '102nd'
        equal = 'equal', '='
        greater = 'greater', '>'
        question = 'question', '?'
        at = 'at', '@'
        bracketleft = 'bracketleft', '[', 'leftbracket'
        bracketright = 'bracketright', ']', 'rightbracket'
        asciicircum = 'asciicircum', '^', 'circumflex'
        underscore = 'underscore', '_'
        grave = 'grave', '`'
        braceleft = 'braceleft', '{', 'leftbrace'
        bar = 'bar', '|'
        braceright = 'braceright', '}', 'rightbrace'
        asciitilde = 'tilde', '~', 'asciitilde'
        exclamdown = 'exclamdown', '¡'
        cent = 'cent', '¢'
        sterling = 'sterling', '£', 'pound'
        currency = 'currency', '¤'
        yen = 'yen', '¥'
        brokenbar = 'brokenbar', '¦'
        section = 'section', '§'
        diaeresis = 'diaeresis', '¨'
        copyright = 'copyright', '©'
        ordfeminine = 'ordfeminine', 'ª'
        guillemotleft = 'guillemotleft', '«'
        notsign = 'notsign', '¬'
        registered = 'registered', '®'
        macron = 'macron', '¯'
        degree = 'degree', '°'
        plusminus = 'plusminus', '±'
        twosuperior = 'twosuperior', '²'
        threesuperior = 'threesuperior', '³'
        acute = 'acute', '´'
        mu = 'mu', 'µ'
        paragraph = 'paragraph', '¶', 'pilcrow'
        periodcentered = 'periodcentered', '·'
        cedilla = 'cedilla', '¸'
        onesuperior = 'onesuperior', '¹'
        masculine = 'masculine', 'º'
        guillemotright = 'guillemotright', '»'
        onequarter = 'onequarter', '¼'
        onehalf = 'onehalf', '½'
        threequarters = 'threequarters', '¾'
        questiondown = 'questiondown', '¿'
        Agrave = 'Agrave', 'À'
        Aacute = 'Aacute', 'Á'
        Acircumflex = 'Acircumflex', 'Â'
        Atilde = 'Atilde', 'Ã'
        Adiaeresis = 'Adiaeresis', 'Ä'
        Aring = 'Aring', 'Å'
        AE = 'AE', 'Æ'
        Ccedilla = 'Ccedilla', 'Ç'
        Egrave = 'Egrave', 'È'
        Eacute = 'Eacute', 'É'
        Ecircumflex = 'Ecircumflex', 'Ê'
        Ediaeresis = 'Ediaeresis', 'Ë'
        Igrave = 'Igrave', 'Ì'
        Iacute = 'Iacute', 'Í'
        Icircumflex = 'Icircumflex', 'Î'
        Idiaeresis = 'Idiaeresis', 'Ï'
        ETH = 'ETH', 'Ð'
        Ntilde = 'Ntilde', 'Ñ'
        Ograve = 'Ograve', 'Ò'
        Oacute = 'Oacute', 'Ó'
        Ocircumflex = 'Ocircumflex', 'Ô'
        Otilde = 'Otilde', 'Õ'
        Odiaeresis = 'Odiaeresis', 'Ö'
        multiply = 'multiply', '×', 'multiplication'
        Ooblique = 'Ooblique', 'Ø', 'Oslash'
        Ugrave = 'Ugrave', 'Ù'
        Uacute = 'Uacute', 'Ú'
        Ucircumflex = 'Ucircumflex', 'Û'
        Udiaeresis = 'Udiaeresis', 'Ü'
        Yacute = 'Yacute', 'Ý'
        THORN = 'THORN', 'Þ'
        ssharp = 'ssharp', 'ß'
        agrave = 'agrave', 'à'
        aacute = 'aacute', 'á'
        acircumflex = 'acircumflex', 'â'
        atilde = 'atilde', 'ã'
        adiaeresis = 'adiaeresis', 'ä'
        aring = 'aring', 'å'
        ae = 'ae', 'æ'
        ccedilla = 'ccedilla', 'ç'
        egrave = 'egrave', 'è'
        eacute = 'eacute', 'é'
        ecircumflex = 'ecircumflex', 'ê'
        ediaeresis = 'ediaeresis', 'ë'
        igrave = 'igrave', 'ì'
        iacute = 'iacute', 'í'
        icircumflex = 'icircumflex', 'î'
        idiaeresis = 'idiaeresis', 'ï'
        eth = 'eth', 'ð'
        ntilde = 'ntilde', 'ñ'
        ograve = 'ograve', 'ò'
        oacute = 'oacute', 'ó'
        ocircumflex = 'ocircumflex', 'ô'
        otilde = 'otilde', 'õ'
        odiaeresis = 'odiaeresis', 'ö'
        division = 'division', '÷'
        oslash = 'oslash', 'ø'
        ugrave = 'ugrave', 'ù'
        uacute = 'uacute', 'ú'
        ucircumflex = 'ucircumflex', 'û'
        udiaeresis = 'udiaeresis', 'ü'
        yacute = 'yacute', 'ý'
        thorn = 'thorn', 'þ'
        ydiaeresis = 'ydiaeresis', 'ÿ'