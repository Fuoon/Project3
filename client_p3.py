import socket
import time
import os
from crypt import crypt
import threading
from threading import Timer

notDone = True
reconnect = True

def sendHashToServer(clientSocket, crypting, serverHost, serverPort):
	global reconnect
	print "try sending to server again"
	reconnect = False
	while True:
		print "IN LOOP"
		clientSocket.sendto("cp:" + crypting, (serverHost, serverPort))
		if reconnect:
			print "loop break"
			break
		time.sleep(5)

class HandlePingServer(threading.Thread):
	def __init__(self, data, addr, clientSocket, crypting):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.clientSocket = clientSocket
		self.crypting = crypting

	def run(self):
		global notDone
		print "Ping Server"
		if notDone:
			self.clientSocket.sendto("ps:" + self.crypting, (self.addr))
		else:
			return

if __name__ == '__main__':
	serverPort = 3333
	# serverHost = '169.254.182.174'
	serverHost = '127.0.0.1'
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	password = os.urandom(3).encode('hex')
	# password = "9999"
	print "password:" + password
	crypting = crypt(password, "ic")
	print "hash: " + crypting
	clientSocket.sendto("cp:" + crypting, (serverHost, serverPort))
	data, addr = clientSocket.recvfrom(1024)
	if data:
		if data[:2] == "ak":
			reconnect = True
			time.sleep(5)
			thread = HandlePingServer(data, addr, clientSocket, crypting)
			thread.start()
			try:
				while True:
					timer = Timer(15.0, sendHashToServer, [clientSocket, crypting, serverHost, serverPort])
					timer.start()
					data, addr = clientSocket.recvfrom(1024)
					if data:
						if data[:2] == "ak":
							reconnect = True
							timer.cancel()
							time.sleep(5)
							thread = HandlePingServer(data, addr, clientSocket, crypting)
							thread.start()
						elif data == password:
							reconnect = True
							notDone = False
							timer.cancel()
							print data
							break
						elif data[:2] == "Cu":
							timer.cancel()
			except KeyboardInterrupt:
				reconnect = True
				notDone = False
		else:
			print data