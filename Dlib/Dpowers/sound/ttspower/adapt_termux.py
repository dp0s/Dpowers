from Dhelpers.launcher import launch
from ... import DependencyManager

command = "termux-tts-speak"

with DependencyManager(__name__) as manager:
    manager.test_shellcommand(command)


def call(text):
    return launch.wait(command, text)