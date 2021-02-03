import builtins,time

def replace_import_func():
  builtins.__import = __import__
  it={}
  def my_import(*args,**kwargs):
    start=time.time()
    ret = __import(*args,**kwargs)
    duration=time.time() - start
    if ret not in it: it[ret.__name__]=duration
    return ret
  builtins.__import__ = my_import
  return lambda: sorted(it.items(),key=lambda item:item[1])