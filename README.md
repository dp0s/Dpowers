Written for Python 3.6+

Dependencies:     
sudo apt install xdotool wmctrl zenity yad xsel xclip x11-xserver-utils python3-xlib python3-psutil python3-tk python3-evdev


Start your Script e.g. with the following lines:

from Dpowers import *

ThisScript().terminate_other_instances()  
Icon().start()
