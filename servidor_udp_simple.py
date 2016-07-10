import pyaudio

import socket
__author__ = "Daniel"

CHUNK = 1024

p = pyaudio.PyAudio()


print(p.get_device_info_by_index(2))
stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                input_device_index=2)

server_add = ""
server_port = 4002

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((server_add, server_port))

while True:
    data, add = s.recvfrom(1)
    if data == b"a":
        while True:
            s.sendto(stream.read(CHUNK), add)
