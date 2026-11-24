#
#
# Copyright (c) 2020-2025 DPS, dps@my.mail.de
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
wand="wand"
eyed3 = "eyed3"
termux = "termux"

class linux:
    
    class HookAdaptor:
        default  = pynput
        triggerman = dict(cursor = pynput, buttons = pynput, keys = evdev,
                custom=evdev)
        keywait = triggerman
        
    class MouseAdaptor:
        default = pynput
        
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
        
    class DialogAdaptor:
        default = dict(_="zenity_bash",popup="tkinter")
        
    class ImageAdaptor:
        default = wand
        
    class mp3tagAdaptor:
        default = eyed3
        
    class TextToSpeechAdaptor:
        default = "ttsx3"
        
    class RecognizerAdaptor:
        default = "SpeechRecognition"
        
    class SoundPlayAdaptor:
        default = "sox"
        
    class VolumeAdaptor:
        default = "pulsectl"
        

class termux:
    
    class NotificationAdaptor:
        default = termux
        
    class ClipboardAdaptor:
        default = termux
    
    class DialogAdaptor:
        default = termux
    
    class ImageAdaptor(linux.ImageAdaptor):
        pass
    
    class mp3tagAdaptor(linux.mp3tagAdaptor):
        pass
    
    class TextToSpeechAdaptor:
        default = termux
        
    class RecognizerAdaptor:
        default = termux
    
    class SoundPlayAdaptor:
        default = "sox"

    class VolumeAdaptor:
        default = termux
    
    
class windows:
    class KeyboardAdaptor:
        default = pynput
        
    class IconAdaptor:
        default = pystray
        
    class MouseAdaptor:
        default = pynput

    class ImageAdaptor:
        default = wand

    class mp3tagAdaptor:
        default = eyed3