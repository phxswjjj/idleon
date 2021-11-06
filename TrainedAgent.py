import os
from time import sleep

import cv2
import keyboard
import numpy as np
import win32api as wapi
import win32gui
from fastai.vision.all import load_learner

from utility import win32

_RESOURCE_DIR_PATH = r'resources'
_EXPORT_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\export.pkl')

_LMB_KEYCODE = 0x01

AppTitle = 'Legends Of Idleon'
hwnd = win32gui.FindWindow(None, AppTitle)
if hwnd == 0:
    print('Error: App not found.')
    exit()
win32gui.SetForegroundWindow(hwnd)
winInfo: win32.WindowInfo = win32.getWindowInfo(hwnd=hwnd)


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


def label_func(x): return x.parent.name


def run():
    learn_inf = load_learner(os.path.abspath(_EXPORT_PATH))
    print("loaded learner")

    default_pos = (970, 70)
    default_size = (444, 232)

    while True:

        full_image = win32.screenshot(*winInfo.position, *winInfo.size)
        full_image = np.array(full_image)

        right_bottom = (default_pos[0] + default_size[0],
                        default_pos[1] + default_size[1])
        small_image = full_image[default_pos[1]:right_bottom[1],
                                 default_pos[0]:right_bottom[0]]
        small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
        small_image = cv2.GaussianBlur(small_image, (5, 5), 0)
        small_image = cv2.Canny(small_image, threshold1=100, threshold2=150)

        test = learn_inf.predict(small_image)
        action = test[0]
        text = str(test)
        cv2.putText(small_image, text, (0, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow('image', small_image)
        cv2.waitKey(1)
        is_q = wapi.GetAsyncKeyState(ord('Q')) & 0x8000
        if is_q:
            exit()

        if action == 'lmb':
            keyboard.press('space')
            keyboard.release('space')


if __name__ == "__main__":
    if not wait_mouse_click():
        print('Error: Mouse not clicked.')
        exit()

    run()
