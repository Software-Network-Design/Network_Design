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
# 创建锁, 防止多个线程写入数据的顺序打乱                     
lock = threading.Lock()                         

class chat_server(threading.Thread):
    global que, users, lock
    # 是否登陆成功
    online = 0
    def __init__(self):
        threading.Thread.__init__(self)
        self.addr = (HOST, Chat_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # addr ——— (host,port)
    # conn ——— socket
    def connect(self, conn, addr):
        request = conn.recv(RCV_SIZE)
        request = json.loads(request.decode('utf-8'))
        # 注册请求
        # 
        # 登录请求
        if request['type'] == 1:
            message = {
                'send': 'server',
                'receive': '',
                'type': 2,
                'info': {
                    # sucess：无此用户、密码错误、登陆成功
                    'success': '',
                    'friends': {

                    },
                    'groups': {

                    }
                }
            }
            user_id = request['info']['user_id']
            user_pwd = request['info']['user_pwd']
            message['receive'] = user_id
            sql = "select * from User where user_id = '%s'" %(user_id)
            # print(sql)
            try:
                cursor.execute(sql)
                user = cursor.fetchone()
                user_name = user[1]
                # 登陆成功
                if user[4] == user_pwd:
                    self.online = 1
                    message['info']['success'] = '登陆成功'
                    sql2 = "select * from User_Friends where user1_id = '%s' or user2_id = '%s'" %(user_id, user_id)
                    # print(sql2)
                    try:
                        cursor.execute(sql2)
                        user_friends = cursor.fetchall()
                        i = 0
                        for friend in user_friends:
                            # print(friend)
                            if(user_id != friend[0]):
                                message['info']['friends']['friend'+str(i)]={
                                    'user_id': friend[0]
                                }
                            else:
                                message['info']['friends']['friend'+str(i)]={
                                    'user_id': friend[1]
                                }
                            i = i + 1
                        message['info']['friends']['friends_num'] = i
                    except:
                        message['info']['friends']['friends_num'] = 0
                    sql3 = "select group_id from User_Group where user_id = '%s'" %(user_id)
                    # print(sql3)
                    try:
                        cursor.execute(sql3)
                        groups_id = cursor.fetchall()
                        i = 0
                        for group_id in groups_id:
                            message['info']['groups']['group'+str(i)]['group_id'] = group_id
                            i = i + 1
                        message['info']['groups']['groups_num'] = i
                    except:
                        message['info']['groups']['groups_num'] = 0
                # 密码错误
                else:
                    message['info']['success'] = '密码错误'
            # 无此用户
            except:
                message['info']['success'] = '无此用户'
        # 登陆成功
        if self.online == 1:
            users.append((conn, user_id, user_name, addr))
            message = json.dumps(message, ensure_ascii=False)
            conn.send(message.encode('utf-8'))
            # 登陆成功，开始一直侦听
            try:
                while True:
                    data = conn.recv(1024)
                    data = data.decode()
                    if not data:
                        break
                    # 处理之后接收到的各类型消息
            # 断开连接
            except:
                pass
            finally:
                conn.close()
                self.online = 0
                self.delUser(conn)
                print(user_id+'断开连接！')

        # 登陆失败
        else :
            message = json.dumps(message, ensure_ascii=False)
            conn.send(message.encode('utf-8')) 

    # addr ——— (host,port)
    # 将聊天消息保存到队列
    def save_data(self, addr, message):
        lock.acquire()
        try:
            que.put((addr,message))
        finally:
            lock.release()

    # 将队列中消息转发
    def send_data(self):
        while True:
            if not que.empty():
                packet = que.get()
                print(packet)
                message = packet[1]
                print(message)
                if message['type'] == 2:
                    for user in users:
                        if user[1] == message['receive']:
                            message = json.dumps(message, ensure_ascii=False)
                            user[0].send(message.encode('utf-8')) 
                            print('success!')

    # 用户离线后将其从users中删除
    def delUser(self, conn):
        a = 0
        for user in users:
            if user[0] == conn:
                users.pop(a)
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







