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
	#split retruned value into the list by new line character
	list = reply.decode().splitlines()
	
	#print(list)
	#print(reply)
	return list
	
def ReadResponse (list, orig_command):
	out = {"status":"", "command":"", "value":"", "error":""} #create empty output dictionary as default response
	if len(list) > 0: #some data was returned
		response = list[len(list)-1] # take the last returned line as the actual response
		
		#print("Before replacment of command==>" + response)
		#print ("orig_command ==> " + orig_command)
		
		#check if original command is returned (it is supposed to be returned if everything is OK)
		if response.find(orig_command) > -1:
			#print ("!Original command was found!")
			response = response.replace(orig_command, '{{command}}', 1)
			out["command"] = orig_command
		else:
			out["error"] = "Expected command name (" + orig_command + ") was not found in the returned value!"
		#response = list[len(list)-1].split() # take the last returned line and split it by " "
		
		#print ("After replacment of command==>" + response)
		
		response_lst = response.split() #split returned string by " "
		if len(response_lst) > 0:
			i = 0
			value = ''
			while i < len(response_lst):
				if i == 0 :
					out["status"] = response_lst[i]
				elif i == 1:
					#do nothing, since command was already saved into "out" dictionary
					out["command"] = out["command"]
				else:
					value = value + ' ' + response_lst[i]
				i = i + 1
			out["value"] = value.strip()
		else:
			out["error"] = "No data can be parsed out of returned value!"
			out["value"] = response
	else:
		out["error"] = "No data was returned."
	return out
	
s = OpenSocket(remote_ip, port)
if s is not None:
	#********************************************
	# Get Rack ID
	SendData (s, cmd_read_rackid)
	reply = RecvResponse(s, 1024, 0.5)
	response = ReadResponse(reply, cmd_read_rackid) #returns dictionary with 3 values: status, command, value
	print (response)

	#Scan Box
	SendData (s, cmd_scan_box)
	reply = RecvResponse(s, 1024, 5)
	response = ReadResponse(reply, cmd_scan_box) #returns dictionary with 3 values: status, command, value
	print (response)

	#Get readiness state
	SendData (s, cmd_state)
	reply = RecvResponse(s, 1024)
	response = ReadResponse(reply, cmd_state) #returns dictionary with 3 values: status, command, value
	print (response)


	#Get Scan results
	SendData (s, cmd_get_scanresult)
	reply = RecvResponse(s, 10240)
	response = ReadResponse(reply, cmd_get_scanresult) #returns dictionary with 3 values: status, command, value
	print (response)

	s.close()#is this required here?
else:
	print('Scanning was aborted!')
