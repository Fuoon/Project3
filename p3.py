#!/usr/bin/env python
import socket as s
import threading 

class HandleConnection(threading.Thread):
	def __init__(self, connSocket, addr):
		threading.Thread.__init__(self)
		self.connSocket = connSocket
		self.addr = addr

	def run(self):
		while True:
			dataBuf = connSocket.recv(1024)
			if dataBuf:
				uppercasedBuf = dataBuf.upper()
				self.connSocket.send(uppercasedBuf)
			else:
				print "Good bye", self.addr
				self.connSocket.close()
				break

if __name__ == '__main__':
	serverPort = 3333
	serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
	serverSocket.bind(('',serverPort))
	serverSocket.listen(50)
	while True:
		connSocket, addr = serverSocket.accept()
		thread = HandleConnection(connSocket, addr)
		thread.start()