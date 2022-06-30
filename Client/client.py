# encoding: utf-8
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage, filedialog
import Client_Network as cn


IP = ''
ID = '' #用户ID
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = {}  # 在线用户列表
chat = ''  # 聊天对象id, 默认为群聊
f_s = 1 # 代表朋友和陌生人之间的分隔位置


# 连接服务器
def connectS():
    cn.connect_server()
    ipRoot.destroy()


# 登录按钮
def login(*args):
    global IP, user, data
    # ~~~~~~~~~~~~~~客户端只需要服务器的ip，端口号是固定的~~~~~~~~~~~~~！！
    # IP= entryIP.get() # 获取IP
    user = entryUser.get()
    password = entryPassword.get()
    cn.login_procedure(user,password)    # 建立验证
    data = cn.rcv_one()        # 接收服务器验证信息
    print(data)
    if data["info"]["success"] == "登录成功":
        loginRoot.destroy()                  # 关闭窗口
    elif data["info"]["success"] == "无此用户":
        tkinter.messagebox.showerror('温馨提示', message='请先注册')
    elif data["info"]["success"] == "密码错误":
        tkinter.messagebox.showerror('温馨提示', message='密码错误，请重新输入')


# 注册按钮绑定函数（注册窗口GUI)
def register():
    # 注册窗口
    global loginReg
    loginReg = tkinter.Tk()
    loginReg.title('注册')
    loginReg['height'] = 300
    loginReg['width'] = 400
    loginReg.resizable(0, 0)  # 限制窗口大小

    global entryUserReg, entryPasswordReg
    User = tkinter.StringVar()
    User.set('')
    Password = tkinter.StringVar()
    Password.set('')
    
    # 用户名标签
    labelUserReg = tkinter.Label(loginReg,text="用户名:")
    labelUserReg.place(x=90, y=100, width=50,height=20)
    entryUserReg = tkinter.Entry(loginReg, width=120, textvariable=User)
    entryUserReg.place(x=145, y=95, width=150,height=30)

    # 密码标签
    labelPasswordReg = tkinter.Label(loginReg,text="密码:")
    labelPasswordReg.place(x=98, y=140, width=50,height=20)
    entryPasswordReg = tkinter.Entry(loginReg, width=120, textvariable=Password)
    entryPasswordReg.place(x=144, y=135, width=150,height=30)

    # 注册按钮
    btnConfirmReg = tkinter.Button(loginReg, text='注册', command=registerConfirm)
    btnConfirmReg.place(x=132, y=217, width=150, height=30)

    loginReg.mainloop()


# 提交注册信息及注册响应
def registerConfirm():
    global ID 
    userReg = entryUserReg.get()
    passwordReg= entryPasswordReg.get()
    cn.register_procedure(userReg,passwordReg)
    ID = cn.rcv_one()
    tkinter.messagebox.showerror('温馨提示', message='注册成功\n您的ID是: '+str(ID['receive']))
    loginReg.destroy()


def makeFriend(event):
    print(listboxFriend.get(listboxFriend.curselection()))


# 创建右键菜单
def showPopoutMenu(w, menu):
    def popout(event):
        menu.post(event.x + w.winfo_rootx(), event.y + w.winfo_rooty()) 
        w.update() 
    w.bind('<Button-2>', popout)


# 发送表情
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    # s.send(mes.encode())#####
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


# 选择文件
def chooseFile():
    global selectFilePath
    selected_file_path = filedialog.askopenfilename()  # 使用askopenfilename函数选择单个文件
    print(selected_file_path)
    selectFilePath.set(selected_file_path)


