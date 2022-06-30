# encoding: utf-8
from plistlib import UID
from queue import Queue
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import PhotoImage, filedialog
from tkinter import filedialog
from Contact import *
import Client_Network as cn
from Client_Network import chat_socket, file_socket, rcv_size, file_rcv
from pathlib import Path

IP = ''
ID = ''  # 用户
uID = '' #用户ID
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = {}  # 在线用户列表
chat = '000000'  # 聊天对象id, 默认为群聊
f_s = 1  # 代表朋友和陌生人之间的分隔位置
group_message_queue = Queue() #群聊信息

# 连接服务器
def connectS():
    cn.connect_server()
    ipRoot.destroy()



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
    labelUserReg = tkinter.Label(loginReg, text="用户名:")
    labelUserReg.place(x=90, y=100, width=50, height=20)
    entryUserReg = tkinter.Entry(loginReg, width=120, textvariable=User)
    entryUserReg.place(x=145, y=95, width=150, height=30)

    # 密码标签
    labelPasswordReg = tkinter.Label(loginReg, text="密码:")
    labelPasswordReg.place(x=98, y=140, width=50, height=20)
    entryPasswordReg = tkinter.Entry(loginReg, width=120, textvariable=Password)
    entryPasswordReg.place(x=144, y=135, width=150, height=30)

    # 注册按钮
    btnConfirmReg = tkinter.Button(loginReg, text='注册', command=registerConfirm)
    btnConfirmReg.place(x=132, y=217, width=150, height=30)

    loginReg.mainloop()


# 提交注册信息及注册响应
def registerConfirm():
    global ID,uID
    userReg = entryUserReg.get()
    passwordReg= entryPasswordReg.get()
    cn.register_procedure(userReg,passwordReg)
    ID = cn.rcv_one()
    uID = ID['revieve']
    tkinter.messagebox.showerror('温馨提示', message='注册成功\n您的ID是: '+str(uID))
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
    labelFile.place(x=5, y=10, height=20, width=200)
    entryFile = tkinter.Entry(fileRoot, width=400, textvariable=selectFilePath)
    entryFile.place(x=50, y=30, height=30, width=350)
    btnFileChoose = tkinter.Button(fileRoot, text="选择文件", command=chooseFile)
    btnFileChoose.place(x=410, y=25, height=40, width=70)
    btnFileConfirm = tkinter.Button(fileRoot, text="确定", command=confirmFile)
    btnFileConfirm.place(x=200, y=68, height=25, width=120)

    fileRoot.mainloop()


# 确认发送文件
def confirmFile():
    sendFile()
    fileRoot.destroy()


# 发送图片
def sendPicture():
    global picRoot
    picRoot = tkinter.Toplevel()
    picRoot.title("选择图片")
    picRoot['height'] = 100
    picRoot['width'] = 500
    picRoot.resizable(0, 0)
    labelPic = tkinter.Label(picRoot, text="请选择要发送的图片")
    labelPic.place(x=5, y=10, height=20, width=200)
    entryPic = tkinter.Entry(picRoot, width=400, textvariable=selectFilePath)
    entryPic.place(x=50, y=30, height=30, width=350)
    btnPicChoose = tkinter.Button(picRoot, text="选择图片", command=chooseFile)
    btnPicChoose.place(x=410, y=25, height=40, width=70)
    btnPicConfirm = tkinter.Button(picRoot, text="确定", command=confirmPic)
    btnPicConfirm.place(x=200, y=68, height=25, width=120)

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
        if chat == '000000':  # 群聊id=000000
            root.title(user+'在群聊')
            return
    ti = user + '  -->  ' + users[chat].contact_name
    root.title(ti)


# 菜单栏函数
def do_job():
    pass


# 好友请求弹窗
def acc(): # 同意好友请求
    global sta, cnt
    sta = True
    cnt = 1
    frRoot.destroy()


def turnDown():     # 拒绝好友请求
    global sta, cnt
    sta = False
    cnt = 1
    frRoot.destroy()


