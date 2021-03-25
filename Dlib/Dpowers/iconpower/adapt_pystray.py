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

from Dhelpers.adaptor import DependencyManager

with DependencyManager(__name__) as tester:
    pystray = tester.import_module("pystray", pkg="pystray")
    Image = tester.import_module("PIL.Image", pkg="pillow")



import multiprocessing

def start(IconObject):
    IconObject.queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_pystray_icon, args=(IconObject,))
    p.start()
    return p

def run_pystray_icon(IconObject):
    def get_putter(num):
        # we need a putter function that can be called without arguments for
        # each function to call when menu entry is chosen
        # functools.partial did somehow not work
        def putter():
            IconObject.queue.put(num)
        return putter
    menutuple = tuple(pystray.MenuItem(    IconObject.items[num][0],
            get_putter(num)    )     for num in range(len(IconObject.items)))
    menu = pystray.Menu(*menutuple)
    image = Image.open(IconObject.path)
    pystray.Icon(IconObject.tooltip, image, IconObject.tooltip, menu).run()
    
    
