The Dpowers are a collection of python tools for common automization tasks, such as:

- Send / receive events from keyboard, mouse and other devices.
- Wait for a certain key combination or sequence to trigger your own code.
- Observe and interact with windows on your screen.
- Display notifications, dialog boxes and tray icons.
- Access the clipboard content.
- Edit images.


The Dpowers package bundles existing open-source projects into a unified python interface. It provides a high level of flexibility due to the following characteristics:

- Adaptable. Each job can be performed by several backends of your choice. Switch between backends dynamically in one line of code.
- Modular. Each sub-package (a.k.a. sub-power) can be used independently.
- Easy to extend. You can add your own power and/or your own backend without touching existing files.
- Cross-platform by nature. (More backends need to be added and tested though to be fully cross-platform.)


Benefits:

- Save time by learning one command syntax to access several backends. 
- Combine the advantages of two or more backends into a single tool.
- Future safe. If one backend becomes out-dated, replace it by a more recent one. No need to change your code.
- Short and intuitive commands are prefered to type less.
- Some higher level classes are included to enhance the backend's functionality. (Such as :class:`Dpowers.Win` and :class:`Dpowers.KeyWaiter`)
