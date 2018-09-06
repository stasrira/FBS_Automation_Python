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

def printL (m):
	if __name__ == '__main__':
		print (m)

def OpenSocket (ip_addr, port):
	out = {"status":"", "command":"", "value":"", "error":""} #create empty output dictionary as default response
	# create socket
	#print (sys.argv)
	printL('# Creating socket')
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		printL('Failed to create socket')
		out["status"] = ''
		out["command"] = 'Create socket'
		out["error"] = 'Failed to create socket'
		# sys.exit()
		return out
		
	# Connect to remote server
	printL('# Connecting to server, ' + remote_ip + ' (' + str(port) + ')')
	# s.connect((remote_ip , port))
	out["command"] = 'connect: ' + remote_ip + ' (' + str(port) + ')'
	
	err = s.connect_ex((remote_ip , port))
	
	if err > 0:
		out["error"] = 'Connectoin to the server - ' + remote_ip + ' (' + str(port) + ')' + ' - cannot be established. Returned error: ' + str(err)
		#printL ('Connectoin to the server - ' + remote_ip + ' (' + str(port) + ')' + ' - cannot be established. Returned error: ' + str(err))
		out["status"] = ''
		s = None
	else:
		out["status"] = 'OK'
	
	out["value"] = s
	#return s
	return out

def SendData (var_socket, request):
	printL(request)
	try:
		var_socket.send(request.encode())
	except socket.error:
		printL('Send failed')
		#s.close() #is this required here?
		sys.exit()

def RecvResponse (socket, resp_size = 1024, delay_sec = 0):
	sleep (delay_sec)
	printL('# Receive data from server')
	reply = socket.recv(resp_size)
	#split retruned value into the list by new line character
	list = reply.decode().splitlines()
	
	#printL(list)
	#printL(reply)
	return list
	
def ReadResponse (list, orig_command):
	out = {"status":"", "command":"", "value":"", "error":""} #create empty output dictionary as default response
	if len(list) > 0: #some data was returned
		response = list[len(list)-1] # take the last returned line as the actual response
		
		#printL("Before replacment of command==>" + response)
		#printL ("orig_command ==> " + orig_command)
		
		#check if original command is returned (it is supposed to be returned if everything is OK)
		if response.find(orig_command) > -1:
			#printL ("!Original command was found!")
			response = response.replace(orig_command, '{{command}}', 1)
			out["command"] = orig_command
		else:
			out["error"] = "Expected command name (" + orig_command + ") was not found in the returned value!"
		#response = list[len(list)-1].split() # take the last returned line and split it by " "
		
		#printL ("After replacment of command==>" + response)
		
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
					if len(value) > 0:
						value = value + ' ' + response_lst[i]
					else:
						value = value + response_lst[i] #avoid an empty space for the first added value
				i = i + 1
			#out["value"] = value.strip()
			out["value"] = value
		else:
			out["error"] = "No data can be parsed out of returned value!"
			out["value"] = response
	else:
		out["error"] = "No data was returned."
	return out
	

def updateOutDict (out, status, value, message, error):
	out ["value"] = value
	out ["status"] = status
	out ["message"] = message
	out ["error_details"] = error
	return out
	
def FBS_Scan():
	
	out_FBS = {"status":0, "result":"", "message":"", "error_details":""} #create empty FBS Scanner output dictionary as default response
	response = {"status":"", "command":"", "value":"", "error":""} #create an empty TCP/IP default response dictionary 
	
	response = OpenSocket(remote_ip, port)

	if response["status"] == 'OK':
		s = response["value"]
	else:
		printL (response["error"])
		#sys.exit(-1)
		updateOutDict (out_FBS, -1, "", "Scanning was aborted!", response)
		#printL (out_FBS)
		return out_FBS

	if s is not None:
		#********************************************
		# Get Rack ID
		SendData (s, cmd_read_rackid)
		reply = RecvResponse(s, 1024, 0.5)
		response = ReadResponse(reply, cmd_read_rackid) #returns dictionary with 3 values: status, command, value
		#printL (response)
		if response["status"] != 'OK':
			updateOutDict (out_FBS, -1, "", "Scanning was aborted!", response)
			if s is not None:
				s.close()
			return out_FBS
		
		rack_id = response ["value"]

		#Scan Box
		SendData (s, cmd_scan_box)
		reply = RecvResponse(s, 1024, 5)
		response = ReadResponse(reply, cmd_scan_box) #returns dictionary with 3 values: status, command, value
		printL (response)
		if response["status"] != 'OK':
			updateOutDict (out_FBS, -1, "", "Scanning was aborted!", response)
			if s is not None:
				s.close()
			return out_FBS

		#Get readiness state
		SendData (s, cmd_state)
		reply = RecvResponse(s, 1024)
		response = ReadResponse(reply, cmd_state) #returns dictionary with 3 values: status, command, value
		printL (response)
		if response["status"] != 'OK':
			updateOutDict (out_FBS, -1, "", "Scanning was aborted!", response)
			if s is not None:
				s.close()
			return out_FBS

		#Get Scan results
		SendData (s, cmd_get_scanresult)
		reply = RecvResponse(s, 10240)
		response = ReadResponse(reply, cmd_get_scanresult) #returns dictionary with 3 values: status, command, value
		#printL (response["status"])
		if response["status"] != 'OK':
			updateOutDict (out_FBS, -1, "", "Scanning was aborted!", response)
			if s is not None:
				s.close()
			return out_FBS
		
		#format scan results
		sc_res = response["value"]
		sc_res = sc_res.replace('Line End,', '\n') #replace header of the last column with the return and new line characters 
		sc_res = sc_res.replace(',,end text,', ',' + rack_id + '\n') #replace "end text" column with the Rack_id value and the return and new line characters
		printL (sc_res)
		out_FBS ["result"] = sc_res
		out_FBS ["status"] = 1
		out_FBS ["message"] = "Scanning was successfully completed."
		out_FBS ["error_details"] = ""

		s.close()#is this required here?
	else:
		printL('Scanning was aborted!')
		response["status"] = "Not Connected"
		response["error"] = "Socket is None"
		response["command"] = ""
		response["value"] = ""
		out_FBS ["result"] = ""
		out_FBS ["status"] = -1
		out_FBS ["message"] = "Scanning was aborted!"
		out_FBS ["error_details"] = response
	
	return out_FBS

#if executed by itself, do the following
if __name__ == '__main__':
	response = FBS_Scan()
	printL ("++++++++++++++++++++++++++++Main output from scanner:")

	printL ("===>Status: " + str(response["status"]))
	printL ("===>Message: " + response["message"])
	printL ("===>Error Details: ") 
	printL (response["error_details"])
	printL ("===>Value: " + response["result"])