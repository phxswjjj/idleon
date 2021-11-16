import threading
from datetime import datetime, timedelta
from time import sleep

import keyboard
import mouse
import win32gui

AppTitle = 'Legends Of Idleon'
next_fire = datetime.now()
fire_interval = timedelta(minutes=30)

mouse_events = []

hwnd = win32gui.FindWindow(None, AppTitle)
win32gui.SetForegroundWindow(hwnd)

keyboard.wait("a")
mouse.hook(mouse_events.append)
keyboard.wait("a")
mouse.unhook(mouse_events.append)

keep_running = True


def quit(ev):
    global keep_running
    keep_running = False


keyboard.hook_key('q', quit)

if len(mouse_events) == 0:
    print("No mouse events")
    exit()

while keep_running:
    if datetime.now() > next_fire:
        win32gui.SetForegroundWindow(hwnd)
        mouse.play(mouse_events)
        next_fire = datetime.now() + fire_interval
    sleep(10)

print('done')
