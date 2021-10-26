import os
from datetime import datetime
from time import sleep

import cv2
import numpy as np
import win32api as wapi
import win32gui

from utility import win32

_RESOURCE_DIR_PATH = r'resources'
_RAW_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\raw')
_TRAIN_DATA_PATH = os.path.join(_RAW_DIR_PATH, 'train_data.npy')
_TARGET_DATA_PATH = os.path.join(_RAW_DIR_PATH, 'target_data.npy')

AppTitle = 'Legends Of Idleon'
hwnd = win32gui.FindWindow(None, AppTitle)
win32gui.SetForegroundWindow(hwnd)
winInfo: win32.WindowInfo = win32.getWindowInfo(hwnd=hwnd)


def setting(): return None


image_size = 21
setting.width = image_size*3
setting.height = image_size*3
setting.contain = lambda x, y: \
    winInfo.position[0] <= x <= winInfo.position[0]+winInfo.width \
    and winInfo.position[1] <= y <= winInfo.position[1]+winInfo.height


def get_traindata():
    images = []
    targets = []
    if os.path.isfile(_TRAIN_DATA_PATH):
        images = list(np.load(_TRAIN_DATA_PATH, allow_pickle=True))
        targets = list(np.load(_TARGET_DATA_PATH, allow_pickle=True))
    return images, targets


def save_data(images, targets):
    np.save(_TRAIN_DATA_PATH, images)
    np.save(_TARGET_DATA_PATH, targets)


def wait_mouse_click() -> bool:
    lmb_state_before = wapi.GetAsyncKeyState(0x01) & 0x8000
    while True:
        is_q = wapi.GetAsyncKeyState(ord('Q')) & 0x8000
        if is_q:
            break
        lmb_state = wapi.GetAsyncKeyState(0x01) & 0x8000
        if lmb_state != lmb_state_before:
            lmb_state_before = lmb_state
            if not lmb_state:
                return True
    return False


if __name__ == '__main__':
    # reset
    wapi.GetAsyncKeyState(0x01)

    images, targets = get_traindata()

    while True:
        if not wait_mouse_click():
            break
        pos = wapi.GetCursorPos()
        print(datetime.now(), 'LMB click', pos)
        left_top = (pos[0]-int(setting.width/2), pos[1]-int(setting.height/2))
        if not setting.contain(*left_top):
            print('out of bound')
            continue
        image = win32.screenshot(*left_top, setting.width, setting.height)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # image = cv2.GaussianBlur(image, (5, 5), 0)
        image = cv2.Canny(image, threshold1=100, threshold2=150)

        images.append(image)
        targets.append(['item'])

        display_img = cv2.resize(image, (400, 400))
        cv2.imshow(AppTitle, display_img)
        cv2.waitKey(1)

    save_data(images, targets)
