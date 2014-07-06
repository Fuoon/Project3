import socket
import time
import os
from crypt import crypt
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

serverHost = '169.254.182.174'
#'169.254.182.174'

port = 3333

#random generate word
randomwording = os.urandom(1).encode('hex')
print "password:" + randomwording

#create hash
crypting = crypt(randomwording, "ic")
print "hash:" + crypting

def sending_hash():
	client.sendto("cp:" + crypting, (serverHost, port))

sending_hash()

data, addr = client.recvfrom(4096)
if data[:2] == "ak":
	print data[3:]
	#start ping
else:
	#send hash again after 15 sec
	w = threading.Timer(15.0, sending_hash)
	w.start()

def sending_ping():
	global client
	global serverHost
	global port
	print "sending ping to server"
	client.sendto("ps", (serverHost, port))

#sending ping to server
while True:
	time.sleep(5)
	sending_ping()
	serverdata = client.recvfrom(1024)
	print serverdata