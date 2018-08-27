import socket
import sys  
from time import sleep

#******* Configuration constants ************
remote_ip = '10.90.121.149'
port = 2500  # web
cmd_read_rackid = 'read rackid'
cmd_scan_box = 'scan box'
cmd_state = 'state'
cmd_get_scanresult = 'get scanresult'
#********************************************

def OpenSocket (ip_addr, port):
	# create socket
	print('# Creating socket')
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		print('Failed to create socket')
		sys.exit()
		
	# Connect to remote server
	print('# Connecting to server, ' + remote_ip + ' (' + str(port) + ')')
	# s.connect((remote_ip , port))
	err = s.connect_ex((remote_ip , port))
	#print (err)
	if err > 0:
		print ('Connectoin to the server - ' + remote_ip + ' (' + str(port) + ')' + ' - cannot be established. Returned error: ' + str(err))
		s = None
	return s

def SendData (var_socket, request):
	print(request)
	try:
		var_socket.send(request.encode())
	except socket.error:
		print('Send failed')
		#s.close() #is this required here?
		sys.exit()

def RecvResponse (socket, resp_size = 1024, delay_sec = 0):
	sleep (delay_sec)
	print('# Receive data from server')
	reply = socket.recv(resp_size)
	print(reply)
	return reply
	
		
s = OpenSocket(remote_ip, port)
if s is not None:
	#********************************************
	# Get Rack ID
	SendData (s, cmd_read_rackid)
	reply = RecvResponse(s, 1024, 0.5)

	#Scan Box
	SendData (s, cmd_scan_box)
	reply = RecvResponse(s, 1024, 5)

	#Get readiness state
	SendData (s, cmd_state)
	reply = RecvResponse(s, 1024)


	#Get Scan results
	SendData (s, cmd_get_scanresult)
	reply = RecvResponse(s, 10240)

	#s.close()#is this required here?
else:
	print('Scanning was aborted!')
