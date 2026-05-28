from Dhelpers.launcher import launch
from ... import DependencyManager
import json

command = "termux-volume"

with DependencyManager(__name__) as manager:
    manager.test_shellcommand(command)


def get():
    l = json.loads(launch.get(command))
    dict = {s['stream']:(int(s['volume']),int(s['max_volume'])) for s in l}
    dict["media"] = dict.pop('music')
    return dict

def set(new_lev, stream):
    if stream == "media": stream="music"
    return launch.wait(command,stream,new_lev)