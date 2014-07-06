#!/usr/bin/env python

from argparse import ArgumentParser
from crypt import crypt
import threading
# from thread import Timer
import socket as s
import time 

status = ""
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
		print self.startRange
		print self.endRange
		print self.hashValue

	def run(self):
		global status
		print "~~~ into cracking password ~~~"
		answer = self.crack(self.startRange, self.endRange, self.hashValue)
		print "~~~ get the answer ~~~"
		print answer
		self.connSocket.sendto(answer, (self.host, self.port))
		status = ""
		print "~~~ sending to server ~~~"
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
		status = "nd"
		for i in range(startRange,endRange+1):
			if(crypt(self.convert(i), "ic") == hashValue):
				status = "df:" + hashValue  + ":" + self.convert(i)

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
		print self.connSocket
		print self.host
		print self.port
		print self.message
		self.connSocket.sendto(self.message, (self.host, self.port))
		if (self.message[:2] == "df" or self.message[:2] == "nf"):
			status = ""
		print "data sent!!!!!!"
		# self.connSocket.sendto("rw", (self.host, self.port))
		# status = ""
		# while True:
		# 	buf, address = self.connSocket.recvfrom(1024)
		# 	print "~~~ message from server ~~~"
		# 	print buf
		# 	if buf == "rs":
		# 		print "have connection with server"
		# 		status = ""
		# 	elif buf[:2] == "as":
		# 		print "server assign task to worker"
		# 		self.connSocket.sendto("wa",(self.host, self.port))
		# 		l = buf.split(":")
		# 		s = l[1]
		# 		e = l[2]
		# 		h = l[3]
		# 		w = Worker(s,e,h)
		# 		status = "nd"
		# 		print "~~~ before start crack pass ~~~"	
		# 		w.start()
		# 		print "~~~ after start crack pass ~~~"	
		# 	elif buf[:2] == "ps":
		# 		print "server ask worker for work progress"
		# 		self.connSocket.sendto(status,(self.host, self.port))
		# 	elif buf[:2] == "kp":
		# 		print "kill worker process"
		# 		w.exit()
		# 		self.connSocket.sendto("kp",(self.host, self.port))
		# 	else:
		# 		print "~~~ something crap! ~~~"


if __name__ == '__main__':
	serverPort = 3333
	hostIP = "169.254.182.174"
	clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	clientSocket.sendto("rw", (hostIP, serverPort))
	while True:
		buf, address = clientSocket.recvfrom(1024)
		if buf == "rs":
			print "~~~ have connection with server ~~~"
		elif buf[:2] == "as":
			print "~~~ server aasign task to worker ~~~"
			print buf
			l = buf.split(":")
			s = l[1]
			e = l[2]
			h = l[3]
			w = Worker(s,e,h,clientSocket,hostIP,serverPort)
			c = listenerServer(clientSocket,hostIP,serverPort,"wa")
			w.setDaemon(True)
			w.start()
			c.start()
			w.join()
			c.join()
		elif buf[:2] == "ps":
			c = listenerServer(clientSocket,hostIP,serverPort,status)
			print "~~~ got ping from server ~~~"
			c.start()
		elif buf[:2] == "kp":
			print "~~~ got kp from server ~~~"
			c = listenerServer(clientSocket,hostIP,serverPort,"kp")
			c.start()
			if w.is_alive() == True:
				print "~~~ thread still alive ~~~"
			print "~~~ going to delete worker process ~~~"
		elif buf == "":
			print "~~~ no data receive ~~~"


	# 169.254.223.238