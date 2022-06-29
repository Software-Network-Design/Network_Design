
import tkinter 
from tkinter import filedialog

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
    frRoot = tkinter.Tk()
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