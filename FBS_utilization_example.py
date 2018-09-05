import FBS_automation as fbs
import datetime

def saveScan(ScanRes, fileName = ""):
	#if no file name provided
	if fileName == "":
		d=datetime.datetime.now()
		ds = str(d.year)+str(100+d.month)[-2:]+str(100+d.day)[-2:]+str(100+d.hour)[-2:]+str(100+d.minute)[-2:]+str(100+d.second)[-2:]
		fileName = "scan_res_" + str(ds)+ ".txt"
	
	sc_res_file=open(fileName,'w')
	sc_res_file.write(ScanRes)
	sc_res_file.close()
	print ("Scan was saved into a file: %s." % fileName)


response = fbs.FBS_Scan()
print ("**************************" + response["message"])
if response["status"] != 1:
	err = response["error_details"]
	print ("Last attempted operation: " + err["command"])
	print ("Error details:" + err["error"])
else:
	print ("Scanned results:\n" + response["result"])
	ans = input ("Do you want to save the scan results into a file? (Y/N)")
	if ans in ['y', 'Y']:
		saveScan (response["result"])
	

#print ("\r\n>>>>>>>>>>>>>For debuggin purposes. Returned info is below:")
#print (response)


