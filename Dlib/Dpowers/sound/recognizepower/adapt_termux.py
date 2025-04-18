from Dhelpers.launcher import launch
from ... import DependencyManager

command = "termux-speech-to-text"

with DependencyManager(__name__) as manager:
    manager.test_shellcommand(command)


def recognize(language):
    return launch.get(command)