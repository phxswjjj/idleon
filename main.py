import os
from time import sleep

import cv2
import numpy as np
import pyautogui
import win32gui
from tinydb import Query, TinyDB
from tinydb.operations import add as db_add

from actor.fisher import Actor, DetectResultType
from utility import win32

AppTitle = 'Legends Of Idleon'
_RESOURCE_DIR_PATH = r'resources'
_FISH_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, 'fish')

img_ball = cv2.imread(os.path.join(
    _RESOURCE_DIR_PATH, 'fish-ball.jpg'), 0)

hwnd = win32gui.FindWindow(None, AppTitle)
win32gui.SetForegroundWindow(hwnd)


def test_fish_db():
    db = TinyDB('resources/fish/db.json')
    dist = 428
    query = Query()
    results = db.search(query.dist == dist)
    if len(results) == 0:
        results = db.search((dist * 0.9 <= query.dist)
                            & (query.dist <= dist * 1.1))
    for r in results:
        print(r)
    ts = np.sum([r['t'] * r['count'] for r in results])
    cnt = np.sum([r['count'] for r in results])
    t = round(ts/cnt, 2)
    print(t)


def test_fish_dist(t: float):
    global img_ball
    def lt_offset(): return None
    lt_offset.x = 0
    # lt_offset.x = 17
    lt_offset.y = 0

    power = 0

    left_top = (773 + lt_offset.x, 496 + lt_offset.y)
    right_bottom = (1387 + lt_offset.x, 572 + lt_offset.y)
    width, height = right_bottom[0] - \
        left_top[0], right_bottom[1] - left_top[1]

    fisher = Actor(template=img_ball, threshold=0.8, power=power)

    pyautogui.keyDown('space')
    sleep(t)
    pyautogui.keyUp('space')

    def fetch():
        image = win32.screenshot(*left_top, width, height)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image

    result, loc = fisher.detect_until(fetch=fetch, timeout=3)
    if result == DetectResultType.OK:
        dist = loc[0]
        print(f't={t:1.2f}, dist={dist}')
    else:
        print(f't={t:1.2f} test fail')


def test_fish_power():
    test_fish_dist(t=0.1)


if __name__ == '__main__':
    # test_fish_db()

    test_fish_power()

    print('done')
