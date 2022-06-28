from email import message
import json
import socket
import sys
import threading
import time
import pymysql
import queue
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
# 用于存放在线好友信息，内容同users
online_friends = []        
# 创建锁, 防止多个线程写入数据的顺序打乱                     
lock = threading.Lock()                         

class chat_server(threading.Thread):
    # 定义为全局变量
    global que, users, lock, online_friends
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
                                'strangers': {
                                    'strangers_num': 0
                                },
                                'friends': {
                                    'friends_num': 0
                                }
                            }
                        }
                        # 记录该用户所以已上线的好友id
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
                            if user[4] == user_pwd:
                                print('登陆成功')
                                message['info']['success'] = '登陆成功'
                                # 遍历在线用户，好友加入friends，陌生人加入strangers
                                friends_num = 0
                                strangers_num = 0
                                for online_user in users:
                                    sql2 = "select * from User_Friends where (user1_id = '%s' and user2_id = '%s') or (user1_id = '%s' and user2_id = '%s')" %(user_id, online_user[1], online_user[1], user_id)
                                    cursor.execute(sql2)
                                    if_friends = cursor.fetchall()
                                    # 是陌生人
                                    if not if_friends:
                                        message['info']['friends']['stranger'+str(strangers_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        strangers_num += 1
                                    # 是好友
                                    else:
                                        online_friends.append((online_user[1],online_user[2]))
                                        message['info']['friends']['friend'+str(friends_num)]={
                                            'user_id': online_user[1],
                                            'user_name': online_user[2]
                                        }
                                        friends_num += 1
                                # 记录好友、陌生人数量    
                                message['info']['friends']['friends_num'] = friends_num
                                message['info']['friends']['strangers_num'] = strangers_num
                                #好友上线消息
                                upline_message = {
                                    'send': 'server',
                                    'receive': '',
                                    'type': 8,
                                    'info': {
                                        'user_id': user_id,
                                        'user_name': user_name
                                    }
                                }
                                for online_friend in online_friends:
                                    upline_message['receive'] = online_friend[0]
                                    print(upline_message)
                                    upline_message = json.dumps(upline_message, ensure_ascii=False)
                                    conn.send(upline_message.encode('utf-8'))
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
                        print(message)
                        conn.send(message.encode('utf-8'))
                    # 注册消息
                    # 其他需服务器转发的消息
                    else:
                        self.save_data(request)

        # 断开连接
        except:
            pass
        finally:
            conn.close()
            self.delUser(conn)
            print('断开连接！')
         

    # 将聊天消息保存到队列
    def save_data(self, message):
        lock.acquire()
        try:
            que.put(message)
        finally:
            lock.release()

    # 将队列中消息转发
    def send_data(self):
        while True:
            if not que.empty():
                message = que.get()
                #私聊消息
                if message['type'] == 3:
                    for online_friend in online_friends:
                        if online_friend[1] == message['receive']:
                            message = json.dumps(message, ensure_ascii=False)
                            online_friend[0].send(message.encode('utf-8')) 
                            print('私聊',online_friend[2],': ',message)
                # 群发消息
                elif message['type'] == 4:
                    for online_user in users:
                        message = json.dumps(message, ensure_ascii=False)
                        online_user[0].send(message.encode('utf-8')) 
                        print('群发',online_friend[2],': ',message)
                

    # 用户离线后将其从users, onlne_friends中删除
    def delUser(self, conn):
        a = 0
        for user in users:
            if user[0] == conn:
                users.pop(a)
                break
            a = a + 1
        a = 0
        for online_friend in online_friends:
            if online_friend[0] == conn:
                online_friend.pop(a)
                break
            a = a + 1
    
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