def friendRequest(stranger):    # 来自名为stranger的人的好友请求
    global sta,frRoot,cnt
    sta = bool()
    cnt = int()
    frRoot = tkinter.Toplevel()
    frRoot.title("好友申请")
    frRoot['height'] = 100
    frRoot['width'] = 500
    frRoot.resizable(0, 0)
    labelFr = tkinter.Label(frRoot, text=str(stranger)+"请求添加您为好友")
    labelFr.place(x=5, y=10, height=20, width=200)
    btnFr1 = tkinter.Button(frRoot, text="同意", command=acc)
    btnFr1.place(x=120, y=68, height=25, width=120)
    btnFr2 = tkinter.Button(frRoot, text="拒绝", command=turnDown)
    btnFr2.place(x=260, y=68, height=25, width=120)
    frRoot.mainloop() 
    if cnt == 1:
        return sta


# 一对一聊天消息显示(接收到的)
def oneRecieve(sender, content, type):   # sender是发送者,content是发送内容,type是发送类型
    global listbox  # listbox是消息框,往里写消息
    if chat == sender: # chat是当前消息框的人的ID,如果正显示对应聊天窗口,则显示消息内容
        if type == 'message': # 如果是文字
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            listbox.insert(tkinter.END, content+'\n','green')
        elif type == 'pic': # 如果是图片
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            photo = PhotoImage(file=content)
            listbox.image_create(tkinter.END, image=photo)
        elif type == 'file': # 如果是文件
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图,保存地址
            #listbox.image_create(tkinter.END, image=photo)
    elif sender == uID:
        if type == 'message': # 如果是文字
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            listbox.insert(tkinter.END, content+'\n','green')
        elif type == 'pic': # 如果是图片
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            photo = PhotoImage(file=content)
            listbox.image_create(tkinter.END, image=photo)
        elif type == 'file': # 如果是文件
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图,保存地址
            #listbox.image_create(tkinter.END, image=photo)

# 群聊消息展示(接收到的)
def groupRecieve(sender,content,type):  # sender是正在聊天的人
    global listbox  # listbox是消息框,往里写消息
    if chat == "000000":     # chat是当前消息框的人的ID,如果正显示群聊窗口,则显示消息内容
        if type == 'message': # 如果是文字
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            listbox.insert(tkinter.END, content+'\n', 'green')
        elif type == 'pic': # 如果是图片
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            photo = PhotoImage(file=content)
            listbox.image_create(tkinter.END, image=photo)
        elif type == 'file': # 如果是文件
            listbox.insert(tkinter.END,str(users[sender].contact_name)+':\n', 'green')
            #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
            #listbox.image_create(tkinter.END, image=photo)
    elif sender == uID:
        if type == 'message': # 如果是文字
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            listbox.insert(tkinter.END, content+'\n','green')
        elif type == 'pic': # 如果是图片
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            photo = PhotoImage(file=content)
            listbox.image_create(tkinter.END, image=photo)
        elif type == 'file': # 如果是文件
            listbox.insert(tkinter.END,"我"+':\n', 'blue')
            #photo = PhotoImage(file=str(content)) # 一会找一张文件的贴图
            #listbox.image_create(tkinter.END, image=photo)

# 个人消息展示（我发送的）
def oneSend(reciever, content, type):
    pass


# 聊天列表移除下线用户
def removeList(logout_user):
    global listboxFriend
    # 重新绘制聊天列表
    listboxFriend.delete(0, tkinter.END)    # 清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))


# 聊天列表显示新上线用户
def addList(login_user):
    global listboxFriend
    # 重新绘制聊天列表
    listboxFriend.delete(0, tkinter.END)     # 清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))
    # 弹窗


# 聊天框里面显示图片
def showPic(file_path): # direction用于判断发送方向
    global listbox
    photo = PhotoImage(file=str(file_path))
    listbox.image_create(tkinter.END, image=photo)


# 显示聊天列表(第一个是群聊,然后是在线好友,然后是在线陌生人)
def showList(users):
    global listboxFriend
    listboxFriend.delete(0, tkinter.END)  # 清空列表
    for key in users.keys():
        listboxFriend.insert(tkinter.END, str(users[key].contact_name)+'|'+str(users[key].contact_num))


