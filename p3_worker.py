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

	def convert(no, al=0):
		alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
		if(no < 62):
			return alphabet[no]
		else:
			al = no % 62
			no = no // 62
			if (no == 0):
				no = 0
			else:
				no = no - 1
			return  convert(no,al)+ alphabet[al]

	def crack(start,end,hash):
		status = "ND"
		for i in range(start,end+1):
			if(crypt(convert(i), "ic") == hash):
				return "DF:" + convert(i)
		status = "NF:" + hash
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
				self.connSocket.sendto("wa",(host, port))
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
				self.connSocket.sendto("kp",(host, port))
if __name__ == '__main__':
	serverPort = 3333
	hostIP = "169.254.182.174"
	clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	thread = WorkerClient(clientSocket,hostIP,serverPort)
	thread.start()	
