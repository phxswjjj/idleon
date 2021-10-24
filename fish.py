import os
import sys
from datetime import datetime
from time import sleep

import cv2
import keyboard
import numpy as np
import pandas as pd
import pyautogui
import win32gui

from actor.fisher import Actor, DetectResultType
from utility import win32
from utility.stopwatch import StopWatch

AppTitle = 'Legends Of Idleon'
_GREEN = (3, 252, 36)
_RESOURCE_DIR_PATH = r'resources'
_FISH_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, 'fish')
_FISHTMP_DIR_PATH = os.path.join(_FISH_DIR_PATH, 'tmp')

threshold = 0.75

LastFired = datetime.now()
FireInterval = 4
pre_dist = None
min_dist = None
max_dist = None

hwnd = win32gui.FindWindow(None, AppTitle)
win32gui.SetForegroundWindow(hwnd)


def fishing(actor: Actor, t: float, except_dist: int = None):
    pyautogui.keyDown('space')
    sleep(t)
    pyautogui.keyUp('space')

    result, loc = actor.detect_until(fetch=fetch_fish_area)
    actual_dist = loc[0]
    dist_ratio = None
    if actual_dist:
        dist_ratio = round(actual_dist / except_dist, 2)
    print(
        f't={t}, result={result.name}, actual_dist={actual_dist}, except_dist={except_dist}, dist_ratio={dist_ratio}')
    if result == DetectResultType.OK and except_dist and abs(except_dist-actual_dist) < 20:
        actor.matched(t=t, dist=actual_dist)
        image = actor.last_source
        cv2.imwrite(os.path.join(
            _FISHTMP_DIR_PATH, f'fish-last-matched.jpg'), image)


img_target = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'fish.jpg'), 0)
h, w = img_target.shape


def lt_offset(): return None


# 1-1 poist
lt_offset.x = 0
# lt_offset.x = 17
lt_offset.y = 0

# 1-2 point
# lt_offset.x = -127
lt_offset.x = -131

power = None

left_top = (773 + lt_offset.x, 496 + lt_offset.y)
right_bottom = (1387 + lt_offset.x, 572 + lt_offset.y)
width, height = right_bottom[0] - left_top[0], right_bottom[1] - left_top[1]

img_ball = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'fish-ball.jpg'), 0)
img_pts = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'fish-pts.jpg'), 0)


def check_pts_position() -> bool:
    global left_top, width, height, img_pts, fisher

    image = win32.screenshot(*left_top, width, height)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    x = 8
    for y in range(24):
        if image[y+15][x] > 100:
            print(f'PTS verify fail: {(x, y+15)}={image[y+15][x]}')
            return False

    return True


check_pts_result = check_pts_position()
if not check_pts_result:
    image = win32.screenshot(*left_top, width, height)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    if image[70][12] == image[70][30] == image[70][65] == 210:
        print('ready to fish')
        click_x, click_y = left_top
        click_x += 100
        click_y += 30
        pyautogui.click(click_x, click_y)
        sleep(1)
        # try again
        check_pts_result = check_pts_position()


def fetch_fish_area():
    global left_top, width, height
    left, top = left_top
    image = win32.screenshot(*left_top, width, height)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


fisher = Actor(template=img_ball, threshold=0.8, power=power)
while True:
    image = fetch_fish_area()

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
        cv2.putText(image, f'dist: {dist}, max: {max_dist}', (80, 65),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, _GREEN, 2)

    cv2.imshow(AppTitle, image)
    key = cv2.waitKey(1)
    if key == ord('q') or keyboard.is_pressed('q'):
        cv2.imwrite(os.path.join(
            _FISH_DIR_PATH, f'fish-q.jpg'), image)
        break

    cur_time = datetime.now()
    dif_time = cur_time - LastFired

    # 計算誤差
    if max_dist:
        offset_dist = int((max_dist - min_dist)/12)
        if offset_dist > 10:
            offset_dist = 10

    if not pre_dist:
        pre_dist = dist

    if check_pts_result and dist and max_dist-dist <= offset_dist and pre_dist <= dist:
        pre_dist = dist
        dist = max_dist - int(img_ball.shape[1]/2)
        if dif_time.total_seconds() > FireInterval:
            print(f'dist={pre_dist}, min_dist={min_dist}, max_dist={max_dist}, offset_dist={offset_dist}')
            t = fisher.lookup_t(dist=dist)
            if t:
                LastFired = cur_time
                fishing(actor=fisher, t=t, except_dist=dist)
                sleep(3)
                LastFired = datetime.now()
                pre_dist = None
                min_dist = None
                max_dist = None
            else:
                cv2.imwrite(os.path.join(
                    _FISH_DIR_PATH, f'fish-not-found.jpg'), image)
                break
    else:
        pre_dist = dist
