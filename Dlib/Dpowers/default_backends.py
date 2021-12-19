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


pynput = "pynput"
evdev = "evdev"
pystray = "pystray"

class linux:
    
    class HookAdaptor:
        default  = pynput
        keywait = (evdev, pynput)
        triggerman = dict(buttons = pynput, keys = evdev, custom=evdev)
        
    class MouseAdaptor:
        default = pynput
        Dfuncs = default
        keywait = default
        
    class WindowAdaptor:
        default = "xtools_bash"
        
    class KeyboardAdaptor:
        default = (pynput, evdev)
        Dfuncs = pynput
        keywait = (evdev, pynput)
        hotstring = pynput
        
    class IconAdaptor:
        default = (pystray, "yad_bash")
        
    class ClipboardAdaptor:
        default = "xclip_bash"
    
    class NotificationAdaptor:
        default = "notify_send_bash"
        waiter =  default
        
    class DialogAdaptor:
        default = dict(_="zenity_bash",popup="tkinter")
        
    class ImageAdaptor:
        default = "wand"
        
    class mp3tagAdaptor:
        default ="eyed3"
        
    class TextToSpeechAdaptor:
        default = "ttsx3"
        

class termux:
    class ImageAdaptor(linux.ImageAdaptor):
        pass
    
    class mp3tagAdaptor(linux.mp3tagAdaptor):
        pass
    
    
class windows:
    class KeyboardAdaptor:
        default = pynput
        Dfuncs = pynput
        keywait = pynput
        hotstring = pynput
        
    class IconAdaptor:
        default = pystray
        
    class MouseAdaptor:
        default = pynput
        Dfuncs = default
        keywait = default

    class ImageAdaptor:
        default = "wand"

    class mp3tagAdaptor:
        default = "eyed3"