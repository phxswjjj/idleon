import os
from datetime import datetime
from time import sleep

import cv2
import keyboard
import numpy as np
import pandas as pd
import pyautogui
import win32gui

from utility import win32

AppTitle = 'Legends Of Idleon'
_GREEN = (3, 252, 36)
_RESOURCE_DIR_PATH = r'resources'
_FISH_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, 'fish')
_FISHTMP_DIR_PATH = os.path.join(_FISH_DIR_PATH, 'tmp')

threshold = 0.8

LastFired = datetime.now()
FireInterval = 5
min_dist = None
max_dist = None
avg_dist = None

hwnd = win32gui.FindWindow(None, AppTitle)
win32gui.SetForegroundWindow(hwnd)


def test(t=0.7, filename='fish'):
    pyautogui.keyDown('space')
    sleep(t)
    pyautogui.keyUp('space')

    image = win32.capture(hwnd)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(
        _FISHTMP_DIR_PATH, f'{filename}-{t}(0).jpg'), image)

    sleep(0.3)
    for i in range(int(t*10)+1):
        image = win32.capture(hwnd)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(
            _FISHTMP_DIR_PATH, f'{filename}-{t}({i+1}).jpg'), image)
        sleep(0.1)


img_target = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'fish.jpg'), 0)
h, w = img_target.shape

left_top = (773, 496)
right_bottom = (1387, 572)
width, height = right_bottom[0] - left_top[0], right_bottom[1] - left_top[1]
while True:
    image = win32.screenshot(*left_top, width, height)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(image, img_target, cv2.TM_CCOEFF_NORMED)

    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    dist = None
    if max_val >= threshold:
        pt = max_loc
        cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 1)

        dist = max_loc[0]

        if not min_dist:
            min_dist = 9999
        if not max_dist:
            max_dist = -9999
        if min_dist > dist:
            min_dist = dist
        if max_dist < dist:
            max_dist = dist
        avg_dist = int((min_dist + max_dist)/2)
        cv2.putText(image, f'dist: {dist}, max: {max_dist}', (80, 65),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, _GREEN, 2)

    cv2.imshow(AppTitle, image)
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27 or keyboard.is_pressed('q'):
        break

    cur_time = datetime.now()
    dif_time = cur_time - LastFired
    if dist and abs(max_dist-dist) < 3:
        dist = max_dist
        if dif_time.total_seconds() > FireInterval:
            t = None
            if dist == 0:
                t = 0.1
            elif 134 <= dist <= 136:
                t = 0.2
            elif 141 <= dist <= 143:
                t = 0.23
            elif 146 <= dist <= 155:
                t = 0.25
            elif 159 <= dist <= 177:
                t = 0.32
            elif 178 <= dist <= 179:
                t = 0.33
            elif 183 <= dist <= 209:
                t = 0.35
            elif 211 <= dist <= 215:
                t = 0.37
            elif 206 <= dist <= 218:
                t = 0.4
            elif 219 <= dist <= 234:
                t = 0.41
            elif 236 <= dist <= 243:
                t = 0.43
            elif 245 <= dist <= 268:
                t = 0.45
            elif 273 <= dist <= 275:
                t = 0.48
            elif 276 <= dist <= 292:
                t = 0.49
            elif 293 <= dist <= 294:
                t = 0.5
            elif 295 <= dist <= 297:
                t = 0.52
            elif 297 <= dist <= 319:
                t = 0.53
            elif 325 <= dist <= 333:
                t = 0.55
            elif 340 <= dist <= 344:
                t = 0.56
            elif 346 <= dist <= 351:
                t = 0.57
            elif dist == 355:
                t = 0.58
            elif 360 <= dist <= 388:
                t = 0.6
            elif 390 <= dist <= 441:    # 第二根釣竿
                t = 0.63
            if t:
                LastFired = cur_time
                test(t, filename=f'fish-{dist}')
                sleep(1)
                LastFired = datetime.now()
                min_dist = None
                max_dist = None
                avg_dist = None
            else:
                cv2.imwrite(os.path.join(
                    _FISH_DIR_PATH, f'fish-not-found.jpg'), image)
                break
