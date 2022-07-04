import os.path
import socket
import json
import struct
from datetime import datetime
from queue import Queue
from time import sleep
import Contact
from pathlib import Path


chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
Chat_PORT = 3500
Server_IP = '127.0.0.1'
#Server_IP = '192.168.0.165'
File_PORT = 3600
Sys_PORT = 3700
send_2_server = ""
rcv_size = 1024
group_message_queue = Queue()
MacOS = False

if MacOS:
    default_file_path = Path("file_received/")
    default_pic_path = Path("pic_received/")
else:
    default_file_path = Path("../file_received/")
    default_pic_path = Path("../pic_received/")


# 客户端输入服务器ip
def modify_server(server_ip):
    global Server_IP
    Server_IP = server_ip


# 连接聊天服务器
def connect_server():
    chat_socket.connect((Server_IP, Chat_PORT))


# 连接文件服务器
def connect_file_rcv(user_id):
    file_socket.connect((Server_IP, File_PORT))
    temp_dict = dict()
    temp_dict['send'] = user_id
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 1
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    file_socket.send(data_str.encode('utf-8'))


# 发送注册消息
def register_procedure(user_name, user_pwd):
    temp_dict = dict()
    temp_dict['send'] = user_name
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 13
    temp_dict['info'] = {'user_name': user_name, 'user_pwd': user_pwd}
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


# 发送登录消息
def login_procedure(user_id, user_pwd):
    temp_dict = dict()
    temp_dict['send'] = user_id
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 1
    temp_dict['info'] = {'user_id': user_id, 'user_pwd': user_pwd}
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


# 发送私聊消息
def send_dm(user_num, rcv_num, chat_message, user_list):
    global chat_socket
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 3
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
    # user_list[rcv_num].message_queue.put(
    #     {'sender': user_num, 'content': chat_message, 'type': 'message'})


# 发送广播消息
def send_group(user_num, chat_message, group_message_queue):
    temp_dict = {}
    temp_dict['send'] = user_num
    temp_dict['receive'] = ''
    temp_dict['type'] = 4
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
    # group_message_queue.put(
    #     {'sender': user_num, 'content': chat_message, 'type': 'message'})


# 发送文件
def send_file(file_path, send_socket):
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        file_size = os.stat(file_path).st_size
        sleep(0.1)
        send_socket.send((file_name + '|' + str(file_size)).encode('utf-8'))
        sleep(0.1)
        with open(file_path, mode='rb') as fp:
            flag = True
            sent_size = 0
            while flag:
                # 大小小于batch_size或最后一个batch的发送
                if sent_size + rcv_size > file_size:
                    data_str = fp.read(file_size - sent_size)
                    flag = False
                else:
                    data_str = fp.read(rcv_size)
                    sent_size += rcv_size
                send_socket.send(data_str)
                print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])
            fp.close()
        sleep(1)


# 发送文件整个过程
def send_file_procedure(user_num, rcv_num, file_path, is_pic):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    if is_pic:
        temp_dict['type'] = 12
    else:
        temp_dict['type'] = 6
    temp_dict['info'] = 'start sending'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    file_socket.send(data_str.encode('utf-8'))

    send_file(file_path, file_socket)

    temp_dict['info'] = 'complete'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    file_socket.send(data_str.encode('utf-8'))
    print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-5])


# 好友请求消息
def friend_request(user_num, rcv_num):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 9
    temp_dict['info'] = '添加好友'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


# 好友请求通过/拒绝消息
def friend_response(user_num, agree, apply_user_num):
    temp_dict = dict()
    # 同意好友请求者id
    temp_dict['send'] = user_num
    # 申请者id
    temp_dict['receive'] = apply_user_num
    temp_dict['type'] = 10
    # 'agree' or 'reject'
    temp_dict['info'] = agree
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    print('friend_response:'+data_str)
    chat_socket.send(data_str.encode('utf-8'))


# 修改个人信息（用户名或密码）消息
def send_self_info(user_num, select, info):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 11
    temp_dict['info'] = {
        # int类型
        # 0：改密码；1：改用户名
        'PU': select,
        # 用户名或密码
        'NewInf': info
    }       
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


# 接收文件
def file_rcv(is_pic):
    recv_data = file_socket.recv(rcv_size).decode('utf-8')
    file_socket.settimeout(3)
    file_name, file_size = recv_data.split('|')
    received_size = 0
    if is_pic:
        path = default_pic_path
    else:
        path = default_file_path
    file_path = path / file_name
    with open(file_path, 'wb') as file:
        flag = True
        while flag:
            # upload incomplete
            if int(file_size) > received_size:
                data = file_socket.recv(rcv_size)
                # print(data)
                received_size += len(data)
            else:
                print(received_size)
                received_size = 0
                flag = False
                continue
            file.write(data)
        file_socket.settimeout(None)
        actual_size = file.tell()
        if int(file_size) != actual_size:
            print(file_size, actual_size)
            print("file damaged")
    return file_path


def rcv_one():
    print("in func rcv_one")
    data_str = chat_socket.recv(rcv_size)
    data_str = json.loads(data_str.decode('utf-8'))
    print(data_str)
    return data_str


def file_recv():
    print("in func file_recv")
    while True:
        rcv_buffer = file_socket.recv(rcv_size)
        print('file_recv:', rcv_buffer)
        data = json.loads(rcv_buffer.decode('utf-8'))
        package_type = data['type']
        sender_id = data['send']
        # 发送文件
        if package_type == 6:
            if data['info'] == "start sending":
                # 实际上的文件接收过程
                file_path = file_rcv(is_pic=False)
                    # groupRecieve(sender_id, file_path, 'file')
                rcv_buffer = file_socket.recv(rcv_size)
                data = json.loads(rcv_buffer.decode('utf-8'))
                print(type(data), data)
                if data['type'] == 6 and data['info'] == "complete":
                    print("File receive Success")
                else:
                    print("结束异常")
            else:
                print("wrong package type/info")
        # 发送图片
        elif package_type == 12:
            if data['info'] == "start sending":
                file_path = file_rcv(is_pic=True)
                rcv_buffer = file_socket.recv(rcv_size)
                data = json.loads(rcv_buffer.decode('utf-8'))
                print(type(data), data)
                if data['type'] == 12 and data['info'] == "complete":
                    print("Pic receive Success")
                else:
                    print("结束异常")
            else:
                print("wrong package type/info")

if __name__ == '__main__':
    connect_server()

    i = input("请输入程序序号")
    if i == '1':
        login_procedure('u123', '12321')
        while True:
            data_str = chat_socket.recv(rcv_size)
            data_str = json.loads(data_str.decode('utf-8'))
            print(data_str)
    elif i == '2':
        login_procedure('u234', '123')
        rcv_one()
        print("u234登陆成功")
        connect_file_rcv('u234')
        file_recv()
    elif i == '3':
        login_procedure('u456', '112233')
        rcv_one()
        print("u234登陆成功")
        connect_file_rcv('u456')
        file_recv()

    chat_socket.close()
