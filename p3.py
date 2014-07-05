#!/usr/bin/env python
import socket as s
import threading 
import time
from collections import deque

total_com = 57731386986

class Singleton(object):
	_instance = None
	cli_queue = []
	workers = {}
	startRange = 0
	endRange = 5000

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

	def getStart(self):
		return self.startRange

	def getEnd(self):
		return self.endRange

	def setStart(self, startRange):
		self.startRange = startRange

	def setEnd(self, endRange):
		self.endRange = endRange

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

def HandleTerminateAllProcess():
	st = Singleton()
	workers = st.getWorkers()
	for i in workers:
		serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
		serverSocket.sendto("tp", workers[i].getAddr())
		workers[i].setStatus("free")

def HandleTerminateSomeProcess(hashValue):
	st = Singleton()
	workers = st.getWorkers()
	for i in workers:
		if workers[i].getHashValue() == hashValue:
			serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
			serverSocket.sendto("tp", workers[i].getAddr())
			workers[i].setStatus("free")

class FirstTransferHandler(threading.Thread):
	def __init__(self, data, worker, startRange, endRange):
		threading.Thread.__init__(self)
		self.data = data
		self.worker = worker
		self.startRange = startRange
		self.endRange = endRange

	def run(self):
		st = Singleton()
		data = "as:" + str(self.startRange) + ":" + str(self.endRange) + ":" + self.data
		sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
		sock.sendto(data, (self.worker.getAddr()))
		self.worker.setStatus("busy")
		self.worker.setStart(self.startRange)
		self.worker.setEnd(self.endRange)
		self.worker.setHashValue(self.data)
		st.setStart(startRange+5000)
		st.setEnd(endRange+5000)
		return
		
class HandleClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		if self.data:
			hashValue = self.data.split(":")[1]
			st = Singleton()
			client = Client(self.addr, hashValue)
			clients = st.getCliQueue()
			clients.append(client)
			workers = st.getWorkers()
			startRange = st.getStart()
			endRange = st.getEnd()
			if workers:
				self.serverSocket.sendto("Please wait while we are trying to crack the password!!!!", self.addr)
				for i in workers:
					thread = FirstTransferHandler(hashValue, workers[i], startRange, endRange)
					thread.start()
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
			workers[self.addr] = worker
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
		st = Singleton()
		startRange = st.getStart()
		endRange = st.getEnd()
		workers = st.getWorkers()
		worker = workers[self.addr]
		data = "as:" + startRange + ":" + endRange + ":" + self.hash 
		self.serverSocket.sendto(data, (self.addr))
		worker.setEnd(endRange)
		worker.setStart(startRange)
		worker.setHashValue(self.hash)
		st.setStart(startRange+5000)
		st.setEnd(endRange+5000)
		return

class HandlePingFromClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		st = Singleton()
		workers = st.getWorkers()
		if self.data:
			self.serverSocket.sendto("rs", self.addr)
			for i in workers:
				thread = HandlePingtoWorkersConnection(workers[i])
				thread.start()

class HandlePingtoWorkersConnection(threading.Thread):
	def __init__(self, worker):
		threading.Thread.__init__(self)
		self.worker = worker

	def run(self):
		serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
		serverSocket.sendto("ps", self.worker.getAddr())
		recvData, addr = serverSocket.recvfrom(1024)

class HandleWorkerDoneFound(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.hashValue = data.split(":")[1]
		self.password = data.split(":")[2]
		self.addr = addr 
		self.serverSocket = serverSocket

	def run(self):
		HandleTerminateSomeProcess(self.hashValue)
		st = Singleton()
		workers = st.getWorkers()
		clients = st.getCliQueue()
		client = clients.popleft()
		startRange = st.getStart()
		endRange = st.getEnd()
		if client.getHashValue() == self.hashValue:
			serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
			serverSocket.sendto(self.password, client.getAddr())
		else:
			for x in clients:
				x.getHashValue() == self.hashValue
				serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
				serverSocket.sendto(self.password, x.getAddr())
		if clients:
			client = clients[0]
			for i in workers:
				if workers[i].getStatus() == "free"
					thread = FirstTransferHandler(self.hashValue, workers[i], startRange, endRange)
					thread.start()
			return
		else:
			return

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
			thread = HandlePingFromClientConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "nf":
			thread = HandleWorkerDoneNotFound(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "df":
			thread = HandleWorkerDoneFound(data, addr, serverSocket)
			thread.start()