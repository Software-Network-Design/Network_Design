import tkinter as tk
from tkinter import filedialog

<<<<<<< HEAD
def acc():
    global sta,cnt
    sta = True
    cnt=1
    frRoot.destroy()
    
def turnDown():
    global sta,cnt
    sta = False
    cnt=1
    frRoot.destroy()

def friendRequest(stranger):#来自名为stranger的人的好友请求
    global sta,frRoot,cnt
    sta = bool()
    cnt = int()
    frRoot = tkinter.Tkl()
    frRoot.title("好友申请")
    frRoot['height'] = 100
    frRoot['width'] = 500
    frRoot.resizable(0,0)
    labelFr = tkinter.Label(frRoot, text=str(stranger)+"请求添加您为好友")
    labelFr.place(x=5,y=10,height=20,width=200)
    btnFr1 = tkinter.Button(frRoot, text="同意",command=acc)
    btnFr1.place(x=120,y=68,height=25,width=120)
    btnFr2 = tkinter.Button(frRoot, text="拒绝",command=turnDown)
    btnFr2.place(x=260,y=68,height=25,width=120)
    frRoot.mainloop() 
    if cnt==1:
        return sta
 



a = friendRequest("hdh")
print(a)
=======

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

>>>>>>> 3470c5a1fa6233f0377e2fd06613661c8046a924
