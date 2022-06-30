import tkinter



def ciConfirm():
    pass


ciRoot = tkinter.Tk()
ciRoot.title("选择文件")
ciRoot['height'] = 300
ciRoot['width'] = 400
ciRoot.resizable(0,0)
labelCi1 = tkinter.Label(ciRoot, text="请修改您的用户名:")
newName = tkinter.StringVar()
labelCi1.place(x=20,y=20,height=20,width=200)
entryCi1 = tkinter.Entry(ciRoot, width=200, textvariable=newName)
entryCi1.place(x=20,y=60,height=30,width=200)
labelCi2 = tkinter.Label(ciRoot, text="请修改您的密码:")
newPassword = tkinter.StringVar()
labelCi2.place(x=20,y=100,height=20,width=200)
entryCi2 = tkinter.Entry(ciRoot, width=200, textvariable=newPassword)
entryCi2.place(x=20,y=140,height=30,width=200)


btnFr1 = tkinter.Button(ciRoot, text="同意", command=ciConfirm)
btnFr1.place(x=140, y=200, height=25, width=120)

ciRoot.mainloop() 



