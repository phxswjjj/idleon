import tkinter

from PIL import Image, ImageTk


def showImage(image):
    window = tkinter.Tk()
    widget = tkinter.Canvas(window, width=800, height=600, bg='blue')
    widget.pack(fill='both', expand=True)
    new_width = widget.winfo_reqwidth()
    new_height = widget.winfo_reqheight()

    resize_img = image.resize(
        (new_width, new_height), Image.ANTIALIAS)
    pimg = ImageTk.PhotoImage(image=resize_img)
    widget.create_image(0, 0, image=pimg, anchor=tkinter.NW)

    window.mainloop()

if __name__ == '__main__':
    image = Image.open("resources/cat.jpg")
    showImage(image)