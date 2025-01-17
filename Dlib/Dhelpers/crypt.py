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
from cryptography.fernet import Fernet
from .container import container

fernet = Fernet(Fernet.generate_key())

def generate_key(name):
    key = fernet.encrypt(Fernet.generate_key())
    container.set_temp_store_key(name, key, 60*120)

def get_coder(name):
    f = Fernet(fernet.decrypt(container.store[name]))
    return lambda by: f.decrypt(by).decode(), lambda str: f.encrypt(
            str.encode())