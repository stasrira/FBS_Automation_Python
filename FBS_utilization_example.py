import FBS_automation as fbs

response = fbs.FBS_Scan()
print ("**************************" + response["message"])
if response["status"] != 1:
	err = response["error_details"]
	print ("Last attempted operation: " + err["command"])
	print ("Error details:" + err["error"])
else:
	print ("Scanned results:\r\n" + response["result"])
	

print ("For debuggin purposes. Returned info is below:")
print (response)
