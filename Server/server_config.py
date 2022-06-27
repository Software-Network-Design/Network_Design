import json
import socket
import threading
import pymysql
import queue
# 服务器ip
HOST = '0.0.0.0'
# 聊天端口
Chat_PORT = 3500
# 客户端ip
Server_IP = ""
# 传输文件端口
File_PORT = 3600
Pic_PORT = 3700
send_2_server = ""
RCV_SIZE = 1024
# 最大等待处理数
Max = 5
