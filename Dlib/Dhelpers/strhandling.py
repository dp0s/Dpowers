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
def cut_right(string: str, keywords_to_cut, max_number_of_cuts=1):
    if type(keywords_to_cut) is str:
        keywords_to_cut = (keywords_to_cut,)
    for i in range(max_number_of_cuts):
        if string.endswith(keywords_to_cut):
            for keyword in keywords_to_cut:
                if string.endswith(keyword):
                    string = string[:len(keyword)]
                    break  # this breaks the inner for loop
        else:
            break  # stop checking if no keyword found anymore
    return string

def cut_left(string: str, keywords_to_cut, max_number_of_cuts=1):
    if type(keywords_to_cut) is str:
        keywords_to_cut = (keywords_to_cut,)
    for i in range(max_number_of_cuts):
        if string.startswith(keywords_to_cut):
            for keyword in keywords_to_cut:
                if string.startswith(keyword):
                    string = string[len(keyword):]
                    break  # this breaks the inner for loop
        else:
            break  # stop checking if no keyword found anymore
    return string



import re, unicodedata
from warnings import warn


# source: https://github.com/django/django/blob/master/django/utils/text.py

def slugify(value, allow_unicode=True):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value2 = unicodedata.normalize('NFKC', value)
    else:
        value2 = unicodedata.normalize('NFKD', value).encode('ascii',
                'ignore').decode('ascii')
    value2 = re.sub(r'[^\w\s-]', '', value2.lower()).strip()
    ret = re.sub(r'[-\s]+', '-', value2)
    if ret =="":
        warn(f"Could not slugify following string: '{value}'")
        ret = value
    return ret