# 创建发送
def sendText(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    print(chat)
    """if chat not in users:
        tkinter.messagebox.showerror('温馨提示', message='没有聊天对象!')
        return"""
    if chat != '000000': # 说明是私聊
        # 发送
        # TODO:a的类型不对，不是str
        cn.send_dm(uID, chat, str(a.get()), users)
        listbox.insert(tkinter.END, str('我')+':\n', 'blue')
        listbox.insert(tkinter.END, str(a.get())+'\n', 'blue')
    else: # 说明是群聊
        cn.send_group(uID, str(a.get()), group_message_queue)
        listbox.insert(tkinter.END, str('我')+':\n', 'blue')
        listbox.insert(tkinter.END, str(a.get())+'\n', 'blue')
    a.set('')  # 发送后清空文本框,a是文本框变量


def sendFile():
    print(chat)
    if chat != '000000': # 说明是私聊
        cn.send_file_procedure(uID,chat,selectFilePath,False)
        listbox.insert(tkinter.END,str('我')+':\n', 'blue')
        photo = PhotoImage(file=str(Path('media')/'filePic.png')) # 文件的贴图
        listbox.image_create(tkinter.END, image=photo)
        listbox.insert(tkinter.END, "\n文件地址:"+str(selectFilePath)+'\n', 'grey')# 文件的地址
    else: # 说明是群聊
        cn.send_file_procedure(uID,'',selectFilePath,False)
        listbox.insert(tkinter.END,str('我')+':\n', 'blue')
        photo = PhotoImage(file=str(Path('media')/'filePic.png')) # 文件的贴图
        listbox.image_create(tkinter.END, image=photo)
        listbox.insert(tkinter.END, "\n文件地址:"+str(selectFilePath)+'\n', 'grey')# 文件的地址

def sendPicture():
    print(chat)
    if chat != '000000': # 说明是私聊
        cn.send_file_procedure(uID,chat,selectFilePath,True)
        listbox.insert(tkinter.END,str('我')+':\n', 'blue')
        photo = PhotoImage(file=str(selectFilePath)) 
        listbox.image_create(tkinter.END, image=photo)
    else: # 说明是群聊
        cn.send_file_procedure(uID,'',selectFilePath,True)
        listbox.insert(tkinter.END,str('我')+':\n', 'blue')
        photo = PhotoImage(file=str(selectFilePath)) 
        listbox.image_create(tkinter.END, image=photo)


#更改个人信息确认
def ciConfirm():
    ciRoot.destroy()

#弹窗确认成功
def changeSuccess():
    tkinter.messagebox.showerror('温馨提示', message='修改成功')

#更改用户名
def changeName():
    cn.send_self_info(uID,1,str(newName.get()))

#更改密码
def changePassword():
    cn.send_self_info(uID,0,str(newPassword.get()))

#更改个人信息
def changeInformation():
    global ciRoot,newName,newPassword
    ciRoot = tkinter.Toplevel()
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

# **********************Network******************************


def init_user_list(user_dict, response_dict):
    print("in func init_user_list")
    stranger_list = response_dict['strangers']
    print(response_dict)
    stranger_count = len(stranger_list)
    friend_list = response_dict['friends']
    friend_count = len(friend_list)
    for stranger in stranger_list:
        name = stranger['user_name']
        ID = stranger['user_id']
        contact = Contact(name, ID, False)
        user_dict[ID] = contact
    for friend in friend_list:
        name = friend['user_name']
        ID = friend['user_id']
        contact = Contact(name, ID, True)
        user_dict[ID] = contact
    print(user_dict)
    return user_dict


def recv():
    while True:
        rcv_buffer = chat_socket.recv(rcv_size)
        print(rcv_buffer)
        rcv_data = json.loads(rcv_buffer.decode('utf-8'))
        print(type(rcv_data), rcv_data)
        package_type = rcv_data['type']
        # 一对一聊天消息
        if package_type == 3:
            sender = rcv_data['send']
            message = rcv_data['info']
            users[sender].message_queue.put({'send': sender, 'message': message, 'type': 'message'})
            oneRecieve(sender, message, 'message')
        # 群聊消息
        elif package_type == 4:
            sender = rcv_data['send']
            message = rcv_data['info']
            group_message_queue.put({'send': sender, 'message': message, 'type': 'message'})
            groupRecieve(sender, message, 'message')
        # 用户下线
        elif package_type == 5:
            logout_user = rcv_data['send']
            try:
                del users[logout_user]
                removeList(logout_user)
            except Exception as e:
                print(e)
                print("logout fault")
        # 用户上线
        elif package_type == 8:
            message = rcv_data['info']
            user_id = message['user_id']
            if message['type'] == 'friend':
                new_online = Contact(message['user_name'], message['user_id'], True)
            else:
                new_online = Contact(message['user_name'], message['user_id'], False)
            users[message['user_id']] = new_online
            addList(user_id)
        # 接到好友邀请
        elif package_type == 9:
            friend_request_from = rcv_data['sender']
            accept = friendRequest(friend_request_from)
            if accept:
                users[friend_request_from].is_friend = True
            cn.friend_response(uID, accept, friend_request_from)
        # 个人信息修改
        elif package_type == 15:
            pass
            # TODO:显示修改成功
        elif package_type == 16:
            person_info = rcv_data['info']
            user_name = person_info['user_name']
            user_id = person_info['user_id']
            users[user_id].contact_name = user_name
            showList(users)


def file_recv():
    print("in func file_recv")
    # while True:
    rcv_buffer = file_socket.recv(rcv_size)
    print(rcv_buffer)
    data = json.loads(rcv_buffer.decode('utf-8'))
    package_type = data['type']
    sender_id = data['send']
    # 发送文件
    if package_type == 6:
        if data['info'] == "start sending":
            # 实际上的文件接收过程
            file_path = file_rcv(is_pic=False)
            if data['receive'] == '':
                users[sender_id].message_queue.put(
                    {'send': sender_id, 'message': file_path, 'type': 'file'})
                oneRecieve(sender_id, file_path, 'file')
            else:
                group_message_queue.put(
                    {'send': sender_id, 'message': file_path, 'type': 'file'})
                groupRecieve(sender_id, file_path, 'file')
            rcv_buffer = file_socket.recv(rcv_size)
            data = json.loads(rcv_buffer.decode('utf-8'))
            if data['type'] == 6 and data['info'] == "complete":
                pass
            else:
                print("结束异常")
        else:
            print("wrong package type/info")
    # 发送图片
    elif package_type == 12:
        if data['info'] == "start sending":
            file_path = file_rcv(is_pic=True)
            if data['receive'] == '':
                users[sender_id].message_queue.put(
                    {'send': sender_id, 'message': file_path, 'type': 'pic'})
                oneRecieve(sender_id, file_path, 'pic')
            else:
                group_message_queue.put(
                    {'send': sender_id, 'message': file_path, 'type': 'pic'})
                groupRecieve(sender_id, file_path, 'pic')
            rcv_buffer = file_socket.recv(rcv_size)
            data = json.loads(rcv_buffer.decode('utf-8'))
            if data['type'] == 12 and data['info'] == "complete":
                pass
            else:
                print("结束异常")
        else:
            print("wrong package type/info")

# **********************login*************************


# 登录按钮
def login(*args):
    global IP, user, data, uID, users
    # ~~~~~~~~~~~~~~客户端只需要服务器的ip，端口号是固定的~~~~~~~~~~~~~！！
    # IP= entryIP.get() # 获取IP
    user = entryUser.get()
    uID = user
    password = entryPassword.get()
    cn.login_procedure(user, password)    # 建立验证
    data = cn.rcv_one()        # 接收服务器验证信息
    print(data)
    if data["info"]["success"] == "登录成功":
        loginRoot.destroy()                  # 关闭窗口
        cn.connect_file_rcv(uID)
        users = init_user_list(users, data['info'])
    elif data["info"]["success"] == "无此用户":
        tkinter.messagebox.showerror('温馨提示', message='请先注册')
    elif data["info"]["success"] == "密码错误":
        tkinter.messagebox.showerror('温馨提示', message='密码错误，请重新输入')


# ******************************** GUI **************************************#

# 初始化连接窗口
ipRoot = tkinter.Tk()
ipRoot.title('选择IP')
ipRoot['height'] = 200
ipRoot['width'] = 400
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

labelUser = tkinter.Label(loginRoot, text="用户ID:")  # 用户名标签
labelUser.place(x=86, y=100, width=50, height=20)
entryUser = tkinter.Entry(loginRoot, width=120, textvariable=user)
entryUser.place(x=145, y=95, width=150, height=30)

labelPassword = tkinter.Label(loginRoot, text="密码:")    # 密码标签
labelPassword.place(x=98, y=140, width=50, height=20)
entryPassword = tkinter.Entry(loginRoot, width=120, textvariable=password)
entryPassword.place(x=144, y=135, width=150, height=30)

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
root.title(user)    # +user
root['height'] = 550
root['width'] = 800
root.resizable(0, 0)

# 创建在线用户列表
listboxFriend = tkinter.Listbox(root, height='20', bg='lightgrey', highlightbackground='white',yscrollcommand=True,font=('Times',24))
listboxFriend.place(x=0, y=0, width=180, height=550)

# listboxFriend.delete(0, tkinter.END) # 这一段是随便填的，到时候可以直接用showList函数
# for i in ['【群发】|123','a|1234','b|2345','c|3456','d|4567','e|5678']:
#     listboxFriend.insert(tkinter.END, i)

showList(users)

menuFriend = tkinter.Menu()     # 右键菜单
menuFriend.add_cascade(label="添加好友")
menuFriend.add_cascade(label="私聊")
showPopoutMenu(listboxFriend, menuFriend)


# 创建输入窗口
a = tkinter.StringVar()
a.set('')
entryText = tkinter.Entry(root, bg='lightblue', textvariable=a)
entryText.place(x=181, y=405, width=620, height=110)


# 创建消息窗口
listbox = ScrolledText(root, relief="solid", bd=1)
listbox.place(x=181, y=0, width=620, height=375)

selectFilePath = tkinter.StringVar()
selectFilePath.set('')

# 在显示用户列表框上设置绑定事件
listboxFriend.bind('<ButtonRelease-1>', private)

# MacOS
p1 = tkinter.PhotoImage(file='media/emoji.png')
p2 = tkinter.PhotoImage(file='media/file.png')
p3 = tkinter.PhotoImage(file='media/picture.png')
p4 = tkinter.PhotoImage(file='media/e1.png')
p5 = tkinter.PhotoImage(file='media/e2.png')
p6 = tkinter.PhotoImage(file='media/e3.png')
p7 = tkinter.PhotoImage(file='media/e4.png')
p8 = tkinter.PhotoImage(file='media/filePic.png')

# Windows
# p1 = tkinter.PhotoImage(file=Path('../media/emoji.png'))
# p2 = tkinter.PhotoImage(file=Path('../media/file.png'))
# p3 = tkinter.PhotoImage(file=Path('../media/picture.png'))
# p4 = tkinter.PhotoImage(file=Path('../media/e1.png'))
# p5 = tkinter.PhotoImage(file=Path('../media/e2.png'))
# p6 = tkinter.PhotoImage(file=Path('../media/e3.png'))
# p7 = tkinter.PhotoImage(file=Path('../media/e4.png'))
# p8 = tkinter.PhotoImage(file=Path('../media/filePic.png')
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
btnSend = tkinter.Button(root, text='发送', command=sendText)
btnSend.place(x=670, y=513, width=120, height=30)
root.bind('<Return>', sendText)  # 绑定回车发送信息


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
editmenu.add_command(label='Copy', command=do_job)
editmenu.add_command(label='Paste', command=do_job)

minemenu = tkinter.Menu(menubar, tearoff=0)
menubar.add_cascade(label='mine', menu=minemenu)
#editmenu.add_command(label='Cut', command=do_job)
minemenu.add_command(label='更改个人信息', command=changeInformation)

"""submenu = tkinter.Menu(filemenu)
filemenu.add_cascade(label='Import', menu=submenu, underline=0)
submenu.add_command(label="Submenu1", command=do_job)"""

root.config(menu=menubar)

# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.tag_config('grey',foreground='lightgrey')

r = threading.Thread(target=recv)
r.setDaemon(True)
r.start()
print("r started")

fr = threading.Thread(target=file_recv)
fr.start()
print("fr started")

# 显示主页面
root.mainloop()

