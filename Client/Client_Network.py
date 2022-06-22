import os.path
import socket
import json
import struct

chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
Chat_PORT = 3500
Server_IP = socket.gethostname()
File_PORT = 3600
Pic_PORT = 3700
send_2_server = ""
rcv_size = 1024


def connect_server():
    chat_socket.connect((Server_IP, Chat_PORT))


def connect_file_rcv(rcv_ip):
    file_socket.connect((rcv_ip, File_PORT))


def login_procedure(user_num, pwd):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 1
    temp_dict['info'] = user_num + ';' + pwd
    data = [temp_dict]
    data_str = json.dumps(data)
    # print(type(json.dumps(data)), json.dumps(data))
    chat_socket.send(data_str.encode('utf-8'))


def logout(user_num):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 5
    temp_dict['info'] = "logout"
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def send_dm(user_num, crv_num, chat_message):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = crv_num
    temp_dict['type'] = 3
    temp_dict['info'] = chat_message
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def send_group(user_num, group_num, chat_message):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = group_num
    temp_dict['type'] = 4
    temp_dict['info'] = chat_message
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def request_rcv_IP(user_num, rcv_num):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 7
    temp_dict['info'] = rcv_num
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


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
                    data = fp.read(file_size - sent_size)
                    flag = False
                else:
                    data = fp.read(rcv_size)
                    sent_size += rcv_size
                send_socket.send(data)
            fp.close()


def send_file_procedure(user_num, rcv_num, rcv_ip, file_path):
    connect_file_rcv(rcv_ip)
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 6
    temp_dict['info'] = 'start sending'
    data = [temp_dict]
    data_str = json.dumps(data)
    file_socket.send(data_str.encode('utf-8'))

    send_file(file_path, file_socket)

    temp_dict['info'] = 'complete'
    data = [temp_dict]
    data_str = json.dumps(data)
    file_socket.send(data_str.encode('utf-8'))
    file_socket.close()


def friend_request(user_num, rcv_num):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 9
    temp_dict['info'] = rcv_num
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def friend_response(user_num, agree):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 10
    temp_dict['info'] = agree
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def send_self_info(user_num, personal_info):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = send_2_server
    temp_dict['type'] = 11
    temp_dict['info'] = personal_info
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def send_pic_procedure(user_num, rcv_num, file_path):
    temp_dict = dict()
    temp_dict['send'] = user_num
    temp_dict['receive'] = rcv_num
    temp_dict['type'] = 12
    temp_dict['info'] = 'start sending'
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))

    send_file(file_path, chat_socket)

    temp_dict['info'] = 'complete'
    data = [temp_dict]
    data_str = json.dumps(data)
    chat_socket.send(data_str.encode('utf-8'))


def recv():
    while True:
        data = chat_socket.recv(rcv_size)
        data = data.decode('utf-8')
        json.loads()

connect_server()
rcv_buffer = chat_socket.recv(rcv_size)
rcv_buffer = rcv_buffer.decode('utf-8')
data = json.loads(rcv_buffer)
print(type(data), data)
