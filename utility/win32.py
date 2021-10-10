
import time

import cv2
import numpy as np
import win32con
import win32gui
import win32ui
from mss import mss
from PIL import Image

if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.path.realpath('.'))

    if not __package__:
        __package__ = 'utility'


class WindowInfo():
    def __init__(self):
        self.width: int = None
        self.height: int = None
        # left, top
        self.position: (int, int) = None

    @property
    def size(self) -> (int, int):
        return (self.width, self.height)


def getWindowInfo(hwnd: int = None, title: str = None) -> WindowInfo:
    if not hwnd:
        if title:
            hwnd = win32gui.FindWindow(None, title)
        else:
            raise InputError

    l, t, r, b = win32gui.GetClientRect(hwnd)
    sl, st, _, _ = win32gui.GetWindowRect(hwnd)
    cl, ct = win32gui.ClientToScreen(hwnd, (l, t))

    size = (r - l, b - t)
    position = (cl - sl, ct - st)

    info = WindowInfo()
    info.width, info.height = size
    info.position = position
    return info

# 25 fps
def capture(hwnd) -> Image:
    if not hwnd:
        return None

    winInfo = getWindowInfo(hwnd)
    size = winInfo.size
    position = winInfo.position

    # too small
    if size[1] < 100:
        return None

    hwndDC = win32gui.GetDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, *size)
    saveDC.SelectObject(saveBitMap)

    saveDC.BitBlt((0, 0), size, mfcDC, position, win32con.SRCCOPY)
    saveDC.SelectObject(saveBitMap)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return im


if __name__ == '__main__':
    hwnd = win32gui.FindWindow(None, 'Legends Of Idleon')
    winInfo = getWindowInfo(hwnd)

    from .stopwatch import StopWatch
    sw = StopWatch()
    sw.start()

    RECT_COLOR = (0, 255, 0)
    framesCount = 0
    bottom_left = (50, 50)
    while True:
        image = capture(hwnd)
        framesCount += 1
        frame = np.array(image)
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame = np.array(image)

        fps = sw.fps(framesCount)
        frame = cv2.putText(frame, 'FPS: ' + str(fps), bottom_left,
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, RECT_COLOR, 2)

        cv2.imshow('press q to exit', frame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            cv2.destroyAllWindows()
            break
