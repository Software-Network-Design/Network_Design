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
# 用户-正在发送对象表
send_receive = {}
# 用户接收文件锁
receive_user_lock = {}
# 文件传输等待时间
waitingTime = 10

lock2 = threading.Lock()

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
    global que, users, lock, receive_user_lock
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
                #print(type(request))
                request = request.decode('utf-8')
                #print(type(request))
                #print(request)
                request = json.loads(request)
                #print(type(request))
                #print(request)
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
                                ''''
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
                                '''
                                for online_user in users:
                                    upline_message = {}
                                    upline_message['send'] = user_id
                                    upline_message['type'] = 8
                                    upline_message['info'] = {
                                        'user_id': user_id,
                                        'user_name': user_name,
                                        'type': ''
                                    }
                                    print(online_user)
                                    upline_message['receive'] = online_user[1]
                                    print('who received:')
                                    print(upline_message['receive'])
                                    sql2 = "select * from User_Friends where (user1_id = '%s' and user2_id = '%s') or (user1_id = '%s' and user2_id = '%s')" %(user_id, online_user[1], online_user[1], user_id)
                                    cursor.execute(sql2)
                                    if_friends = cursor.fetchall()
                                    # 是陌生人
                                    if not if_friends:
                                        upline_message['info']['type'] = 'stranger'
                                        stranger = {
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        message['info']['strangers'].append(stranger)
                                    # 是好友
                                    else:
                                        upline_message['info']['type'] = 'friend'

                                        friend = {
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        message['info']['friends'].append(friend)
                                    
                                    # 发送上线消息
                                    print('message')
                                    print(upline_message)
                                    self.save_data(upline_message)

                                # 将该用户加入在线用户列表
                                users.append([conn, user_id, user_name, addr,'']) 
                                receive_user_lock[user_id] = [threading.Lock(),time.time()]
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
            que.put(message)
        except Exception as e:
            print(e)
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
                message1 = json.dumps(message, ensure_ascii=False)    
                message2 = message1.encode('utf-8')
                # 群发消息
                if type == 4 or type == 5 or type == 16:
                    for online_user in users:
                        if online_user[1] != send:
                            online_user[0].send(message2)
                # 私发消息
                else:
                    for online_user in users:
                        if online_user[1] == receive:
                            online_user[0].send(message2)


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
    global fileque, users, lock, send_receive, receive_user_lock
    def __init__(self):
        threading.Thread.__init__(self)
        self.addr = (HOST, File_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # addr ——— (host,port)
    # conn ——— socket
    def connect(self, conn, addr):
        try:
            print("建立了文件连接！")
            while True:
                request = conn.recv(1024)
                if not request:
                    break
                #print('现在接收的是' + str(request))
                try:
                    request = request.decode('utf-8')
                    request = json.loads(request)
                except:
                    pass
                finally:
                    pass
                if(isinstance(request,dict)):

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

                        if receive == '':
                            group_send = True
                        else:
                            group_send = False

                        if(not group_send and request['info'] == 'start sending'):          #为接收客户端加锁
                            receive_user_lock[receive][0].acquire()
                            receive_user_lock[receive][1] = time.time()
                        elif(not group_send and request['info'] == 'complete'):
                            receive_user_lock[receive][0].release()

                        send_receive[send] = receive
                        is_online = 0
                        

                        for online_user in users:
                            if online_user[1] == receive:
                                is_online = 1
                        if(not is_online and not group_send):
                            print("用户不在线！")
                        elif(not group_send):
                            message['isGroup'] = False
                            self.save_data(message)
                            
                        else:   #群发
                            if(request['info'] == 'start sending'):
                                for online_user in users:
                                    if(online_user[1] != send):
                                        receive_user_lock[online_user[1]][0].acquire()
                                        receive_user_lock[online_user[1]][1] = time.time() + 3*waitingTime
                                        send_message = message.copy()
                                        send_message['receive'] = online_user[1]
                                        send_message['isGroup'] = True
                                        self.save_data(send_message)
                            elif(request['info'] == 'complete'):
                                for online_user in users:
                                    if(online_user[1] != send):
                                        receive_user_lock[online_user[1]][0].release()
                                        send_message = message.copy()
                                        send_message['receive'] = online_user[1]
                                        send_message['isGroup'] = True
                                        self.save_data(send_message)
                    elif request['type'] == 1:
                        print("文件服务器登录信息")
                        user_id = request['send']
                        for online_user in users:
                            if(online_user[1] == user_id):
                                online_user[4] = conn
                                break
                    # 文件或图片内容
                elif(isinstance(request,str)):
                    print("文件头信息")
                    send_id = 0 
                    #receive_conn = None
                    for online_user in users:
                        if(conn == online_user[4]):
                            send_id = online_user[1]
                    receive_id = send_receive[send_id]
                    request = request.encode('utf-8')
                    message = {
                        'send': send_id,
                        'receive': receive_id,
                        'info': request,
                        'type':99
                    }
                    if(receive_id == ''):
                        for online_user in users:
                            if(online_user[1] != send):
                                send_message = message.copy()
                                send_message['receive'] = online_user[1]
                                self.save_data(send_message)
                    else:
                        self.save_data(message)
                else:
                    print("文件碎片")
                    send_id = 0 
                    #receive_conn = None
                    for online_user in users:
                        if(conn == online_user[4]):
                            send_id = online_user[1]
                    receive_id = send_receive[send_id]
                    message = {
                        'send': send_id,
                        'receive': receive_id,
                        'info': request,
                        'type':99
                    }
                    if(receive_id == ''):
                        for online_user in users:
                            if(online_user[1] != send):
                                send_message = message.copy()
                                send_message['receive'] = online_user[1]
                                self.save_data(send_message)
                    else:
                        self.save_data(message)
        # 断开连接
        except Exception as e:
            print("异常为：%s"%e)
        finally:
            conn.close()
            print('用户下线或服务器出错')

    # 将聊天消息保存到队列
    def save_data(self, message):
        lock.acquire()
        try:
            fileque.put((message))
        finally:
            lock.release()

    # 将队列中消息转发
    def send_data(self):
        while True:
            if not fileque.empty():
                message = fileque.get()
                send = message['send']
                receive = message['receive']
                info = message['info']
                type = message['type']
                if(type == 99):
                    for online_user in users:
                        if online_user[1] == receive:
                            print('现在发送的是' + str(message))
                            online_user[4].send(info)
                else:
                    isGroup = message['isGroup']
                    if isGroup:
                        message['receive'] = ''
                    message = json.dumps(message, ensure_ascii=False)
                    message = message.encode('utf-8')
                    for online_user in users:
                        if online_user[1] == receive:
                            sleep(1)
                            print('现在发送的是' + str(message) + '真实receive为:' + str(receive))
                            online_user[4].send(message)
                            sleep(1)
                            break

            #sleep(1)
    def check_time(self):
        global receive_user_lock
        global waitingTime
        nowtime = time.time()
        for key in receive_user_lock.keys():
            if (nowtime - receive_user_lock[key][1] > waitingTime):
                receive_user_lock[key][0].release
    
    def run(self):
        self.socket.bind((HOST, File_PORT))
        self.socket.listen(Max)
        print('文件服务器正在运行中...')
        q = threading.Thread(target=self.send_data)
        q.start()
        c = threading.Thread(target=self.check_time)
        c.start()
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