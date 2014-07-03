#!/usr/bin/env python
import socket as s
import threading 
import time
from collections import deque

total_com = 57731386986
startRange = 0
endRange = 10000

class Singleton(object):
	_instance = None
	cli_queue = []
	workers = []

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def getCliQueue(self):
		return self.cli_queue

	def getFirstClient(self):
		return self.cli_queue.popleft()

	def getWorkers(self):
		return self.workers

	# def gerCurrentWorkers(worker):

class Client():
	def __init__(self, addr, hashValue):
		self.addr = addr
		self.hashValue = hashValue

	def setAddr(self, addr):
		self.addr = addr 

	def setHashValue(self, hashValue):
		self.hashValue = hashValue

	def getAddr(self):
		return self.addr 

	def gethashValue(self):
		return self.hashValue

class Worker():
	def __init__(self, addr, status):
		self.addr = addr
		self.status = status
		self.hashValue = ''
		self.startRange = 0  
		self.endRange = 0

	def setAddr(self, addr):
		self.addr = addr

	def setStatus(self, status):
		self.status = status

	def setHashValue(self, hashValue):
		self.hashValue = hashValue

	def setStart(self, startRange):
		self.startRange = startRange

	def setEnd(self, endRange):
		self.endRange = endRange

	def getAddr(self):
		return self.addr

	def getStatus(self):
		return self.status

	def getHashValue(self):
		return self.hashValue

	def getStart(self):
		return self.startRange 

	def getEnd(self):
		return self.endRange

class TransferHandler():
	def __init__(self, data):
		self.data = data
		global startRange
		global endRange
		print "TransferHandler"
		st = Singleton()
		workers = st.getWorkers()
		for i in workers:
			data = "as:" + str(startRange) + ":" + str(endRange) + ":" + self.data
			sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
			sock.sendto(data, (i.getAddr()))
			print "sent"
			i.setStatus("busy")
			startRange += 10000
			endRange += 10000
			i.setStart(startRange)
			i.setEnd(endRange)
			i.setHashValue(self.data)
		
class HandleClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		if self.data:
			st = Singleton()
			client = Client(self.addr, self.data.split(":")[1])
			clients = st.getCliQueue()
			clients.append(client)
			workers = st.getWorkers()
			if workers:
				self.serverSocket.sendto("Please wait while we are trying to crack the password!!!!", self.addr)
				TransferHandler(self.data.split(":")[1])
			else:
				self.serverSocket.sendto("Currently the system is not avaliable, please try again later", self.addr)
				return
		else:
			print "Good bye", self.addr
			self.serverSocket.close()

class HandleWorkerConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		if self.data:
			self.serverSocket.sendto("rs", self.addr)
			st = Singleton()
			workers = st.getWorkers()
			worker = Worker(self.addr, "free")
			workers.append(worker)
			return
		else:
			print "Good bye", self.addr
			self.serverSocket.close()

class HandleWorkerDoneNotFound(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket
		self.hash = data.split(":")[1]

	def run(self):
		global startRange
		global endRange 
		st = Singleton()
		workers = st.getWorkers()
		data = "as:" + startRange + ":" + endRange + ":" + self.hash 
		self.serverSocket.sendto(data, (self.addr))
		for i in workers:
			if i.getAddr() == self.addr:
				i.setStart(startRange)
				i.setEnd(endRange)
				i.setHashValue(self.hash)

# class HandlePingClientServerConnection(threading.Thread):
# 	def __init__(self, data, addr, serverSocket):
# 		threading.Thread.__init__(self)
# 		self.data = data
# 		self.addr = addr
# 		self.serverSocket = serverSocket

# 	def run(self):
# 		st = Singleton()
# 		workers = st.getWorkers()
# 		for i in workers:
# 			serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
# 			serverSocket.bind((i.getAddr()))
# 			serverSocket.sendto(self.data, self.addr)

# class HandleWorkerDoneFound(threading.Thread):
# 	def __init__(self, data, addr, serverSocket):
# 		threading.Thread.__init__(self)

if __name__ == '__main__':
	serverPort = 3333
	serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	serverSocket.bind(('',serverPort))
	while True:
		data, addr = serverSocket.recvfrom(1024)
		if data[:2] == "rw":
			thread = HandleWorkerConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "cp":
			thread = HandleClientConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "ps":
			thread = HandlePingClientServerConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "nf":
			thread = HandleWorkerDoneNotFound(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "df":
			thread = HandleWorkerDoneFound(data, addr, serverSocket)
			thread.start()