import socket
import time
import os
from crypt import crypt
import threading

def sendHashToServer(clientSocket, crypting, serverHost, serverPort):
	clientSocket.sendto("cp:" + crypting, (serverHost, serverPort))

class HandlePingServer(threading.Thread):
	def __init__(self, data, addr, clientSocket, password):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.clientSocket = clientSocket
		self.password = password

	def run(self):
		print self.data[3:]
		time.sleep(5)
		print "Ping Server"
		self.clientSocket.sendto("ps:" + self.password, (self.addr))

if __name__ == '__main__':
	serverPort = 3333
	serverHost = '169.254.182.174'
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	password = os.urandom(2).encode('hex')
	print "password:" + password
	crypting = crypt(password, "ic")
	print "hash: " + crypting
	# send hash to server
	sendHashToServer(clientSocket, crypting, serverHost, serverPort)
	while True:
		data, addr = clientSocket.recvfrom(1024)
		if data:
			if data[:2] == "ak":
				thread = HandlePingServer(data, addr, clientSocket, password)
				thread.start()
			elif data == password:
				print data
				break
		else:
			w = threading.Timer(15.0, sendHashToServer)
			w.start()