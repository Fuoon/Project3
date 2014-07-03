#!/usr/bin/env python

from argparse import ArgumentParser
from crypt import crypt
import threading
import socket as s
import time 

class Worker(threading.Thread):
	def __init__(self,start,end,hash):
		threading.Thread.__init__(self)
		self.start = start
		self.end = end
		self.hash = hash

	def run(self):
		answer = crack(self.start, self.end, self.hash)
		return answer

	def convert62(n):
		def combination(i):
			if i >= 1:
				return (62 ** i) + combination(i-1)
			else:
				return (62 ** i)

		def setString(no,iter,a):
			if(iter == 1):
				return str(a[no % 62])
			elif(iter == 2):
				return str(a[((no - 0) / 62) % 62 - 1])
			else:
				return str(a[((no - 62 ** (iter - 2)) / 62 ** (iter - 1)) % 62 - 1])

		alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
		s = ""
		iterate = 1
		while True:
			if(n < combination(iterate)-1):
				s +=  setString(n,iterate,alphabet)
				return s[::-1] 
			else:
				s += setString(n,iterate,alphabet)
				iterate = iterate + 1

	def crack(start,end,hash):
		status = 0
		for i in range(start,end+1):
			if(crypt(convert62(i), "ic") == hash):
				return convert62(i)
		status = ""
		return status


class WorkerClient(threading.Thread):
	def __init__(self,connSocket,host,port):
		threading.Thread.__init__(self)
		self.connSocket = connSocket
		self.host = host
		self.port = port

	def run(self):
		self.connSocket.sendto("rw", (host, port))
		status = ""
		while True:
			buf, address = self.connSocket.recvfrom(1024)
			if buf == "rs":
				print "have connection with server"
				status = ""
			elif buf[:2] == "as":
				print "server assign task to worker"
				l = buf.split(":")
				s = l[1]
				e = l[2]
				h = l[3]
				w = Worker(s,e,h)
				status = w.start()
			elif buf[:2] == "ps":
				print "server ask worker for work progress"
				self.connSocket.sendto(status,(host, port))
			elif buf[:2] == "kp":
				print "kill worker process"
				w.exit()

if __name__ == '__main__':
	serverPort = 3333
	hostIP = "169.254.182.174"
	clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	thread = WorkerClient(clientSocket,hostIP,serverPort)
	thread.start()	
