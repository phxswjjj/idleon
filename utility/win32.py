
import win32con
import win32gui
import win32ui
from PIL import Image


def capture(hwnd) -> Image:
    if not hwnd:
        return None

    l, t, r, b = win32gui.GetClientRect(hwnd)
    sl, st, _, _ = win32gui.GetWindowRect(hwnd)
    cl, ct = win32gui.ClientToScreen(hwnd, (l, t))

    size = (r - l, b - t)
    position = (cl - sl, ct - st)

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
    image = capture(hwnd)
    image.save('resources/tmp.jpg')
    
    from ImageViewer import showImage
    showImage(image)