# 发送文件
def sendFile():
    global fileRoot
    fileRoot = tkinter.Toplevel()
    fileRoot.title("选择文件")
    fileRoot['height'] = 100
    fileRoot['width'] = 500
    fileRoot.resizable(0,0)
    labelFile = tkinter.Label(fileRoot, text="请选择要发送的文件")
    labelFile.place(x=5,y=10,height=20,width=200)
    entryFile = tkinter.Entry(fileRoot,width=400, textvariable=selectFilePath)
    entryFile.place(x=50,y=30,height=30,width=350)
    btnFileChoose = tkinter.Button(fileRoot, text="选择文件",command=chooseFile)
    btnFileChoose.place(x=410,y=25,height=40,width=70)
    btnFileConfirm = tkinter.Button(fileRoot, text="确定",command=confirmFile)
    btnFileConfirm.place(x=200,y=68,height=25,width=120)

    fileRoot.mainloop()


# 确认发送文件
def confirmFile():
    fileRoot.destroy()


# 发送图片
def sendPicture():
    global picRoot
    picRoot = tkinter.Toplevel()
    picRoot.title("选择图片")
    picRoot['height'] = 100
    picRoot['width'] = 500
    picRoot.resizable(0,0)
    labelPic = tkinter.Label(picRoot, text="请选择要发送的图片")
    labelPic.place(x=5,y=10,height=20,width=200)
    entryPic = tkinter.Entry(picRoot,width=400, textvariable=selectFilePath)
    entryPic.place(x=50,y=30,height=30,width=350)
    btnPicChoose = tkinter.Button(picRoot, text="选择图片",command=chooseFile)
    btnPicChoose.place(x=410,y=25,height=40,width=70)
    btnPicConfirm = tkinter.Button(picRoot, text="确定",command=confirmPic)
    btnPicConfirm.place(x=200,y=68,height=25,width=120)

    picRoot.mainloop()

# 选择图片函数 用 选择文件函数代替即可

# 确认发送图片
def confirmPic():
    picRoot.destroy()


# 获取当前聊天对象(包括群聊和私聊对象)
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listboxFriend.curselection()
    print(indexs)
    index = indexs[0]
    if index >= 0:
        temp = listboxFriend.get(index)
        chat = temp.split('|')[1]
        # 修改客户端名称
        if chat == '000000': #群聊id=000000
            root.title(user+'在群聊')
            return
    ti = user + '  -->  ' + users[chat].contact_name
    root.title(ti)


# 创建发送窗口
def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('【群发】')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('温馨提示', message='没有聊天对象!')
        return
    if chat == user:
        tkinter.messagebox.showerror('温馨提示', message='自己不能和自己进行对话!')
        return
    mes = entryText.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    # s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 菜单栏函数
def do_job():
    pass


# 好友请求弹窗
def acc(): # 同意好友请求
    global sta, cnt
    sta = True
    cnt=1
    frRoot.destroy()


def turnDown(): #拒绝好友请求
    global sta,cnt
    sta = False
    cnt=1
    frRoot.destroy()


def friendRequest(stranger):#来自名为stranger的人的好友请求
    global sta,frRoot,cnt
    sta = bool()
    cnt = int()
    frRoot = tkinter.Toplevel()
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


# 一对一聊天消息显示(接收到的)
def oneRecieve(sender, content, type):   # sender是发送者,content是发送内容,type是发送类型
    global listbox  # listbox是消息框,往里写消息
    if chat == sender: # chat是当前消息框的人的ID,如果正显示对应聊天窗口,则显示消息内容
        if sender != ID['receive']: #如果不是我发送的
            if type == 'message': # 如果是文字
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                listbox.insert(tkinter.END, content,'green')
            elif type == 'pic': # 如果是图片
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                photo = PhotoImage(file=str(content))
                listbox.image_create(tkinter.END, image=photo)
            elif type == 'file': # 如果是文件
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
                #listbox.image_create(tkinter.END, image=photo)
        else:
            if type == 'message': # 如果是文字
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                listbox.insert(tkinter.END, content,'green')
            elif type == 'pic': # 如果是图片
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                photo = PhotoImage(file=str(content))
                listbox.image_create(tkinter.END, image=photo)
            elif type == 'file': # 如果是文件
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
                #listbox.image_create(tkinter.END, image=photo)


