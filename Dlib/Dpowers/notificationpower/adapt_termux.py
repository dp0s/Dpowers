from .. import DependencyManager, launch

with DependencyManager(__name__) as tester:
    tester.test_shellcommand("termux-toast")
    

def post_notification(title, timeout, text):
    launch("termux-toast", title)  #ignore the other args