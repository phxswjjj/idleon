import tkinter
from ctypes import windll

import win32con
import win32gui
import win32ui
from PIL import Image, ImageTk


class StreamWidget(tkinter.Canvas):
    def __init__(self, window, width, height, image=None, target_win_title=None):
        super().__init__(window, width=width, height=height, bg='blue')

        self.window = window
        new_width = self.winfo_reqwidth()
        new_height = self.winfo_reqheight()
        self.width = new_width
        self.height = new_height

        self.bind('<Configure>', self.on_resize)

        if target_win_title:
            self.hwnd = win32gui.FindWindow(None, target_win_title)
            image = self.capture()

        self.update_image(image)

    def on_resize(self, event):
        new_width = event.width
        new_height = event.height
        self.width = new_width
        self.height = new_height

        self.update_image(self.image)

    def update_image(self, image):
        self.image = image

        if self.image:
            new_width = self.width
            new_height = self.height

            resize_img = self.image.resize(
                (new_width, new_height), Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(image=resize_img)
            self.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

    def capture(self):
        if not self.hwnd:
            return None

        hwnd = self.hwnd
        
        l, t, r, b   = win32gui.GetClientRect(hwnd)
        sl, st, _, _ = win32gui.GetWindowRect(hwnd)
        cl, ct       = win32gui.ClientToScreen(hwnd, (l, t))

        size     = (r - l, b - t)
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


class App():
    def __init__(self, target_win_title):
        print('Stream init')

        window = tkinter.Tk()
        window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window = window

        self.widgets = [tkinter.Frame]
        widget = StreamWidget(window, width=500, height=400,
                              target_win_title=target_win_title)
        widget.pack(fill='both', expand=True)
        self.widgets.append(widget)

    def show(self):
        window = self.window
        window.mainloop()

    def on_closing(self):
        window = self.window
        print('Stream close')
        window.destroy()


def create(target_win_title) -> App:
    return App(target_win_title=target_win_title)


if __name__ == '__main__':
    viewer = create(target_win_title='Legends Of Idleon')
    viewer.show()
