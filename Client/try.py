import tkinter


#更改个人信息确认
def ciConfirm():
    ciRoot.destroy()
    pass

def changeName():
    pass

def changePassword():
    pass

#更改个人信息
def changeInformation():
    global ciRoot
    ciRoot = tkinter.Tk()
    ciRoot.title("更改个人信息")
    ciRoot['height'] = 300
    ciRoot['width'] = 400
    ciRoot.resizable(0,0)
    labelCi1 = tkinter.Label(ciRoot, text="请修改您的用户名:")
    newName = tkinter.StringVar()
    labelCi1.place(x=20,y=50,height=20,width=200)
    entryCi1 = tkinter.Entry(ciRoot, width=220, textvariable=newName)
    entryCi1.place(x=60,y=70,height=30,width=220)
    labelCi2 = tkinter.Label(ciRoot, text="请修改您的密码:")
    newPassword = tkinter.StringVar()
    labelCi2.place(x=20,y=130,height=20,width=200)
    entryCi2 = tkinter.Entry(ciRoot, width=220, textvariable=newPassword)
    entryCi2.place(x=60,y=150,height=30,width=220)
    btnci1 = tkinter.Button(ciRoot, text="修改用户名", command=changeName)
    btnci1.place(x=300, y=72, height=25, width=75)
    btnci2 = tkinter.Button(ciRoot, text="修改密码", command=changePassword)
    btnci2.place(x=300, y=152, height=25, width=75)
    btnci3 = tkinter.Button(ciRoot, text="完成", command=ciConfirm)
    btnci3.place(x=140, y=220, height=35, width=120)

    ciRoot.mainloop() 

changeInformation()

