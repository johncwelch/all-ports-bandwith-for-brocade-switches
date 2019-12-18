#! /usr/bin/python
#better print functions
from __future__ import print_function
import os
import sys
from optparse import OptionParser
#better CSV read functions
import csv


brocadeIFInfoTable = []
brocadeIFInfoTableList = []
brocadeIFInfoTableOID = ".1.3.6.1.4.1.1991.1.1.3.3.5"
smnpCommand = ""
unitLabel = ""

brocadeResultsTable = []
brocadeResultsString = ""



scriptversion = ".1"

errors = {
	"OK": 0,
	"WARNING": 1,
	"CRITICAL": 2,
	"UNKNOWN": 3,
	}
	
common_options = ""

# function for setting common options
def set_common_options(snmpver):
	#this way we know which common_options we're setting
	global common_options
	if snmpver == "2":
		common_options = "snmptable -v 2c -m ALL -CH -Cf , -c "
		#print(snmpwalkstring)
	elif snmpver == "3":
		#common_options = "snmpwalk -OvQ -v 3"
		sys.exit("Currently only working with v2, 3 is on the way")
	else:
		#print("Invalid SNMP version, must be 2 or 3")
		sys.exit("Invalid SNMP version, must be 2 or 3")
	
def main():
	args = None
	options = None

	# Create command-line options
	parser = OptionParser(version="%prog " + scriptversion)
	parser.add_option("-H", action="store", type="string", dest="hostname", help="hostname or IP of target device <REQUIRED>")
	#parser.add_option("-h", action="store_true", dest="help")
	parser.add_option("-U", action="store", type="string", dest="bandwidth_units", help="units for bandwidth measurement, g(igabps) or m(ega)bps <REQUIRED>")
	#snmp options
	parser.add_option("-V", action="store", type="string", dest="snmpver", help="version of snmp, use either 2 or 3, currently only v2 implemented <REQUIRED")
	parser.add_option("-c", action="store", type="string", dest="community", help="snmpv2/2c community string, mandatory for v2 <REQUIRED for V 2")
	parser.add_option("-a", action="store", type="string", dest="authProt", help="snmpv3 authentication protocol to use, use either MD5 or SHA (required for all v3 sec levels over noAuthNoPriv)")
	parser.add_option("-A", action="store", type="string", dest="authPass", help="snmpv3 authentication passphrase (required for all v3 sec levels over noAuthNoPriv)")
	parser.add_option("-e", action="store", type="string", dest="secEngineID", help="snmpv3 security engine ID (optional)")
	parser.add_option("-E", action="store", type="string", dest="conEngineID", help="snmpv3 context engine ID (optional)")
	parser.add_option("-l", action="store", type="string", dest="secLevel", help="snmpv3 security level, use either noAuthNoPriv, authNoPriv, authPriv")
	parser.add_option("-n", action="store", type="string", dest="context", help="snmpv3 context name (optional)")
	parser.add_option("-u", action="store", type="string", dest="userName", help="snmpv3 user name (required for all security levels other than noAuthNoPriv)")
	parser.add_option("-x", action="store", type="string", dest="encryptProt", help="snmpv3 encryption protocol to use, use either DES or AES (required for v3 sec level of authPriv)")
	parser.add_option("-X", action="store", type="string", dest="encryptPass", help="snmpv3 encryption passphrase (required for v3 sec level of authPriv)")
	parser.add_option("-Z", action="store", type="string", dest="bootsTime", help="snmpv3 destination engine boots/time (optional)")
	
	
	(options, args) = parser.parse_args(args)
	
	host = options.hostname
	#helptext = options.help
	units = options.bandwidth_units
	vers = options.snmpver
	comm = options.community
	aprot = options.authProt
	apass = options.authPass
	seng = options.secEngineID
	ceng = options.conEngineID
	secl = options.secLevel
	cont = options.context
	user = options.userName
	eprot = options.encryptProt
	epass = options.encryptPass
	btime = options.bootsTime
	
	#check for -h
	#if helptext:
	#	print("This probe is designed to show you point in time bandwidth flow from Brocade switches.\nIt uses private Brocade OIDs, so it won't work with other vendor models.\n Currently, only SNMPv2 is implemented, working on v3, that's a bit of a pain to implement when you can't easily test it.\nUsage:\n checkBrocadeAllPortsBandwidthUsage.py -H <Hostname or IP address REQUIRED> -V <snmp version, either 2 or 3, REQUIRED, only 2 is working> -c <snmp v2c community string REQUIRED> -U <units, g (Gbps) or m (Mbps)\nOptions:\n-H IPv4 IP address or DNS name of target\n-V SNMP version, either 2 or three, only 2 is currently supported\n-c SNMP v2 community string\n-U Units, g or m\n")
	#	sys.exit()
	
	# Check for required "-H" option
	if host:
		pass
	else:
		sys.exit("ERROR: -H (target DNS name or IP address) is a required argument")
		
	#check for units
	if units == "g" or units == "m":
		pass
	else:
		sys.exit("ERROR: -U measurement units (g for Gbps or m for Mbps) is a required argument")
		
	# check for snmp version (we HAVE to have this to decide what to use)
	if vers:
		set_common_options(vers)
	else:
		sys.exit("ERROR: -V, SNMP version is a required argument")
		
	if vers == "2":
		if comm:
			pass
			#build the command string
			smnpCommand = common_options + comm + " " + host + " " + brocadeIFInfoTableOID
			#print(smnpCommand)
		else:
			sys.exit("ERROR: for snmp versions 1 or 2 a community string is mandatory")

	

	#run snmptable command, shove results into list
	brocadeIFInfoTable = os.popen(smnpCommand).read().split('\n')
	
	
	#build CSV structure from initial list
	brocadeInfoTableCSV=csv.reader(brocadeIFInfoTable)
	
	#create list of lists from CSV structure
	for row in brocadeInfoTableCSV:
		brocadeIFInfoTableList.append(row)
	
	#delete the last item in the list. This is empty and causes us problems.
	del brocadeIFInfoTableList[-1]
	
	#in this table, there's this thing where it has a row that is all question marks
	#then it's nothing but IF MAC addresses in the first field, followed by question marks 
	#for every other field in the row. We don't need these, so we delete them
	
	for row in brocadeIFInfoTableList:
		#get the index of that first question mark row and break out of the loop
		if row[0] == "?":
			deleteRowStart = brocadeIFInfoTableList.index(row)
			break

	#since the way we delete the unneeded rows handles the foo-1 for us, we set the "end" of the list to the total length.
	lastItem = len(brocadeIFInfoTableList)

	#delete every row from the question marks to the end, and now all we have is useful data!
	del brocadeIFInfoTableList[deleteRowStart:lastItem]
	for row in brocadeIFInfoTableList:
		theIndex = brocadeIFInfoTableList.index(row)
		#row[0]=the port number
		#row[17]=the portDescr
		#row[53]=the inKbps
		#row[54]=the outKbps 
		
		#coerce kbps to floats
		row[53] = float(row[53])
		row[54] = float(row[54])
		
		#using Mbps
		if units == "m":
			unitLabel = "Mbps"
			row[53] = row[53]/1000
			row[54] = row[54]/1000
		elif units == "g":
			unitLabel = "Gbps"
			row[53] = row[53]/1000000
			row[54] = row[54]/1000000
		
		#de-scientific notation the results
		row[53] = format(row[53],'.4f')
		row[54] = format(row[54],'.4f')
		
		#print(row[0],row[17],row[53],row[54])
		
		#build list of vars we want for the main bit
		brocadeResultsTable.append(row[17] + ": " + row[53] + unitLabel + " in " + row[54] + unitLabel + " out \n")
		#brocadeResutlsTable[theIndex] = row[17] + ": " + row[53] + unitLabel + " in " + row[54] + unitLabel + " out "
		#print(brocadeResultsTable)
	
	#needed to avoid assignment error
	brocadeResultsString = ""
	
	#convert list of lists to a single multiline text file
	for row in brocadeResultsTable:
		brocadeResultsString = brocadeResultsString + row
	
	#remove trailing \n
	brocadeResultsString = brocadeResultsString[:-2]
	
	#add pipe character for perfdata
	brocadeResultsString = brocadeResultsString + "|"
	
	#print("'test'")
	
	#build string with perfdata
	for row in brocadeIFInfoTableList:
		#print(row[17])
		brocadeResultsString = brocadeResultsString + "'Interface " + row[17] + " in:'=" + row[53] + " 'Interface " + row[17] + " out: '=" +row[54] + " "
	
	#trim trailing space
	brocadeResultsString = brocadeResultsString[:-1]
	
	#this is here because this is what nagios actually uses for the probe output
	print(brocadeResultsString)
	
	sys.exit()
	# Should never get here
	#sys.exit(errors['UNKNOWN'])

# Execute main() function
if __name__ == "__main__":
	main()
