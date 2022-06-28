from email import message
import json
import socket
import sys
import threading
import time
import pymysql
import queue
import random
from server_config import *

# message --- json格式信息 packet --- (addr,message)
# addr --- (host,port)

# 数据库连接
db = pymysql.connect(host='nas.boeing773er.site', port=49156, user='root', passwd='q1w2e3r4', db='Chat_Program', charset='utf8')
cursor = db.cursor()
# 用于存放客户端发送的信息的队列
que = queue.Queue()                
# 用于存放在线用户的信息  [conn, user_id, user_name, addr]             
users = []          
# 创建锁, 防止多个线程写入数据的顺序打乱                     
lock = threading.Lock()                         

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
                request = json.loads(request.decode('utf-8'))
                if not request:
                    break
                # 处理之后接收到的各类型消息
                else:
                    print(type(request))
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
                                'strangers': {
                                    'strangers_num': 0
                                },
                                'friends': {
                                    'friends_num': 0
                                }
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
                                print('登陆成功')
                                message['info']['success'] = '登陆成功'
                                # 遍历在线用户，好友加入friends，陌生人加入strangers
                                friends_num = 0
                                strangers_num = 0
                                #好友上线消息
                                upline_message = {
                                    'send': 'server',
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
                                        message['info']['friends']['stranger'+str(strangers_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        strangers_num += 1
                                    # 是好友
                                    else:
                                        upline_message['info']['type'] = 'friend'
                                        message['info']['friends']['friend'+str(friends_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        friends_num += 1
                                    # 发送上线消息
                                    self.save_data(upline_message)
                                # 记录好友、陌生人数量    
                                message['info']['friends']['friends_num'] = friends_num
                                message['info']['friends']['strangers_num'] = strangers_num
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
                    #好友请求消息
                    elif request['type'] == 9:
                        print('好友请求')
                        friend_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 9,
                            'info': ''        
                        }
                        friend_message['receive'] = request['info']
                        friend_message['info'] = request['send']
                        user_id = request['info']
                        apply_id = request['send']
                        sql = "select * from User where user_id = '%s'" %(apply_id)
                        sql1 = "SELECT * FROM Chat_Program.User_Friends where user1_id = '%s'" %(user_id)
                        sql2 = "SELECT * FROM Chat_Program.User_Friends where user2_id = '%s'" %(user_id)
                        try:
                            cursor.execute(sql)
                            users = cursor.fetchone()
                            cursor.execute(sql1)
                            pairs1 = cursor.fetchone()
                            cursor.execute(sql2)
                            pairs2 = cursor.fetchone()
                            exsist = 0
                            already_friend = 0
                            for user in users:
                                if(user_id == user[0]):
                                    exist = 1
                            for pair in pairs1:
                                if(apply_id == pair[1]):
                                    already_friend = 1
                                    break
                            for pair in pairs2:
                                if(apply_id == pair[0]):
                                    already_friend = 1
                                    break
                            if(exist == 0):
                                print("添加好友失败。不存在该用户。")
                            elif(already_friend == 1):
                                print("已经为好友。请勿重复添加。")
                            else:
                                self.save_data(friend_message)
                        except:
                            pass
                    #回复好友请求消息
                    elif request['type'] == 10:
                        print('回复好友请求')
                        friend_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 10,
                            'info': {
                                'agree':'',
                                'user_id':''
                            }        
                        }
                        friend_message['receive'] = request['send']
                        friend_message['info']['agree'] = request['info']['agree']
                        friend_message['info']['user_id'] = request['info']['agree']
                        user_id = request['info']['user_id']
                        friend_id = request['send']
                        sql = "INSERT INTO `Chat_Program`.`User_Friends` (`user1_id`, `user2_id`) VALUES ('%s', '%s');"%(user_id)(friend_id)
                        try:
                            cursor.execute(sql)
                            self.save_data(friend_message)
                        except:
                            pass
                    elif request['type'] == 11:
                        print('修改个人信息')
                        correct_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 11,
                            'info': {
                                'PU':'',
                                'NewInf':''
                            }        
                        }
                        correct_message['receive'] = request['send']
                        correct_message['PU'] = request['PU']
                        correct_message['NewInf'] = request['NewInf']
                        user_id = request['send']
                        New_Inf = request['info']['NewInf']
                        if(request['PU'] == 0):
                            sql = "UPDATE `Chat_Program`.`User` SET `user_pwd` = '%s' WHERE (`user_id` = '%s');"%(New_Inf)(user_id)
                        else:
                            sql = "UPDATE `Chat_Program`.`User` SET `name` = '%s' WHERE (`user_id` = '%s');"%(New_Inf)(user_id)
                        try:
                            cursor.execute(sql)
                            self.save_data(correct_message)
                        except:
                            pass
                    # 注册消息                     
                    elif request['type'] == 13:
                        print(type(request))
                        print('注册')
                        register_message = {
                            'send': 'server',
                            'receive': '',
                            'type': 14,
                            'info': ''
                        }
                        print(type(request))
                        user_name = request['info']['user_name']
                        register_message['info'] = user_name
                        user_pwd = request['info']['user_pwd']
                        user_id = register(user_name, user_pwd)
                        register_message['receive'] = user_id
                        register_message = json.dumps(register_message, ensure_ascii=False)
                        conn.send(register_message.encode('utf-8'))
                        print(register_message)



                    # 其他需服务器转发的消息
                    else:
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
                #私聊消息
                if type == 3:
                    print('私聊消息')
                    for online_user in users:
                        if online_user[1] == receive:
                            message = json.dumps(message, ensure_ascii=False)
                            online_user[0].send(message.encode('utf-8'))
                            print('私聊',online_user[2],': ',message)
                # 群发消息
                elif type == 4:
                    print('群发消息')
                    for online_user in users:
                        if online_user[1] != send:
                            message = json.dumps(message, ensure_ascii=False)
                            online_user[0].send(message.encode('utf-8')) 
                            print('群发',online_user[2],': ',message)
                # 注销消息
                elif type == 5:
                    print('注销消息')
                    for online_user in users:
                        message = json.dumps(message, ensure_ascii=False)
                        online_user[0].send(message.encode('utf-8')) 
                        print('注销',online_user[2],': ',message)
                # 上线提示
                elif message['type'] == 8:
                    print('上线提示')
                    for online_user in users:
                        if online_user[1] == receive:
                            message = json.dumps(message, ensure_ascii=False)
                            online_user[0].send(message.encode('utf-8')) 
                            print('上线提醒',online_user[2],': ',message)
                else:
                    message = json.dumps(message, ensure_ascii=False)
                    online_user[0].send(message.encode('utf-8')) 
                

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
            print(addr)
            t = threading.Thread(target=self.connect, args=(conn, addr))
            t.start()
        self.socket.close()


if __name__ == '__main__':
    cserver = chat_server()
    cserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)







