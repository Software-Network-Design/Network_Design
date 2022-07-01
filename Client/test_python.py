from pathlib import Path
from tkinter.scrolledtext import ScrolledText
from tkinter import *


def func():
    global file_icon, text
    text.image_create(END, image=file_icon)


root = Tk()
text = ScrolledText(root)
text.insert(END, 'content'+'\n', 'green')
# photo = PhotoImage(file='../media/e1.png')
# text.image_create(END, image=photo)     # 用这个方法创建一 个 图片对象，并插入到“END"的位置
# text.insert(END, '\ncontent'+'\n', 'green')
# photo2 = PhotoImage(file='../media/e2.png')
# text.image_create(END, image=photo2)
# photo3 = PhotoImage(file='../media/e3.png')
# text.image_create(END, image=photo3)
# photo4 = PhotoImage(file='../media/e4.png')
# text.image_create(END, image=photo4)
file_icon = PhotoImage(file=str(Path('../media/icons8-file-96.png')))
# file_icon = PhotoImage("D:\\University Courses\\Network_Design\\media\\icons8-file-96.png")
text.image_create(END, image=file_icon)
text.pack()
text.mainloop()
root.mainloop()


# file_pic = PhotoImage('../media/icons8-file-96.png')

