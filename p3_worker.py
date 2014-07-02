#!/usr/bin/env python

from argparse import ArgumentParser
from crypt import crypt
import threading
import socket as s
import time 

class Worker(threading.Thread):
	def intToStr(n):
		alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
		iterate = 1
		str = ""
		if(n >= 62):
			temp = n % 62
			str = str + alphabet[temp]
			iterate += 1 
			while True:
				co = n - (n % 62 ** (iterate -1))
				temp = (co / 62 ** (iterate - 1)) - 1
				if (temp <= 61): 
					str += alphabet[temp]
					return str[::-1]
				else:
					str += alphabet[temp % 62]
					iterate += 1
		else:
			return alphabet[n]

	def crack(start,end,hash):
		status = 0
		for i in range(start,end+1):
			if(crypt(intToStr(i), "ic") == hash):
				return intToStr(i)
		status = -1
		return status


class WorkerClient(threading.Thread):
	def __init__(self,connSocket,host,port):
		threading.Thread.__init__(self)
		self.connSocket = connSocket
		self.host = host
		self.port = port

	def run(self):
		self.connSocket.sendto("rw", (host, port))
		while True:
			buf, address = self.connSocket.recvfrom(1024)
			if buf == "rs":
				print "have connection with server"
			elif buf[:2] == "as":
				print "server assign task to worker"
			elif buf[:2] == "ps":
				print ""
			elif buf[:2] == "kp":


if __name__ == '__main__':
	serverPort = 3333
	hostIP = "169.254.182.174"
	clientSocket = s.socket(s.AF_INET, s.SOCK_DGRAM)
	thread = WorkerClient(clientSocket,hostIP,serverPort)
	thread.start()	