# 群聊消息展示(接收到的)
def groupRecieve(sender,content,type):  # sender是正在聊天的人
    global listbox  # listbox是消息框,往里写消息
    if chat == "000000":     # chat是当前消息框的人的ID,如果正显示群聊窗口,则显示消息内容
        if sender != ID['receive']: #如果不是我发送的
            if type == 'message': # 如果是文字
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                listbox.insert(tkinter.END, content,'green')
            elif type == 'pic': # 如果是图片
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                photo = PhotoImage(file=str(content))
                listbox.image_create(tkinter.END, image=photo)
            elif type == 'file': # 如果是文件
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
                #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
                #listbox.image_create(tkinter.END, image=photo)
        else:
            if type == 'message': # 如果是文字
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                listbox.insert(tkinter.END, content,'green')
            elif type == 'pic': # 如果是图片
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                photo = PhotoImage(file=str(content))
                listbox.image_create(tkinter.END, image=photo)
            elif type == 'file': # 如果是文件
                listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'blue')
                #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
                #listbox.image_create(tkinter.END, image=photo)



# 聊天列表移除下线用户
def removeList(logout_user):
    global listboxFriend
    # 重新绘制聊天列表
    listboxFriend.delete(0, tkinter.END) # 清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))

# 聊天列表显示新上线用户
def addList(login_user):
    global listboxFriend
    # 重新绘制聊天列表
    listboxFriend.delete(0, tkinter.END) # 清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))
    #弹窗


# 聊天框里面显示图片
def showPic(file_path): # direction用于判断发送方向
    global listbox
    photo = PhotoImage(file=str(file_path))
    listbox.image_create(tkinter.END, image=photo)



# 显示聊天列表(第一个是群聊,然后是在线好友,然后是在线陌生人)
def showList(users):
    global listboxFriend
    listboxFriend.delete(0,tkinter.END) #清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))

# ******************************** GUI **************************************#

# 初始化连接窗口
ipRoot = tkinter.Tk()
ipRoot.title('选择IP')
ipRoot['height'] = 200
ipRoot['width'] =  400
ipRoot.resizable(0, 0)

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1')  # 默认显示的ip和端口

entry_ip = tkinter.Entry(ipRoot, width=120, textvariable=IP1)
entry_ip.place(x=145, y=95, width=150, height=30)
btnip = tkinter.Button(ipRoot, text="连接", command=connectS)
btnip.place(x=198, y=130, width=60, height=25)

ipRoot.mainloop()


# 登陆窗口
loginRoot = tkinter.Tk()
loginRoot.title('聊天室')
loginRoot['height'] = 300
loginRoot['width'] = 400
loginRoot.resizable(0, 0)  # 限制窗口大小

user = tkinter.StringVar()
user.set('')
password = tkinter.StringVar()
password.set('')

labelUser = tkinter.Label(loginRoot,text="用户ID:") # 用户名标签
labelUser.place(x=86, y=100, width=50,height=20)
entryUser = tkinter.Entry(loginRoot, width=120, textvariable=user)
entryUser.place(x=145, y=95, width=150,height=30)

labelPassword = tkinter.Label(loginRoot,text="密码:") # 密码标签
labelPassword.place(x=98, y=140, width=50,height=20)
entryPassword = tkinter.Entry(loginRoot, width=120, textvariable=password)
entryPassword.place(x=144, y=135, width=150,height=30)

"""#服务器IP标签
labelIP = tkinter.Label(loginRoot,text=" IP地址:")
labelIP.place(x=74, y=180, width=80,height=20)
entryIP = tkinter.Entry(loginRoot, width=120, textvariable=IP1)
entryIP.place(x=144, y=175, width=150,height=30)"""


loginRoot.bind('<Return>', login)            # 回车绑定登录功能
btnLogin = tkinter.Button(loginRoot, text='登录', command=login)
btnLogin.place(x=132, y=217, width=150, height=30)

