from Dhelpers.launcher import launch
from ... import DependencyManager

command = "play"

with DependencyManager(__name__) as manager:
    manager.test_shellcommand(command)


def beep(frequency, duration):
    launch(command,"-q","-n","synth",duration,"sin", frequency)