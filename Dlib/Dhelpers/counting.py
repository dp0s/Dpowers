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
import time, threading, importlib
from .container import container

def count(key, dic, waittime, maxc=None):
    """
    This function simply counts how often it is called within waittime and
    returns that number.
    """
    key = str(key)
    c = dic.get(key, 0)  # dic must be a globally defined dictionary
    if maxc and (c >= maxc):
        dic[key] = 0
        return 0
    dic[key] = c + 1
    threading.Thread(target=uncount,args=(key, dic, waittime)).start()
    return c

def uncount(key, dic, waittime):
    time.sleep(waittime)
    if dic[key] > 0:
        dic[key] -= 1

container.dpress_store = {}

def dpress(keyname, timebetween):
    return count(keyname, container.dpress_store, timebetween, maxc=2) == 1
