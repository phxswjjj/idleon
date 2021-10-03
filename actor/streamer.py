import threading
import time
import tkinter
from ctypes import windll

import win32con
import win32gui
import win32ui
from PIL import Image, ImageTk

if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from utility import win32


class StreamWidget(tkinter.Canvas):
    def __init__(self, window, width, height):
        super().__init__(window, width=width, height=height, bg='blue')

        self.window = window
        new_width = self.winfo_reqwidth()
        new_height = self.winfo_reqheight()
        self.width = new_width
        self.height = new_height

        self.bind('<Configure>', self.on_resize)

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
            pimg = ImageTk.PhotoImage(image=resize_img)
            self.create_image(0, 0, image=pimg, anchor=tkinter.NW)
            # keep image alive
            self.photo = pimg


class App():
    def __init__(self, target_win_title, refresh_interval=100):
        print('Stream init')

        self._closing = False
        # too small will make it impossible to close
        self.refresh_interval = refresh_interval

        window = tkinter.Tk()
        window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window = window

        self.widgets = []
        widget = StreamWidget(window, width=500, height=400)
        widget.pack(fill='both', expand=True)
        self.widgets.append(widget)

        self._stream_widget = widget

        if target_win_title:
            self.hwnd = win32gui.FindWindow(None, target_win_title)

        job = threading.Thread(target=self._run_refresh_stream)
        self.refresh_job = job
        job.start()

    def show(self):
        window = self.window
        window.mainloop()

    def refresh_stream(self):
        image = win32.capture(self.hwnd)
        if image:
            widget = self._stream_widget
            widget.update_image(image)

    def _run_refresh_stream(self):
        while(not self._closing):
            self.refresh_stream()
            if self.refresh_interval > 0:
                time.sleep(self.refresh_interval/1000)
        print('stream stopped')

    def on_closing(self):
        window = self.window

        self._closing = True
        print('stream stopping')
        self.refresh_job.join(timeout=1)
        if self.refresh_job.is_alive():
            print('interrupt app')
            import os
            os._exit(0)

        for widget in self.widgets:
            widget.destroy()
        window.destroy()
        print('app closed')


def create(target_win_title) -> App:
    return App(target_win_title=target_win_title)


if __name__ == '__main__':
    viewer = create(target_win_title='Legends Of Idleon')
    viewer.show()
