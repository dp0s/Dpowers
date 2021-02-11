import warnings, os

def import_all(folder, globals, raise_error=False):
    _, folders, files = os.walk(folder).__next__()
    for file in files:
        if not file.endswith(".py"): continue
        modname = file[:-3]
        try:
            yield modname, __import__(modname, globals=globals, level=1)
        except ModuleNotFoundError as e:
            if raise_error: raise
            warnings.warn(f"Module {modname} not loaded because of error: {e}")
    for modname in folders:
        dir = os.path.join(folder,modname)
        if "__init__.py" not in os.listdir(dir): continue
        try:
            yield modname, __import__(modname, globals=globals, level=1)
        except ModuleNotFoundError as e:
            if raise_error: raise
            warnings.warn(f"Subpackage {modname} not loaded because of error: {e}")

def extract_all(mod, globals, all):
    try:
        names = mod.__all__
    except AttributeError:
        names = tuple(name for name in mod.__dict__ if not name.startswith(
                "__"))
    for name in names:
        if name in globals: continue
        globals[name] = getattr(mod, name)
        all.append(name)