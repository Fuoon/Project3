#!/usr/bin/env python
import socket as s
import threading 
from threading import Timer
import time
from collections import deque
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("port")
args = parser.parse_args()

total_com = 57731386986
# total_com = 15018570
global_worker_id = 1

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
	def __init__(self, addr, hashValue, startRange, endRange, timer, status):
		self.addr = addr
		self.hashValue = hashValue
		self.startRange = startRange
		self.endRange = endRange
		self.timer = timer
		self.status = status 

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

	def getTimer(self):
		return self.timer

	def setTimer(self, timer):
		self.timer = timer

	def getStatus(self):
		return self.status

	def setStatus(self, status):
		self.status = status

class Worker():
	def __init__(self, addr, status, timer, worker_id):
		self.addr = addr
		self.status = status
		self.hashValue = ''
		self.startRange = 0  
		self.endRange = 0
		self.timer = timer
		self.worker_id = worker_id

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

	def setWorkerID(self, worker_id):
		self.worker_id = worker_id

	def setTimer(self, timer):
		self.timer = timer

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

	def getTimer(self):
		return self.timer

	def getWorkerID(self):
		return self.worker_id

def HandleTerminateSomeProcess(hashValue, worker_id):
	st = Singleton()
	workers = st.getWorkers()
	for i in workers:
		if workers[i].getHashValue() == hashValue:
			workers[i].setStatus("free")
			if workers[i].getWorkerID() != worker_id:
				serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
				serverSocket.sendto("kp", workers[i].getAddr())
			

def TerminateWorker(worker_id, addr):
	st = Singleton()
	workers = st.getWorkers()
	clients = st.getCliQueue()
	if workers:
		if workers[addr].getWorkerID() == worker_id:
			if workers[addr].getStatus() == "busy":
				hashValue = workers[addr].getHashValue()
				startRange = workers[addr].getStart()
				endRange = workers[addr].getEnd()
				del workers[addr]
				print "We lost a worker: " + addr[0] + " now we have " + str(len(workers)) + " in the system."
				if clients:
					client_addr = " "
					for x in clients:
						if x.getHashValue() == hashValue:
							client_addr = x.getAddr()
					if client_addr != " ":
						timer = Timer(15.0, TerminateClient, [client_addr, hashValue])
						client = Client(client_addr, hashValue, startRange, endRange, timer, "leftover")
						clients.insert(0, client)
			else:
				del workers[addr]
				print "We lost a worker: " + addr[0] + " now we have " + str(len(workers)) + " in the system."
			
def TerminateClient(addr, hashValue):
	st = Singleton()
	clients = st.getCliQueue()
	workers = st.getWorkers()
	index = 0
	act_index = 0
	if clients:
		for x in clients:
			if x.getAddr() == addr and x.getHashValue() == hashValue:
				act_index = index
			index += 1
		clients.pop(act_index)
		print "We lost a client, now " + addr[0] + " is gone from our system! now we have " + str(len(clients)) + " in the queue." 
	for i in workers:
		if workers[i].getHashValue() == hashValue:
			serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
			serverSocket.sendto("kp", workers[i].getAddr())
			workers[i].setStatus("free")
			if clients:
				client = clients[0]
				startRange = client.getStartRange()
				endRange = client.getEndRange()
				thread = FirstTransferHandler(client.getHashValue(), workers[i], startRange, endRange)
				thread.start()
				startRange += 10000000
				endRange += 10000000
				client.setStartRange(startRange)
				client.setEndRange(endRange)

