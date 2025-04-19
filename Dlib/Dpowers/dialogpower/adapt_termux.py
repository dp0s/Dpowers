from .. import DependencyManager, launch
import json

base_command = "termux-dialog"

with DependencyManager(__name__) as tester:
    tester.test_shellcommand(base_command)
    
    
def quest(text, title):
    ret = launch.get(base_command, "confirm", "-i", text, "-t", title)
    dic = json.loads(ret)
    if dic["text"] == "yes":
        return True
    elif dic["text"] == "no":
        return False
    else:
        raise ValueError