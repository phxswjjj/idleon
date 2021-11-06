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
_IMAGES_RAWDATA_PATH = os.path.join(_RAW_DIR_PATH, 'images.npy')
_LABELS_RAWDATA_PATH = os.path.join(_RAW_DIR_PATH, 'labels.npy')
_LMB_KEYCODE = 0x01

AppTitle = 'Legends Of Idleon'
hwnd = win32gui.FindWindow(None, AppTitle)
if hwnd == 0:
    print('Error: App not found.')
    exit()
win32gui.SetForegroundWindow(hwnd)
winInfo: win32.WindowInfo = win32.getWindowInfo(hwnd=hwnd)


def get_traindata():
    images = []
    labels = []
    if os.path.isfile(_IMAGES_RAWDATA_PATH):
        images = list(np.load(_IMAGES_RAWDATA_PATH, allow_pickle=True))
    if os.path.isfile(_LABELS_RAWDATA_PATH):
        labels = list(np.load(_LABELS_RAWDATA_PATH, allow_pickle=True))
    return images, labels


def save_data(images, labels):
    np.save(_IMAGES_RAWDATA_PATH, images)
    np.save(_LABELS_RAWDATA_PATH, labels)


def wait_mouse_click() -> bool:
    lmb_state_before = wapi.GetAsyncKeyState(_LMB_KEYCODE) & 0x8000
    while True:
        is_q = wapi.GetAsyncKeyState(ord('Q')) & 0x8000
        if is_q:
            break
        lmb_state = wapi.GetAsyncKeyState(_LMB_KEYCODE) & 0x8000
        if lmb_state != lmb_state_before:
            lmb_state_before = lmb_state
            if not lmb_state:
                return True
    return False


if __name__ == '__main__':
    images, labels = get_traindata()

    # reset
    wapi.GetAsyncKeyState(_LMB_KEYCODE)
    if not wait_mouse_click():
        print('Error: Mouse not clicked.')
        exit()

    while True:
        pos = wapi.GetCursorPos()
        if not winInfo.is_inner(*pos):
            print('mouse out of bound')
            sleep(1)
            continue
        is_q = wapi.GetAsyncKeyState(ord('Q')) & 0x8000
        if is_q:
            cv2.destroyAllWindows()
            break

        image = win32.screenshot(*winInfo.position, *winInfo.size)
        image = np.array(image)
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # image = cv2.GaussianBlur(image, (5, 5), 0)
        # image = cv2.Canny(image, threshold1=100, threshold2=150)

        images.append(image)
        is_click = wapi.GetAsyncKeyState(_LMB_KEYCODE) & 0x8000
        if is_click:
            labels.append('lmb')
        else:
            labels.append('na')
        sleep(0.1)

        display_img = cv2.resize(
            image, winInfo.scale_size_fit_width(width=400))
        cv2.imshow(AppTitle, display_img)
        cv2.waitKey(1)

    save_data(images, labels)
