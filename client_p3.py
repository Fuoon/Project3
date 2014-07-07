import socket
import time
import os
from crypt import crypt
import threading

notDone = True

def sendHashToServer(clientSocket, crypting, serverHost, serverPort):
	clientSocket.sendto("cp:" + crypting, (serverHost, serverPort))

class HandlePingServer(threading.Thread):
	def __init__(self, data, addr, clientSocket, crypting):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.clientSocket = clientSocket
		self.crypting = crypting

	def run(self):
		global notDone
		print self.data[3:]
		print "Ping Server"
		if notDone:
			print "not finish cracking yet"
			print notDone
			self.clientSocket.sendto("ps:" + self.crypting, (self.addr))
		else:
			return

if __name__ == '__main__':
	serverPort = 3333
	serverHost = '169.254.182.174'
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# password = os.urandom(2).encode('hex')
	password = "9999"
	print "password:" + password
	crypting = crypt(password, "ic")
	print "hash: " + crypting
	sendHashToServer(clientSocket, crypting, serverHost, serverPort)
	data, addr = clientSocket.recvfrom(1024)
	if data:
		if data[:2] == "ak":
			time.sleep(5)
			thread = HandlePingServer(data, addr, clientSocket, crypting)
			thread.start()
			while True:
				data, addr = clientSocket.recvfrom(1024)
				if data:
					if data[:2] == "ak":
						time.sleep(5)
						thread = HandlePingServer(data, addr, clientSocket, crypting)
						thread.start()
					elif data == password:
						notDone = False
						print "data finish"
						print notDone
						print data
						break
				else:
					w = threading.Timer(15.0, sendHashToServer)
					w.start()
		else:
			print data  