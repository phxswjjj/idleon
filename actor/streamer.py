import tkinter
from PIL import Image, ImageTk


class StreamWidget(tkinter.Canvas):
    def __init__(self, window, width, height, image=None):
        super().__init__(window, width=width, height=height, bg='blue')

        self.window = window
        new_width = self.winfo_reqwidth()
        new_height = self.winfo_reqheight()
        self.width = new_width
        self.height = new_height

        self.bind('<Configure>', self.on_resize)

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


class App():
    def __init__(self):
        print('Stream init')

        window = tkinter.Tk()
        window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window = window

        self.widgets = [tkinter.Frame]
        widget = StreamWidget(window, width=500, height=400)
        widget.pack(fill='both', expand=True)
        self.widgets.append(widget)

        widget.update_image(Image.open('./resources/cat.jpg'))

    def show(self):
        window = self.window
        window.mainloop()

    def on_closing(self):
        window = self.window
        print('Stream close')
        window.destroy()


def create() -> App:
    return App()


if __name__ == '__main__':
    viewer = create()
    viewer.show()
