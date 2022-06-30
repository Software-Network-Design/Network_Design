import os.path
import socket
import json
import struct
from queue import Queue
from time import sleep
import Contact
# import client as GUI


chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
Chat_PORT = 3500
Server_IP = '127.0.0.1'
File_PORT = 3600
Sys_PORT = 3700
send_2_server = ""
rcv_size = 1024
default_file_path = "../file_received/"
default_pic_path = "../pic_received/"
group_message_queue = Queue()


# 客户端输入服务器ip
def modify_server(server_ip):
    global Server_IP
    Server_IP = server_ip


# 连接聊天服务器
def connect_server():
    chat_socket.connect((Server_IP, Chat_PORT))


# 连接文件服务器
def connect_file_rcv():
    global file_socket
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
def send_dm(user_num, rcv_num, chat_message, user_list):
    global chat_socket
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 3
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
    user_list[rcv_num].message_queue.put({'send': user_num, 'message': chat_message})


# 发送广播消息
def send_group(user_num, chat_message, group_message_queue):
    temp_dict = {}
    temp_dict['send'] = user_num
    temp_dict['receive'] = ''
    temp_dict['type'] = 4
    temp_dict['info'] = chat_message
    data_str = json.dumps(temp_dict, ensure_ascii=False)
    chat_socket.send(data_str.encode('utf-8'))
    group_message_queue.put()


# 发送文件
def send_file(file_path, send_socket):
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        file_size = os.stat(file_path).st_size
        send_socket.send((file_name + '|' + str(file_size)).encode('utf-8'))
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


def recv(user_dict, group_message_queue, my_id):
    while True:
        rcv_buffer = chat_socket.recv(rcv_size)
        data = json.loads(rcv_buffer.decode('utf-8'))
        print(data)
        package_type = data['type']
        # 一对一聊天消息
        if package_type == 3:
            sender = data['send']
            message = data['info']
            user_dict[sender].message_queue.put({'send': sender, 'message': message})
            # TODO: GUI如果正显示对应聊天窗口，显示消息内容
        # 群聊消息
        elif package_type == 4:
            sender = data['send']
            message = data['info']
            group_message_queue.put({'send': sender, 'message': message})
            # TODO: GUI如果正显示群聊窗口，显示消息内容
        # 用户下线
        elif package_type == 5:
            logout_user = data['sender']
            try:
                del user_dict[logout_user]
                # TODO:GUI聊天列表中移除下线用户
            except Exception as e:
                print(e)
                print("logout fault")
        # 用户上线
        elif package_type == 8:
            message = data['info']
            if message['type'] == 'friend':
                new_online = Contact(message['user_name'], message['user_id'], True)
            else:
                new_online = Contact(message['user_name'], message['user_id'], False)
            user_dict[message['user_id']] = new_online
            # TODO:GUI聊天列表中显示新上线用户
        # 接到好友邀请
        elif package_type == 9:
            friend_request_from = data['sender']
            accept = GUI.friendRequest(friend_request_from)
            if accept:
                user_dict[friend_request_from].is_friend = True
            friend_response(my_id, accept, friend_request_from)
        # 个人信息修改
        elif package_type == 16:
            person_info = data['info']
            user_name = person_info['user_name']
            user_id = person_info['user_id']
            user_dict[user_id].contact_name = user_name
            # TODO: GUI更新用户列表


# 接收文件
def file_rcv(is_pic):
    recv_data = file_socket.recv(rcv_size).decode('utf-8')
    file_name, file_size = recv_data.split('|')
    received_size = 0
    if is_pic:
        path = default_pic_path
    else:
        path = default_file_path
    file_path = path+file_name
    with open(file_path, 'wb') as file:
        flag = True
        while flag:
            # upload incomplete
            if int(file_size) > received_size:
                data = file_socket.recv(rcv_size)
                received_size += len(data)
            else:
                received_size = 0
                flag = False
                continue
            file.write(data)
        actual_size = os.stat(file_path).st_size
        if int(file_size) != actual_size:
            print("file damaged")
    return file_path


def file_recv():
    print("in func file_recv")
    while True:
        rcv_buffer = file_socket.recv(rcv_size)
        data = json.loads(rcv_buffer.decode('utf-8'))
        package_type = data['type']
        # 发送文件
        if package_type == 6:
            if data['info'] == "开始发送":
                file_rcv(is_pic=False)
                rcv_buffer = file_socket.recv(rcv_size)
                data = json.loads(rcv_buffer.decode('utf-8'))
                if data['type'] == 6 and data['info'] == "发送结束":
                    pass
                else:
                    print("结束异常")
            else:
                print("wrong package type/info")
        # 发送图片
        elif package_type == 12:
            if data['info'] == "开始发送":
                file_path = file_rcv(is_pic=True)
                # TODO:根据file_path将图片展示在文件中
                rcv_buffer = file_socket.recv(rcv_size)
                data = json.loads(rcv_buffer.decode('utf-8'))
                if data['typr'] == 12 and data['info'] == "发送结束":
                    pass
                else:
                    print("结束异常")
            else:
                print("wrong package type/info")


def rcv_one():
    print("in func rcv_one")
    data_str = chat_socket.recv(rcv_size)
    data_str = json.loads(data_str.decode('utf-8'))
    print(data_str)
    return data_str


# TODO: finish init_user_list
def init_user_list(user_list, response_dict):
    print("in func init_user_list")
    stranger_list = response_dict['strangers']
    stranger_count = len(stranger_list)
    friend_list = response_dict['friends']
    friend_count = len(friend_list)
    for stranger in stranger_list:
        name = stranger['user_name']
        ID = stranger['user_id']
        contact = Contact(name, ID, False)
        user_list[name] = contact
    for friend in friend_list:
        name = friend['user_name']
        ID = friend['user_id']
        contact = Contact(name, ID, True)
        user_list[name] = contact
    # TODO:GUI显示聊天列表


if __name__ == '__main__':
    chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_server()
    login_procedure('u123', '123321')
    rcv_one()
    sleep(1)
    send_dm('u123', 'u234', '私聊给你的哟')
    sleep(1)
    send_group('u123', '广播听到了吗')
    print('发送消息成功')
    sleep(1)
    friend_request('u123', 'u234')
    print('发送好友请求')
    sleep(1)
    send_self_info('u123', 0, '123321')
    # login_response = rcv_one()
    # login_success = login_response['info']['success']
    # if login_success == "登录成功":
    #     print("login success")
    #     init_user_list(user_list, login_response['info'])
    # elif login_response == "无此用户":
    #     pass
    # elif login_success == "密码错误":
    #     pass
    chat_socket.close()
