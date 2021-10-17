import math
import os
import sys
import time
from datetime import datetime

import cv2
import keyboard
import numpy as np
import pyautogui
import win32gui

from utility import win32
from utility.stopwatch import StopWatch

AppTitle = 'Legends Of Idleon'
CVTitle = f'CV-{AppTitle}'
_GREEN = (3, 252, 36)
_WHITE = (255, 255, 255)
_RESOURCE_DIR_PATH = r'resources'

threshold = 0.8

LastFired = datetime.now()
FireInterval = 5
xOffsetWidth = 400

failCount = 0


def isMatchFire() -> bool:
    global LastFired
    cur_time = datetime.now()
    dif_time = cur_time - LastFired
    return dif_time.total_seconds() > FireInterval


def takeItems(hwnd, pts):
    global LastFired
    if isMatchFire():
        LastFired = datetime.now()

        win32gui.SetForegroundWindow(hwnd)
        pyautogui.moveTo(x=200, y=950)
        pyautogui.mouseDown(button='left')
        for pt in pts[:3]:
            x, y = pt
            pyautogui.dragTo(x=x, y=y+10, duration=0.3, mouseDownUp=False)
            pyautogui.dragRel(xOffset=-xOffsetWidth, yOffset=0,
                              duration=0.3, mouseDownUp=False)
            pyautogui.dragRel(xOffset=xOffsetWidth*3, yOffset=0,
                              duration=0.8, mouseDownUp=False)

        pyautogui.dragTo(x=200, y=950, duration=0.2, mouseDownUp=False)
        pyautogui.mouseUp(button='left')

        LastFired = datetime.now()


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    xd = (x1-x2)**2
    yd = (y1-y2)**2
    return math.sqrt(xd+yd)


hwnd = win32gui.FindWindow(None, AppTitle)
sw = StopWatch()
sw.start()

img_target = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'Copper_Coin.jpg'), 0)

h, w = img_target.shape

pause = False
while True:
    image = win32.capture(hwnd)
    image = np.array(image)
    # image_org = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(image, img_target, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    pts = []
    lastPt = None
    for pt in zip(*loc[::-1]):
        cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 1)
        if not lastPt or distance(pt, lastPt) > 300:
            lastPt = pt
            pts.append(pt)

    # _, max_val, _, max_loc = cv2.minMaxLoc(result)
    # if max_val >= threshold:
    #     takeItem(hwnd, max_loc)

    fps = sw.fps()
    cv2.putText(image, f'FPS: {fps}, Pause: {pause}', (70, 50),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, _WHITE, 2)

    cv2.imshow(CVTitle, image)
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27 or keyboard.is_pressed('q'):
        # image_org = cv2.cvtColor(image_org, cv2.COLOR_RGB2BGR)
        # cv2.imwrite(os.path.join(
        #     _RESOURCE_DIR_PATH, 'tmp2.jpg'), image_org)
        break

    if keyboard.is_pressed('s'):
        pause = not pause

    if not pause and len(pts) > 0:
        failCount = 0
        takeItems(hwnd, pts)
    elif len(pts) == 0 and isMatchFire():
        failCount += 1
        if failCount > 1000:
            sys.exit()
    else:
        failCount = 0

sw.stop()
cv2.destroyAllWindows()
