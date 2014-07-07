#!/usr/bin/env python
import socket as s
import threading 
import time
from collections import deque

# total_com = 57731386986
total_com = 15018570

class Singleton(object):
	_instance = None
	cli_queue = []
	workers = {}

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

class Client():
	def __init__(self, addr, hashValue, startRange, endRange):
		self.addr = addr
		self.hashValue = hashValue
		self.startRange = startRange
		self.endRange = endRange

	def setAddr(self, addr):
		self.addr = addr 

	def setHashValue(self, hashValue):
		self.hashValue = hashValue

	def setStartRange(self, startRange):
		self.startRange = startRange

	def setEndRange(self, endRange):
		self.endRange = endRange

	def getAddr(self):
		return self.addr 

	def getHashValue(self):
		return self.hashValue

	def getStartRange(self):
		return self.startRange

	def getEndRange(self):
		return self.endRange

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
		serverSocket.sendto("kp", workers[i].getAddr())
		workers[i].setStatus("free")

def HandleTerminateSomeProcess(hashValue):
	st = Singleton()
	workers = st.getWorkers()
	print "HandleTerminateSomeProcess"
	for i in workers:
		if workers[i].getHashValue() == hashValue:
			print "Actuall send to worker to terminate process"
			serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
			serverSocket.sendto("kp", workers[i].getAddr())
			workers[i].setStatus("free")

# def HandleRangeCalculation():

class FirstTransferHandler(threading.Thread):
	def __init__(self, data, worker, startRange, endRange):
		threading.Thread.__init__(self)
		self.data = data
		self.worker = worker
		self.startRange = startRange
		self.endRange = endRange

	def run(self):
		print "FirstTransferHandler"
		data = "as:" + str(self.startRange) + ":" + str(self.endRange) + ":" + self.data
		print data
		sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
		sock.sendto(data, (self.worker.getAddr()))
		self.worker.setStatus("busy")
		self.worker.setStart(self.startRange)
		self.worker.setEnd(self.endRange)
		self.worker.setHashValue(self.data)
		return
		
class HandleClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		print "Client Connection"
		if self.data:
			hashValue = self.data.split(":")[1]
			startRange = 0
			endRange = 3000000
			st = Singleton()
			client = Client(self.addr, hashValue, startRange, endRange)
			print hashValue
			clients = st.getCliQueue()
			workers = st.getWorkers()
			if workers:
				self.serverSocket.sendto("ak:Please wait while we are trying to crack the password!!!!", self.addr)
				for i in workers:
					if workers[i].getStatus() == "free":
						thread = FirstTransferHandler(hashValue, workers[i], startRange, endRange)
						thread.start()
						startRange += 3000000
						endRange += 3000000
				client.setStartRange(startRange)
				client.setEndRange(endRange)
				clients.append(client)
				return
			else:
				print "No worker"
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
			self.serverSocket.sendto("ak", self.addr)
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
		self.hashValue = data.split(":")[1]

	def run(self):
		global total_com
		st = Singleton()
		clients = st.getCliQueue()
		workers = st.getWorkers()
		worker = workers[self.addr]
		for x in clients:
			if x.getHashValue() == self.hashValue:
				startRange = x.getStartRange()
				endRange = x.getEndRange()
				if endRange != total_com:
					if endRange+3000000 > total_com:
						endRange = total_com
					data = "as:" + str(startRange) + ":" + str(endRange) + ":" + self.hashValue
					self.serverSocket.sendto(data, (self.addr))
					worker.setEnd(endRange)
					worker.setStart(startRange)
					worker.setHashValue(self.hashValue)
					startRange += 3000000
					endRange += 3000000
					x.setStartRange(startRange)
					x.setEndRange(endRange)
					print startRange
					print endRange
					return
				else:
					if len(clients) > 1:
						client = clients[1]
						for i in workers:
							if workers[i].getStatus() == "free":
								startRange = client.getStartRange()
								endRange = client.getEndRange()
								thread = FirstTransferHandler(client.getHashValue(), workers[i], startRange, endRange)
								thread.start()
								startRange += 3000000
								endRange += 3000000
								client.setStartRange(startRange)
								client.setEndRange(endRange)
								print startRange
								print endRange
								return
					else:
						print "NO MORE CLIENT"
						return
		return

class HandlePingFromClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		print "ping client"
		self.serverSocket.sendto("ak", self.addr)
		# for i in workers:
		# 	if self.data.split(":")[1] == workers[i].getHashValue():
		# 		serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
		# 		serverSocket.sendto("ps", workers[i].getAddr())
		return

class HandleResponsePingToWorker(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		print "Response ping to worker"
		self.serverSocket.sendto("rp", self.addr)
		return

class HandleWorkerDoneFound(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.hashValue = data.split(":")[1]
		self.password = data.split(":")[2]
		self.addr = addr 
		print self.addr
		self.serverSocket = serverSocket

	def run(self):
		HandleTerminateSomeProcess(self.hashValue)
		st = Singleton()
		workers = st.getWorkers()
		clients = st.getCliQueue()
		if clients:
			print clients
			print "Client poppppppppppppppppppppppppppppppppppppp"
			client = clients.pop(0)
			print client.getHashValue()
			if client.getHashValue() == self.hashValue:
				serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
				serverSocket.sendto(self.password, client.getAddr())
				if clients:
					print "New CLIENTTTTTTTTTTTTTTTTTTTTTTT"
					client = clients[0]
					print client.getHashValue()
					for i in workers:
						if workers[i].getStatus() == "free":
							startRange = client.getStartRange()
							endRange = client.getEndRange()
							thread = FirstTransferHandler(client.getHashValue(), workers[i], startRange, endRange)
							thread.start()
							startRange += 3000000
							endRange += 3000000
							client.setStartRange(startRange)
							client.setEndRange(endRange)
			else:
				for x in clients:
					x.getHashValue() == self.hashValue
					serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
					serverSocket.sendto(self.password, x.getAddr())
			return
		else:
			return

# class HandleWorkerNotDoneNotFound(threading.Thread):
# 	def __init__(self, data, addr, serverSocket):
# 		threading.Thread.__init__(self)
# 		self.data = data
# 		self.addr = addr 
# 		self.serverSocket = serverSocket

# 	def run(self):
# 		print "To handle timer and time out!!!"

if __name__ == '__main__':
	serverPort = 3333
	serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	serverSocket.bind(('',serverPort))
	while True:
		data, addr = serverSocket.recvfrom(1024)
		if data[:2] == "rw":
			print "HandleWorkerConnection"
			thread = HandleWorkerConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "cp":
			print "HandleClientConnection"
			thread = HandleClientConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "ps":
			thread = HandlePingFromClientConnection(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "nf":
			print "Done and Not Found"
			thread = HandleWorkerDoneNotFound(data, addr, serverSocket)
			thread.start()
		elif data[:2] == "df":
			print "Done Found Status"
			thread = HandleWorkerDoneFound(data, addr, serverSocket)
			thread.start()
		# elif data[:2] == "nd":
		# 	print "Not Done Not Found"
		# 	thread = HandleWorkerNotDoneNotFound(data, addr, serverSocket)
		# 	thread.start()
		elif data[:2] == "wp":
			print "HandleRespondPingToWorker"
			thread = HandleResponsePingToWorker(data, addr, serverSocket)
			thread.start()