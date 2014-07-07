#!/usr/bin/env python
from argparse import ArgumentParser
from crypt import crypt
import threading
from threading import Timer
import socket as s
import time 
import sys

status = ""
isFinish = False
isActive = True
serverPort = 3333
hostIP = "127.0.0.1" #"169.254.182.174"
reconnect = True
ID = "0"

class Worker(threading.Thread):
	def __init__(self, startRange, endRange, hashValue, connSocket, host, port):
		print "~~~ worker instance instanciate ~~~"
		threading.Thread.__init__(self)
		self.startRange = int(startRange)
		self.endRange = int(endRange)
		self.hashValue = hashValue
		self.connSocket = connSocket
		self.host = host
		self.port = port

	def run(self):
		global status
		global ID
		status = "nd"
		print "~~~ into cracking password ~~~"
		tic = time.clock()
		answer = self.crack(self.startRange, self.endRange, self.hashValue)
		toc = time.clock()
		rt = toc - tic
		rt = int(rt)
		answer = answer + ":" + str(rt) + ":" + ID
		print "~~~ get the answer ~~~"
		print answer
		print "~~~ sending to server ~~~"
		self.connSocket.sendto(answer, (self.host, self.port))
		status = ""
		return 

	def convert(self, no, al=0):
		alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
		if(no < 62):
			return alphabet[no]
		else:
			al = no % 62
			no = no // 62
			if (no == 0):
				no = no - 1
			return  self.convert(no,al)+ alphabet[al]

	def crack(self, startRange, endRange, hashValue):
		global status
		global isFinish
		isFinish = False
		isActive = True
		status = "nd"
		for i in range(startRange,endRange+1):
			if (isFinish == False and isActive == True):
				if(crypt(self.convert(i), "ic") == hashValue):
					status = "df:" + hashValue  + ":" + self.convert(i)
					return status
			else:
				status = "nf:" + hashValue
				return status
		status = "nf:" + hashValue
		return status

class listenerServer(threading.Thread):
	def __init__(self,connSocket,host,port,message):
		threading.Thread.__init__(self)
		self.connSocket = connSocket
		self.host = host
		self.port = port
		self.message = message

	def run(self):
		global status
		self.connSocket.sendto(self.message, (self.host, self.port))
		if (self.message[:2] == "df" or self.message[:2] == "nf"):
			status = ""

class workerPing(threading.Thread):
	def __init__(self, connSocket, host, port):
		threading.Thread.__init__(self)
		self.connSocket = connSocket
		self.host = host
		self.port = port

	def run(self):
		global ID
		self.connSocket.sendto("wp" + ":" + ID, (self.host, self.port))


def reconnectToServer(clientSocket):
	global isActive
	global reconnect
	print "~~~ reconnect to server ~~~"
	# sys.exit()
	isActive = False
	reconnect = False
	stopWorkerWork()
	while True:
		print "Trying to reconnect"
		clientSocket.sendto("rw", (hostIP, serverPort))
		if reconnect:
			print "loop break"
			break
		time.sleep(5)

def stopWorkerWork():
	global isFinish
	isFinish = True

if __name__ == '__main__':
	clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	clientSocket.sendto("rw", (hostIP, serverPort))
	while True:
		t = Timer(8.0, reconnectToServer, [clientSocket])
		t.start()
		buf, address = clientSocket.recvfrom(1024)
		if buf[:2] == "ak":
			a = buf.split(":")
			ID = a[1]
			print "~~~ ping ~~~"
			reconnect = True
			t.cancel()
			time.sleep(5)
			p = workerPing(clientSocket,hostIP,serverPort)
			p.start()
		elif buf[:2] == "as":
			t.cancel()
			print "~~~ server aasign task to worker ~~~"
			print buf
			l = buf.split(":")
			s = l[1]
			e = l[2]
			h = l[3]
			w = Worker(s,e,h,clientSocket,hostIP,serverPort)
			c = listenerServer(clientSocket,hostIP,serverPort,"wa")
			w.start()
			c.start()
		elif buf[:2] == "kp":
			t.cancel()
			print "~~~ got kp from server ~~~"
			c = listenerServer(clientSocket,hostIP,serverPort,"kp")
			c.start()
			if w.is_alive() == True:
				print "~~~ thread still alive ~~~"
				stopWorkerWork()
				print "~~~ stop worker process ~~~"
	# 169.254.223.238