#!/usr/bin/env python
import socket as s
import threading 
import time
from collections import deque

class Singleton(object):
	_instance = None
	cli_queue = []

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def getCliQueue():
		return self.cli_queue

class Bundle():
	def __init__(self):
		self.cliAddr = ''
		self.hashValue = ''
		self.Worker = None
		self.Workers = []

	def deleteWorker(self, workerAddr):
		self.Workers.remove(workerAddr)

	def addWorker(self, worker):
		self.Workers.append(self.Worker)

	def createWorker(self, workerAddr):
		self.Worker = Worker(workerAddr)

	def getWorkerList(self):
		return self.Workers

	def getCliAddr(self):
		return self.cliAddr

	def getHashValue(self):
		return self.hashValue

	def getWorkerAddr(self):
		return self.Worker.getAddr()

	def getStart(self):
		return self.Worker.getStart()

	def getEnd(self):
		return self.Worker.getEnd()

	def setCliAddr(self, cliAddr):
		self.cliAddr = cliAddr

	def setHashValue(self, hashValue):
		self.hashValue = hashValue

	def setWorkerAddr(self, workerAddr):
		self.Worker.setAddr(workerAddr)

	def setStart(self, start):
		self.Worker.setStart(start)

	def setEnd(self, end):
		self.Worker.setEnd(end)

class Worker():
	def __init__(self, addr):
		self.addr = addr
		self.start = None
		self.end = None

	def getAddr(self):
		return self.addr 

	def getStart(self):
		return self.start

	def getEnd(self):
		return self.end

	def setAddr(self, addr):
		self.addr = addr

	def setStart(self, start):
		self.start = start

	def setEnd(self, end):
		self.end = end

class HandleClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		if self.data:
			self.serverSocket.sendto("Welcome, please wait while we are trying to crack the password!!!", self.addr)
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
		else:
			print "Good bye", self.addr
			self.serverSocket.close()

class HandleWorkerNewJob(threading.Thread):
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
		elif data[:2] == "cr":
			thread = HandleClientConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "nf":

		elif data[:2] == "df":