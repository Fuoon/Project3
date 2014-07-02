#!/usr/bin/env python
import socket
UDP_IP = "127.0.0.1"
UDP_PORT = 3333
MESSAGE = "Hello, World!"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
data, addr = sock.recvfrom(1024)
print data
print addr