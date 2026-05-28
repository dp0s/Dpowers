from Dhelpers.launcher import launch
from ... import DependencyManager
import json

command = "termux-volume"

with DependencyManager(__name__) as manager:
    manager.test_shellcommand(command)

def stream_names():
    l = json.loads(launch.get(command))
    return tuple(s['stream'] for s in l)

def get(stream):
    if not stream or stream == "media": stream = "music"
    l = json.loads(launch.get(command))
    #dict = {s['stream']:(int(s['volume']),int(s['max_volume'])) for s in l}
    for entry in l:
        if entry["stream"] == stream:
            return entry["volume"], entry["max_volume"], stream
    else:
        return False

def set(new_lev, stream):
    if not stream or stream == "media": stream = "music"
    return launch.wait(command,stream,new_lev)