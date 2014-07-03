#!/usr/bin/env python
import socket as s
import threading 
import time
from collections import deque

total_com = 57731386986
start = 0
end = 10000

class Singleton(object):
	_instance = None
	cli_queue = []
	workers = []

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def getCliQueue():
		return self.cli_queue

	def getWorkers():
		return self.workers

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
		self.hashValue = hashValue
		self.start = 0  
		self.end = 0

	def setAddr(self, addr):
		self.addr = addr

	def setStatus(self, status):
		self.status = status

	def setHashValue(self, hashValue):
		self.hashValue = hashValue

	def setStart(self, start):
		self.start = start

	def setEnd(self, end):
		self.end = end

	def getAddr(self):
		return self.getAddr

	def getStatus(self):
		return self.status

	def getHashValue(self):
		return self.hashValue

	def getStart(self):
		return self.start 

	def getEnd(self):
		return self.end

class TransferHandler():
	def __init__(self, data):
		self.data = data

	def run(self):
		global start
		global end
		st = Singleton()
		workers = st.getWorkers()
		for i in workers:
			addr = i.getAddr()
			data = "as:" + self.start + ":" + self.end + ":" + self.data
			sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
			sock.sendto(data, (addr))
			i.setStatus("busy")
			start += 10000
			end += 10000
			i.setStart(start)
			i.setEnd(end)
			i.setHashValue(self.data)

class Manager(threading.Thread):
	def __init(self):
		threading.Thread.__init__(self)

	def range_manager(self):
		global total_com
		chunk = int(total_com/8)
		
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
				TransferHandler(self.data.split(":")[1])
			else:
				self.serverSocket.sendto("Currently the system is not avaliable, please try again later")
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
		global start
		global end 
		data = "as:" + start + ":" + end ":" + self.hash 
		self.serverSocket.sendto(data, (self.addr))

class HandleWorkerDoneFound(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)

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
		elif data[:2] == "nf":
			thread = HandleWorkerDoneNotFound(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "df":
			thread = HandleWorkerDoneFound(data, addr, serverSocket)
			thread.start()