class FirstTransferHandler(threading.Thread):
	def __init__(self, data, worker, startRange, endRange):
		threading.Thread.__init__(self)
		self.data = data
		self.worker = worker
		self.startRange = startRange
		self.endRange = endRange

	def run(self):
		data = "as:" + str(self.startRange) + ":" + str(self.endRange) + ":" + self.data
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
		if self.data:
			hashValue = self.data.split(":")[1]
			startRange = 0
			endRange = 10000000
			timer = Timer(15.0, TerminateClient, [self.addr, hashValue])
			st = Singleton()
			client = Client(self.addr, hashValue, startRange, endRange, timer, "client")
			clients = st.getCliQueue()
			workers = st.getWorkers()
			if workers:
				self.serverSocket.sendto("ak:Please wait while we are trying to crack the password!!!!", self.addr)
				for i in workers:
					if workers[i].getStatus() == "free":
						thread = FirstTransferHandler(hashValue, workers[i], startRange, endRange)
						thread.start()
						startRange += 10000000
						endRange += 10000000
				client.setStartRange(startRange)
				client.setEndRange(endRange)
				client.getTimer().start()
				clients.append(client)
				print "We have a new client: " + self.addr[0] + " now we have " + str(len(clients)) + " in the queue"
				return
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
		global total_com
		global global_worker_id
		if self.data:
			self.serverSocket.sendto("ak:" + str(global_worker_id), self.addr)
			st = Singleton()
			clients = st.getCliQueue()
			workers = st.getWorkers()
			timer = Timer(15.0, TerminateWorker, [str(global_worker_id), self.addr])
			worker = Worker(self.addr, "free", timer, str(global_worker_id))
			global_worker_id += 1
			worker.getTimer().start()
			workers[self.addr] = worker
			print "Welcome new worker: " + self.addr[0] + " now we have " + str(len(workers)) + " workers"
			if clients:
				client = clients[0]
				startRange = client.getStartRange()
				endRange = client.getEndRange()
				if endRange != total_com:
					if startRange+10000000 > total_com:
						endRange = total_com
					thread = FirstTransferHandler(client.getHashValue(), worker, startRange, endRange)
					thread.start()
					if endRange != total_com:
						startRange += 10000000
						endRange += 10000000
					client.setStartRange(startRange)
					client.setEndRange(endRange)
				else:
					client = clients[1]
					startRange = client.getStartRange()
					endRange = client.getEndRange()
					if startRange+10000000 > total_com:
						endRange = total_com
					thread = FirstTransferHandler(client.getHashValue(), worker, startRange, endRange)
					thread.start()
					if endRange != total_com:
						startRange += 10000000
						endRange += 10000000
					client.setStartRange(startRange)
					client.setEndRange(endRange)
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
		if clients:
			for x in clients:
				if x.getHashValue() == self.hashValue:
					if x.getStatus() != "leftover":
						startRange = x.getStartRange()
						endRange = x.getEndRange()
						if endRange != total_com:
							if startRange+10000000 > total_com:
								endRange = total_com
							data = "as:" + str(startRange) + ":" + str(endRange) + ":" + self.hashValue
							self.serverSocket.sendto(data, (self.addr))
							worker.setEnd(endRange)
							worker.setStart(startRange)
							worker.setHashValue(self.hashValue)
							if endRange != total_com:
								startRange += 10000000
								endRange += 10000000
							x.setStartRange(startRange)
							x.setEndRange(endRange)
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
										if endRange != total_com:
											startRange += 10000000
											endRange += 10000000
										client.setStartRange(startRange)
										client.setEndRange(endRange)
										return
							else:
								print "NO MORE CLIENT"
								return
					else:
						client = clients.pop(0)
						startRange = client.getStartRange()
						endRange = client.getEndRange()
						hashValue = client.getHashValue()
						data = "as:" + str(startRange) + ":" + str(endRange) + ":" + hashValue
						self.serverSocket.sendto(data, (self.addr))
						worker.setEnd(endRange)
						worker.setStart(startRange)
						worker.setHashValue(hashValue)
		return

class HandlePingFromClientConnection(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket
		self.hashValue = self.data.split(":")[1]

	def run(self):
		st = Singleton()
		clients = st.getCliQueue()
		for x in clients:
			if x.getAddr()[1] == self.addr[1] and x.getHashValue() == self.hashValue:
				x.getTimer().cancel()
				timer = Timer(15.0, TerminateClient, [x.getAddr(), self.hashValue])
				x.setTimer(timer)
				x.getTimer().start()
				if x.getStatus() == "leftover":
					x.getTimer().cancel()
		self.serverSocket.sendto("ak", self.addr)
		return

class HandleResponsePingToWorker(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.data = data
		self.addr = addr
		self.serverSocket = serverSocket

	def run(self):
		st = Singleton()
		workers = st.getWorkers()
		for i in workers:
			if workers[i].getWorkerID() == self.data.split(":")[1]:
				workers[i].getTimer().cancel()
				timer = Timer(15.0, TerminateWorker, [workers[i].getWorkerID(), workers[i].getAddr()])
				workers[i].setTimer(timer)
				workers[i].getTimer().start()
		self.serverSocket.sendto("ak:" + self.data.split(":")[1], self.addr)
		return

class HandleWorkerDoneFound(threading.Thread):
	def __init__(self, data, addr, serverSocket):
		threading.Thread.__init__(self)
		self.hashValue = data.split(":")[1]
		self.password = data.split(":")[2]
		self.worker_id = data.split(":")[3]
		self.addr = addr 
		self.serverSocket = serverSocket

	def run(self):
		HandleTerminateSomeProcess(self.hashValue, self.worker_id)
		st = Singleton()
		workers = st.getWorkers()
		clients = st.getCliQueue()
		if clients:
			client = clients.pop(0)
			client.getTimer().cancel()
			if client.getHashValue() == self.hashValue:
				serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
				serverSocket.sendto(self.hashValue + ":" + self.password, client.getAddr())
				if clients:
					client = clients[0]
					for i in workers:
						if workers[i].getStatus() == "free":
							startRange = client.getStartRange()
							endRange = client.getEndRange()
							thread = FirstTransferHandler(client.getHashValue(), workers[i], startRange, endRange)
							thread.start()
							startRange += 10000000
							endRange += 10000000
							client.setStartRange(startRange)
							client.setEndRange(endRange)
			else:
				for x in clients:
					if x.getHashValue() == self.hashValue:
						serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
						serverSocket.sendto(self.hashValue + ":" + self.password, x.getAddr())
			return
		else:
			return

if __name__ == '__main__':
	serverPort = int(args.port)
	serverSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	serverSocket.bind(('',serverPort))
	try:
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
			elif data[:2] == "wp":
				thread = HandleResponsePingToWorker(data, addr, serverSocket)
				thread.start()
	except KeyboardInterrupt:
		print "server gone"