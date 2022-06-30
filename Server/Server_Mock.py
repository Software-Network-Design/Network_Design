from email import message
import json
import socket
import sys
import threading
import time
import pymysql
import queue
import random
from time import sleep
from server_config import *

# addr --- (host,port)

# 数据库连接
db = pymysql.connect(host='nas.boeing773er.site', port=49156, user='root', passwd='q1w2e3r4', db='Chat_Program', charset='utf8')
cursor = db.cursor()
# 用于存放客户端发送的信息的队列
que = queue.Queue()
#用于存放文件队列
fileque = queue.Queue()
# 用于存放在线用户的信息  [conn, user_id, user_name, addr]             
users = []          
# 创建锁, 防止多个线程写入数据的顺序打乱                     
lock = threading.Lock()      
#用户-正在发送对象表
send_receive = {}

def register(user_name, user_pwd):
    id = str(random.randrange(100000000, 999999999))
    sql = "select * from User where user_id = '%s'" %(id)
    cursor.execute(sql)
    user = cursor.fetchone()
    # 没有被注册
    if not user:
        sql2 = "insert into User(user_id, name, user_pwd) values('%s','%s','%s')" %(id, user_name, user_pwd)
        try:
            cursor.execute(sql2)
            db.commit()
        except:
            id = ''
            db.rollback()
        return id
    else:
        register(user_name, user_pwd)

