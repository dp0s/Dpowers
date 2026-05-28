from ... import DependencyManager, launch
import warnings

with DependencyManager(__name__) as manager:
    pulsectl = manager.import_module("pulsectl")
    
    
pulse = pulsectl.Pulse()

def stream_names():
    return tuple(sink.description for sink in pulse.sink_list())

def find_sink(name):
    if not name:
        return pulse.sink_default_get()
    else:
        for sink in pulse.sink_list():
            if sink.description == name: return sink
        else:
            return False

def get(stream):
    sink = find_sink(stream)
    if not sink: return False
    return pulse.volume_get_all_chans(sink), 1, sink.description

def set(new_lev,stream):
    sink = find_sink(stream)
    if not sink: return False
    return pulse.volume_set_all_chans(sink,new_lev)
    