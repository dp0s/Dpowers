Written for Python 3.6+

Installation:
sudo pip install psutil Dpowers

Careful! This will reset evdev to version 0.7. In a next update, I will make Dpowers compatible to current version of evdev.

Further dependencies:
sudo apt install xdotool wmctrl zenity yad xsel xclip x11-xserver-utils python3-tk


Start your Script e.g. with the following lines:

from Dpowers import *

ThisScript().terminate_other_instances()  
Icon().start()

Documentation and/or more examples will be added later.
