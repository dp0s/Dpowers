from .. import DependencyManager, launch

with DependencyManager(__name__) as tester:
    tester.test_shellcommand("termux-clipboard-get")
    
    
def get(selection):
    return launch.get("termux-clipboard-get")

def fill(content,selection):
    launch.wait("termux-clipboard-set", content)