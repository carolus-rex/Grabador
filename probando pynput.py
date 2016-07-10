__author__ = "Daniel"

from pynput.keyboard import Listener

def onpress(key):
    print("key pressed %s" %key)
def onrelease(key):
    print("key released %s" %key)

with Listener(on_press=onpress,on_release=onrelease) as lis:
    lis.join()