class chat_server(threading.Thread):
    # 定义为全局变量
    global que, users, lock
    def __init__(self):
        threading.Thread.__init__(self)
        self.addr = (HOST, Chat_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # addr ——— (host,port)
    # conn ——— socket
    def connect(self, conn, addr):
        try:
            while True:
                request = conn.recv(1024)
                print(type(request))
                request = request.decode('utf-8')
                print(type(request))
                print(request)
                request = json.loads(request)
                print(type(request))
                print(request)
                if not request:
                    break
                # 处理之后接收到的各类型消息
                else:
                    # 登录消息
                    if request['type'] == 1:
                        print('登陆消息')
                        # 登录请求返回消息
                        message = {
                            'send': 'server',
                            'receive': '',
                            'type': 2,
                            'info': {
                                # sucess：无此用户、密码错误、登陆成功
                                'success': '',
                                'strangers': [],
                                #{
                                    #'strangers_num': 0
                                #},
                                'friends': []
                                #{
                                    #'friends_num': 0
                                #}
                            }
                        }
                        user_id = request['info']['user_id']
                        user_pwd = request['info']['user_pwd']
                        user_name = ''
                        message['receive'] = user_id
                        sql = "select * from User where user_id = '%s'" %(user_id)
                        # print(sql)
                        try:
                            cursor.execute(sql)
                            user = cursor.fetchone()
                            user_name = user[1]
                            # 登陆成功
                            if user[2] == user_pwd:
                                print('登录成功')
                                print(1)
                                message['info']['success'] = '登录成功'
                                # 遍历在线用户，好友加入friends，陌生人加入strangers
                                friends_num = 0
                                strangers_num = 0
                                #好友上线消息
                                upline_message = {
                                    'send': user_id,
                                    'receive': '',
                                    'type': 8,
                                    'info': {
                                        'user_id': user_id,
                                        'user_name': user_name,
                                        'type': ''
                                    }
                                }
                                for online_user in users:
                                    upline_message['receive'] = online_user[1]
                                    sql2 = "select * from User_Friends where (user1_id = '%s' and user2_id = '%s') or (user1_id = '%s' and user2_id = '%s')" %(user_id, online_user[1], online_user[1], user_id)
                                    cursor.execute(sql2)
                                    if_friends = cursor.fetchall()
                                    # 是陌生人
                                    if not if_friends:
                                        upline_message['info']['type'] = 'stranger'
                                        ''''
                                        message['info']['strangers']['stranger'+str(strangers_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        strangers_num += 1
                                        '''
                                        stranger = {
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        message['info']['strangers'].append(stranger)
                                    # 是好友
                                    else:
                                        upline_message['info']['type'] = 'friend'
                                        ''''
                                        message['info']['friends']['friend'+str(friends_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        friends_num += 1
                                        '''
                                        friend = {
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        message['info']['friends'].append(friend)
                                    # 发送上线消息
                                    self.save_data(upline_message)
                                # 记录好友、陌生人数量    
                                #message['info']['friends']['friends_num'] = friends_num
                                #message['info']['strangers']['strangers_num'] = strangers_num
                                # 将该用户加入在线用户列表
                                users.append((conn, user_id, user_name, addr)) 
                            # 密码错误
                            else:
                                message['info']['success'] = '密码错误'
                        # 无此用户
                        except:
                            message['info']['success'] = '无此用户'
                        # 发送响应消息
                        message = json.dumps(message, ensure_ascii=False)
                        conn.send(message.encode('utf-8'))
                    # 好友请求消息
                    elif request['type'] == 9:
                        print('好友请求')
                        accept_user = request['receive']
                        apply_user = request['send']
                        sql = "select * from User where user_id = '%s'" %(accept_user)
                        sql1 = "select * from User_Friends where (user1_id = '%s' and user2_id = '%s') or (user1_id = '%s' and user2_id = '%s')" %(accept_user, apply_user, apply_user, accept_user)
                        cursor.execute(sql)
                        if_user = cursor.fetchone()
                        if not if_user:
                            print('用户不存在')
                        else:
                            cursor.execute(sql1)
                            pair = cursor.fetchone()
                            if not pair:
                                self.save_data(request)
                                print('好友请求发送！！！！')
                            else:
                                message = {
                                    'send': 'server',
                                    'receive': apply_user,
                                    'type': 10,
                                    'info': '已经是好友了'   
                                }
                                self.save_data(message)
                    # 回复好友请求消息
                    elif request['type'] == 10:
                        print('回复好友请求')
                        message = request
                        print(type(message))
                        print(message)
                        apply_user = message['receive']
                        accept_user = message['send']
                        agree = message['info']
                        if agree == True:
                            sql = "INSERT INTO User_Friends (user1_id, user2_id) VALUES ('%s', '%s')" %(apply_user, accept_user)
                            try:
                                cursor.execute(sql)
                                db.commit()
                                self.save_data(message)
                            except:
                                print('错误错误错误！！！！！！')
                                db.rollback()
                    # 个人信息修改
                    elif request['type'] == 11:
                        print('修改个人信息')
                        correct_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 15,
                            'info': {
                                'PU': 0,
                                'NewInf':''
                            }        
                        }
                        user_id = request['send']
                        correct_message['receive'] = user_id
                        select = request['info']['PU']
                        correct_message['info']['PU'] = select
                        New_Inf = request['info']['NewInf']
                        correct_message['info']['NewInf'] = New_Inf
                        if(select == 0):
                            sql = "UPDATE User SET user_pwd = '%s' WHERE (user_id = '%s')" %(New_Inf, user_id)
                        else:
                            sql = "UPDATE User SET name = '%s' WHERE (user_id = '%s')" %(New_Inf, user_id)
                        try:
                            cursor.execute(sql)
                            db.commit()
                            self.save_data(correct_message)
                            if select == 1:
                                modify_message = {
                                    'send': user_id,
                                    'receive': '',
                                    'type': 16,
                                    'info': {
                                        'user_id': user_id,
                                        'user_name': New_Inf
                                    }
                                }
                                self.save_data(modify_message)
                        except:
                            print('出错了')
                            db.rollback()
                    # 注册消息                     
                    elif request['type'] == 13:
                        print('注册')
                        register_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 14,
                            'info': ''
                        }
                        user_name = request['info']['user_name']
                        register_message['info'] = user_name
                        user_pwd = request['info']['user_pwd']
                        user_id = register(user_name, user_pwd)
                        register_message['receive'] = user_id
                        register_message = json.dumps(register_message, ensure_ascii=False)
                        conn.send(register_message.encode('utf-8'))
                    # 其他由服务器直接转发的消息
                    else:
                        print('其他消息')
                        self.save_data(request)
        # 断开连接
        except:
            pass
        finally:
            conn.close()
            logout_user_id = self.delUser(conn)
            logout_message = {
                'send': logout_user_id,
                'receive': '',
                'type': 5,
                'info': 'logout'
            }
            self.save_data(logout_message)
            print(logout_user_id,'断开连接！')

    # 将聊天消息保存到队列
    def save_data(self, message):
        lock.acquire()
        try:
            que.put((message))
        finally:
            lock.release()

    # 将队列中消息转发
    def send_data(self):
        while True:
            if not que.empty():
                message = que.get()
                send = message['send']
                receive = message['receive']
                type = message['type']  
                print(message)      
                # 群发消息
                if type == 4 or type == 5 or type == 8:
                    print('群发消息')
                    message = json.dumps(message, ensure_ascii=False)
                    message = message.encode('utf-8')
                    for online_user in users:
                        if online_user[1] != send:
                            
                            online_user[0].send(message) 
                # 私发消息
                else:
                    print('私发消息')
                    message = json.dumps(message, ensure_ascii=False)
                    message = message.encode('utf-8')
                    for online_user in users:
                        if online_user[1] == receive:
                            online_user[0].send(message)
                #sleep(1)

    # 用户离线后将其从users中删除
    def delUser(self, conn):
        user_id = ''
        a = 0
        for user in users:
            if user[0] == conn:
                user_id = user[1]
                users.pop(a)
                break
            a = a + 1
        return user_id
    
    def run(self):
        self.socket.bind((HOST, Chat_PORT))
        self.socket.listen(Max)
        print('聊天服务器正在运行中...')
        q = threading.Thread(target=self.send_data)
        q.start()
        while True:
            conn, addr = self.socket.accept()
            t = threading.Thread(target=self.connect, args=(conn, addr))
            t.start()
        self.socket.close()

class file_server(threading.Thread):
    # 定义为全局变量
    global fileque, users, lock, send_receive
    def __init__(self):
        threading.Thread.__init__(self)
        self.addr = (HOST, File_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # addr ——— (host,port)
    # conn ——— socket
    def connect(self, conn, addr):
        try:
            while True:
                request = conn.recv(1024)
                if not request:
                    break
                if(check_json_format(request)):
                    request = request.decode('utf-8')
                    request = json.loads(request)

                # 处理之后接收到的各类型消息
                    # 图片或文件信息
                    if request['type'] == 6 or request['type'] == 12:
                        print('图片或文件信息')
                        # 登录请求返回消息
                        #message = {
                        #    'send': '',
                        #    'receive': '',
                        #    'type': 0,
                        #    'info': ''
                        #}
                        message = request
                        receive = request['receive']
                        send = request['send']
                        is_online = 0
                        if receive_id == '':
                            group_send = 1
                        else:
                            group_send = 0
                        for online_user in users:
                            if online_user[1] == receive:
                                is_online = 1
                        if(not is_online and not group_send):
                            print("用户不在线！")
                        elif(not group_send):
                            self.save_data(message)
                            send_receive[send] = receive
                        else:
                            send_receive[send] = receive
                            for online_user in users:
                                message['receive'] = online_user[1]
                                self.save_data(message)
                        self.save_data(message)
                    # 文件或图片内容
                else:
                    send_id = 0 
                    #receive_conn = None
                    for online_user in users:
                        if(conn == online_user[0]):
                            send_id = online_user[1]
                    receive_id = send_receive[send_id]
                    message = {
                        'send': send_id,
                        'receive': receive_id,
                        'info': request,
                        'type':99
                    }
                    self.save_data(request)
        # 断开连接
        except:
            pass
        finally:
            conn.close()
            print('用户下线或服务器出错')

    # 将聊天消息保存到队列
    def save_data(self, message):
        lock.acquire()
        try:
            que.put((message))
        finally:
            lock.release()

    # 将队列中消息转发
    def send_data(self):
        while True:
            if not que.empty():
                message = que.get()
                send = message['send']
                receive = message['receive']
                info = message['info']
                type = message['type']
                if(type == 99):
                    for online_user in users:
                        if online_user[1] == receive:
                            online_user[0].send(info)
                else:
                    for online_user in users:
                        if online_user[1] == receive:
                            message = json.dumps(message, ensure_ascii=False)
                            online_user[0].send(message.encode('utf-8'))

            #sleep(1)
    
    def run(self):
        self.socket.bind((HOST, File_PORT))
        self.socket.listen(Max)
        print('文件服务器正在运行中...')
        q = threading.Thread(target=self.send_data)
        q.start()
        while True:
            conn, addr = self.socket.accept()
            t = threading.Thread(target=self.connect, args=(conn, addr))
            t.start()
        self.socket.close()

def check_json_format(raw_msg): 
    if isinstance(raw_msg, str):
        try : 
            json.loads(raw_msg, encoding= 'utf-8' ) 
        except ValueError: 
            return False 
        return True
    else:
        return False

if __name__ == '__main__':
    cserver = chat_server()
    cserver.start()
    fserver = file_server()
    fserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
        if not fserver.isAlive():
            print("File connection lost...")
            sys.exit(0)