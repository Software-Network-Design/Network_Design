import json
import socket
import threading

chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
Chat_PORT = 3500
Server_IP = ""
File_PORT = 3600
Pic_PORT = 3700
send_2_server = ""
rcv_size = 1024
Max_connection = 5

print(host, Chat_PORT)

chat_socket.bind((host, Chat_PORT))
chat_socket.listen(Max_connection)

client_skt, client_addr = chat_socket.accept()

data = {"a": '你好', "b": 2}
client_skt.send(json.dumps(data).encode('utf-8'))