btnRegister = tkinter.Button(loginRoot, text='注册', command=register)
btnRegister.place(x=132, y=250, width=150, height=30)

# 显示登录窗口
loginRoot.mainloop()

# *************************** 以上为登录&注册窗口 **********************************#

# *************************** 以下为主界面窗口 **********************************#

# 创建主页面
root = tkinter.Tk()
root.title(user) # +user
root['height'] = 550
root['width'] = 800
root.resizable(0,0)

# 创建在线用户列表
listboxFriend = tkinter.Listbox(root,height='20',bg='lightgrey',highlightbackground='white',yscrollcommand=True,font=('Times',24))
listboxFriend.place(x=0,y=0,width=180,height=550)

listboxFriend.delete(0,tkinter.END) # 这一段是随便填的，到时候可以直接用showList函数
for i in ['【群发】|123','a|1234','b|2345','c|3456','d|4567','e|5678']:
    listboxFriend.insert(tkinter.END,i)

menuFriend = tkinter.Menu() # 右键菜单
menuFriend.add_cascade(label="添加好友")
menuFriend.add_cascade(label="私聊")
showPopoutMenu(listboxFriend,menuFriend)


# 创建输入窗口
a = tkinter.StringVar()
a.set('')
entryText = tkinter.Entry(root, bg='lightblue',textvariable=a)
entryText.place(x=181, y=405, width=620, height=110)


# 创建消息窗口
listbox = ScrolledText(root,relief="solid",bd=1)
listbox.place(x=181,y=0,width=620,height=375)

selectFilePath = tkinter.StringVar()
selectFilePath.set('')

# 在显示用户列表框上设置绑定事件
listboxFriend.bind('<ButtonRelease-1>', private)

p1 = tkinter.PhotoImage(file='media/emoji.png')
p2 = tkinter.PhotoImage(file='media/file.png')
p3 = tkinter.PhotoImage(file='media/picture.png')
p4 = tkinter.PhotoImage(file='media/e1.png')
p5 = tkinter.PhotoImage(file='media/e2.png')
p6 = tkinter.PhotoImage(file='media/e3.png')
p7 = tkinter.PhotoImage(file='media/e4.png')
dicEmoji = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0  # 判断表情面板开关的标志

# 创建按钮
btnEmoji = eBut = tkinter.Button(root,image=p1, command=sendEmoji)
btnEmoji.place(x=183,y=374,width=30,height=30)
btnFile = eBut = tkinter.Button(root,image=p2, command=sendFile)
btnFile.place(x=213,y=374,width=30,height=30)
btnPicture = eBut = tkinter.Button(root,image=p3, command=sendPicture)
btnPicture.place(x=243,y=374,width=30,height=30)

# 发送窗口相关
btnSend = tkinter.Button(root, text='发送', command=send)
btnSend.place(x=670, y=513, width=120, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息


# 创建菜单栏
menubar = tkinter.Menu(root)
filemenu = tkinter.Menu(menubar, tearoff=0)

menubar.add_cascade(label='Chat', menu=filemenu)
filemenu.add_command(label='版本', command=do_job)
filemenu.add_command(label='声明', command=do_job)
filemenu.add_separator()#分割线
filemenu.add_command(label='退出', command=root.quit)# 退出

editmenu = tkinter.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Edit', menu=editmenu)
#editmenu.add_command(label='Cut', command=do_job)
editmenu.add_command(label='Copy', command=do_job)
editmenu.add_command(label='Paste', command=do_job)

"""minemenu = tkinter.Menu(menubar, tearoff=0)
menubar.add_cascade(label='mine', menu=minemenu)
#editmenu.add_command(label='Cut', command=do_job)
minemenu.add_command(label='好友申请', command=do_job)"""

"""submenu = tkinter.Menu(filemenu)
filemenu.add_cascade(label='Import', menu=submenu, underline=0)
submenu.add_command(label="Submenu1", command=do_job)"""

root.config(menu=menubar)

# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')

#显示主页面
root.mainloop()