from socket import SOCK_STREAM, AF_INET
from socket import socket

__author__ = "Daniel"

s = socket(AF_INET, SOCK_STREAM)

s.bind(("127.0.0.1", 2500))

s.listen(1)

while True:
    connection, address = s.accept()
    print("Conectado")
    connection.send(b"soy_python")
    while True:
        data = connection.recv(4)
        print("data recivida: " + data.decode())
        connection.send(b"llamando a casa")
