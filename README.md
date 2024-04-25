Dpowers is a python package to help you automate interactions with your 
operating system. It combines several backends into a unified interface and 
allows to pick the backend most suited to the specific use case.

For documentation and details see https://dpowers.readthedocs.io.

Supported operating systems:

- This project follows a modular approach where is is easy to add new 
components ("powers"), as well as new backends for aleady existing powers. 
This makes it cross-platform by nature. The support for a specific OS 
depends mostly on which backends have been implemented yet.

- As I am using Linux Mint myself, I make sure that all features run 
smoothly on there. Other Linux systems (particularly Debian-based) should 
already be supported by the implemented backends as well, but haven't been 
tested yet.

- Windows and Mac haven't been tested either. They should be supported via 
the pynput backend already. As of now, I don't have any plans to add more 
backends for these systems since I almost never use them.

- Termux on Android is supported as well. I have two everyday use 
  cases, where the Dpowers allow me to run the same python script on both 
  Linux desktop and my Android phone. However, Termux lacks access to many 
  Android functions, which is why I prefer Tasker for most of my Android 
  automization. Tasker allows using Termux as a plugin, so it can 
  also run python and Dpowers scripts.

If you have question about a specific part of this project, if you want to try 
it out on another OS, or add your own backends, you are welcome to post 
issues here on github.


Ideas for the future:
- Add complete support for Wayland. Keyboard and mouse support is already 
  available via the evdev backend, but window interactions are still relying 
  on the X Server.
- Add automatic detections of the OS / platform properties (e.g. wether X 
  Server or Wayland active), and automatically select the suiting backend. 
  Currently, automatic selection of backends is only supported on Linux.
- Extend the documentation. (Reference for all commands, more examples, 
  tutorials.)