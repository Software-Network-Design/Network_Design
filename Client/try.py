import tkinter as tk
from tkinter import filedialog


def select_file():
    # 单个文件选择
    selected_file_path = filedialog.askopenfilename()  # 使用askopenfilename函数选择单个文件
    select_path.set(selected_file_path) 

root = tk.Tk()
root.title("选择文件或文件夹，得到路径")

# 初始化Entry控件的textvariable属性值
select_path = tk.StringVar()

# 布局控件
tk.Label(root, text="文件路径：").grid(column=0, row=0, rowspan=3)
tk.Entry(root, textvariable = select_path).grid(column=1, row=0, rowspan=3)
tk.Button(root, text="选择单个文件", command=select_file).grid(row=0, column=2)


root.mainloop()

