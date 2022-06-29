import os.path
import socket
import json
import struct
from time import sleep


chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
Chat_PORT = 3500
Server_IP = '127.0.0.1'
File_PORT = 3600
Pic_PORT = 3700
send_2_server = ""
rcv_size = 1024


# 客户端输入服务器ip
def modify_server(server_ip):
    global Server_IP
    Server_IP = server_ip


# 连接聊天服务器
def connect_server():
    global chat_socket
    chat_socket.connect((Server_IP, Chat_PORT))


# 连接文件服务器
def connect_file_rcv():
    file_socket.connect((Server_IP, File_PORT))


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
def send_dm(user_num, rcv_num, chat_message):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 3
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


# 发送广播消息
def send_group(user_num, chat_message):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = ''
    temp_dict['type'] = 4
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))

'''
def request_rcv_IP(user_num, rcv_num):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 7
    temp_dict['info'] = rcv_num
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
'''


def send_file(file_path, send_socket):
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        file_size = os.stat(file_path).st_size
        send_socket((file_name + '|' + file_size).encode('utf-8'))
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
            fp.close()


def send_file_procedure(user_num, rcv_num, rcv_ip, file_path):
    connect_file_rcv(rcv_ip)
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 6
    temp_dict['info'] = 'start sending'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))

    send_file(file_path, file_socket)

    temp_dict['info'] = 'complete'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
    file_socket.close()


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


def send_pic_procedure(user_num, rcv_num, file_path):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 12
    temp_dict['info'] = 'start sending'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))

    send_file(file_path, chat_socket)

    temp_dict['info'] = 'complete'
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))


def recv():
    while True:
        rcv_buffer = chat_socket.recv(rcv_size)
        data = json.loads(rcv_buffer.decode('utf-8'))
        print(data)
        package_type = data['type']
        # 一对一聊天消息
        if package_type == 3:
            pass
        # 群聊消息
        elif package_type == 4:
            pass
        elif package_type == 9:
            pass


def rcv_one():
    data_str = chat_socket.recv(rcv_size)
    data_str = json.loads(data_str.decode('utf-8'))
    print(data_str)


if __name__ == '__main__':
    connect_server()
    login_procedure('u123', '123321')
    rcv_one()
    send_dm('u123', 'u234', '私聊给你的哟')
    send_group('u123', '广播听到了吗')
    print('发送消息成功')
    #friend_request('u123', 'u234')
    print('发送好友请求')
    send_self_info('u123', 0, '123321')
    rcv_one()
    sleep(10)
    chat_socket.close()
