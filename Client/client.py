# encoding: utf-8
from collections import UserString
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
#import Client_Network as cn


from pandas_datareader import test
from sqlalchemy import true  # 导入多行文本框用到的包

IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '【群发】'  # 聊天对象, 默认为群聊



#cn.connect_server() 初始化连接
#cn.connect_file_rcv() 初始化连接


# 登陆窗口
loginRoot = tkinter.Tk()
loginRoot.title('聊天室')
loginRoot['height'] = 300
loginRoot['width'] = 400
loginRoot.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:8888')  # 默认显示的ip和端口
user = tkinter.StringVar()
user.set('请输入用户名')
Password = tkinter.StringVar()
Password.set('请输入密码')

#用户名标签
labelUser = tkinter.Label(loginRoot,text="用户名:")
labelUser.place(x=90, y=100, width=50,height=20)
entryUser = tkinter.Entry(loginRoot, width=120, textvariable=user)
entryUser.place(x=145, y=95, width=150,height=30)

#密码标签
labelPassword = tkinter.Label(loginRoot,text="密码:")
labelPassword.place(x=98, y=140, width=50,height=20)
entryPassword = tkinter.Entry(loginRoot, width=120, textvariable=Password)
entryPassword.place(x=144, y=135, width=150,height=30)

#服务器IP标签
labelIP = tkinter.Label(loginRoot,text="地址:端口:")
labelIP.place(x=68, y=180, width=80,height=20)
entryIP = tkinter.Entry(loginRoot, width=120, textvariable=Password)
entryIP.place(x=144, y=175, width=150,height=30)

#登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)                     # 端口号需要为int类型
    user = entryUser.get()
    password = entryPassword.get()
    data = cn.login_procedure(user,password)    #建立验证
    if data["info"]["success"] == "登陆成功":
        loginRoot.destroy()                  # 关闭窗口
    elif data["info"]["success"] == "无此用户":
        tkinter.messagebox.showerror('温馨提示', message='请先注册')
    elif data["info"]["success"] == "密码错误":
        tkinter.messagebox.showerror('温馨提示', message='密码错误，请重新输入')


def register():
    #注册窗口
    global loginReg
    loginReg = tkinter.Tk()
    loginReg.title('注册')
    loginReg['height'] = 300
    loginReg['width'] = 400
    loginReg.resizable(0, 0)  # 限制窗口大小

    #用户名标签
    labelUserReg = tkinter.Label(loginReg,text="用户名:")
    labelUserReg.place(x=90, y=100, width=50,height=20)
    entryUserReg = tkinter.Entry(loginReg, width=120, textvariable=user)
    entryUserReg.place(x=145, y=95, width=150,height=30)

    #密码标签
    labelPasswordReg = tkinter.Label(loginReg,text="密码:")
    labelPasswordReg.place(x=98, y=140, width=50,height=20)
    entryPasswordReg = tkinter.Entry(loginReg, width=120, textvariable=Password)
    entryPasswordReg.place(x=144, y=135, width=150,height=30)

    #注册按钮
    btnConfirmReg = tkinter.Button(loginReg, text='注册', command=registerConfirm)
    btnConfirmReg.place(x=132, y=217, width=150, height=30)

    global userReg,passwordReg
    userReg = entryUserReg.get()
    password= entryPasswordReg.get()

    loginReg.mainloop()

#提交注册信息
def registerConfirm():
    tkinter.messagebox.showerror('温馨提示', message='注册成功')
    loginReg.destroy()



loginRoot.bind('<Return>', login)            # 回车绑定登录功能
btnLogin = tkinter.Button(loginRoot, text='登录', command=login)
btnLogin.place(x=132, y=217, width=150, height=30)

btnRegister = tkinter.Button(loginRoot, text='注册', command=register)
btnRegister.place(x=132, y=250, width=150, height=30)

#显示登录窗口
loginRoot.mainloop()


#创建主页面
root = tkinter.Tk()
root.title("的网络聊天") #+user
root['height'] = 550
root['width'] = 800
root.resizable(0,0)

#创建多行文本框——显示在线用户
listboxFriend = tkinter.Listbox(root,height='20',bg='lightgrey',highlightbackground='white',yscrollcommand=True,font=('Times',24))
listboxFriend.place(x=0,y=0,width=180,height=550)

listboxFriend.delete(0,tkinter.END)
for i in ['a','b','c','d','e']:
    listboxFriend.insert(tkinter.END,i)

def makeFriend(event):
    print(listboxFriend.get(listboxFriend.curselection()))

#创建右键菜单
def showPopoutMenu(w, menu):
    def popout(event):
        menu.post(event.x + w.winfo_rootx(), event.y + w.winfo_rooty()) 
        w.update() 
    w.bind('<Button-2>', popout) 

menuFriend = tkinter.Menu()
menuFriend.add_cascade(label="添加好友")
menuFriend.add_cascade(label="私聊")
showPopoutMenu(listboxFriend,menuFriend)


#创建输入窗口和关联变量
a = tkinter.StringVar()
a.set('')
entryText = tkinter.Entry(root, bg='lightblue',textvariable=a)
entryText.place(x=181, y=401, width=620, height=110)



# 发送表情
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    #s.send(mes.encode())#####
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0

# 四个对应的函数
def bb1():
    mark('aa**')

def bb2():
    mark('bb**')

def bb3():
    mark('cc**')

def bb4():
    mark('dd**')

def sendEmoji():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p4,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p5,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p6,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p7,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=185, y=330)
        b2.place(x=255, y=330)
        b3.place(x=325, y=330)
        b4.place(x=395, y=330)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()

#发送文件
def sendFile():
    pass

#发送图片
def sendPicture():
    pass


p1 = tkinter.PhotoImage(file='media/emoji.png')
p2 = tkinter.PhotoImage(file='media/file.png')
p3 = tkinter.PhotoImage(file='media/picture.png')
p4 = tkinter.PhotoImage(file='media/e1.png')
p5 = tkinter.PhotoImage(file='media/e2.png')
p6 = tkinter.PhotoImage(file='media/e3.png')
p7 = tkinter.PhotoImage(file='media/e4.png')
dicEmoji = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0  # 判断表情面板开关的标志

#创建按钮
btnEmoji = eBut = tkinter.Button(root,image=p1, command=sendEmoji)
btnEmoji.place(x=183,y=374,width=30,height=30)
btnFile = eBut = tkinter.Button(root,image=p2, command=sendFile)
btnFile.place(x=213,y=374,width=30,height=30)
btnPicture = eBut = tkinter.Button(root,image=p3, command=sendPicture)
btnPicture.place(x=243,y=374,width=30,height=30)

#创建发送窗口
def send():
    print("kick your as")

btnSend = tkinter.Button(root, text='发送', command=send)
btnSend.place(x=670, y=513, width=120, height=30)


#显示主页面
root.mainloop()