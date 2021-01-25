import os,sys

#this fixes an annoying error message on termux/android where /proc
# permission is not given
# see https://stackoverflow.com/questions/62640148

sys.stderr = open(os.devnull, "w")
try:
  import psutil
finally:
  sys.stderr = sys.__stderr__