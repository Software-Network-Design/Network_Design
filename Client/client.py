# encoding: utf-8
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
import Client_Network as cn


from pandas_datareader import test  # 导入多行文本框用到的包

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
Name = tkinter.StringVar()
Name.set('请输入用户名')
Password = tkinter.StringVar()
Password.set('请输入密码')

#用户名标签
labelName = tkinter.Label(loginRoot,text="用户名:")
labelName.place(x=90, y=100, width=50,height=20)
entryName = tkinter.Entry(loginRoot, width=120, textvariable=Name)
entryName.place(x=145, y=95, width=150,height=30)

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
    user = entryName.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入的用户名！')
    else:
        loginRoot.destroy()                  # 关闭窗口


#注册按钮


#显示登录窗口
loginRoot.mainloop()