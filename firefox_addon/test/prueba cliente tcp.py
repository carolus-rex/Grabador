from socket import AF_INET, socket, SOCK_STREAM
import json

__author__ = "Daniel"

s = socket(AF_INET, SOCK_STREAM)

s.connect(("127.0.0.1", 9000))

#s.send(b"hola_python")
# data = s.recv(65536)
# print(json.loads(data.decode()))
s.send(b"-5-2")
while True:
    data = s.recv(65536)
    print(data.decode())
