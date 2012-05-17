#!/usr/bin/python
#################################################################
# Email Verifier v2.1											#
# By: Dennis Linuz <dennismald@gmail.com>						#
# Verify if email addresses are valid by checking SMTP server   #
#################################################################

import smtplib, sys

#Check if dnspython libraries exist and import them
try:
	import dns.resolver
except Exception as exc:
	print "Email Verifier requires 'dnspython 1.10.0' libraries"
	quit()

#Extract the host from the given email address
def getHost(emailAddress):
	try:
		return emailAddress.split("@")[1]
	except Exception as exc:
		print "'" + emailAddress + "' is not a valid email address"
		output(exc)
		return -1	

#Find the mail server hostname from DNS MX records
def resolveMX(emailHost):
	global hostItems
	hostDict={}
	try:
		records = dns.resolver.query(emailHost, "MX")
	except Exception as exc:
		print "Could not extract records from host."
		output(exc)
		return -1
	for r in records:
		hostDict[r.exchange] = r.preference
	hostItems = hostDict.items()
	hostItems.sort()
#Connect to host and check if the email address is valid
def checkEmail(emailAddress):
	result = True
	smtp = smtplib.SMTP()
	for x in hostItems:
		try:
			host = x[0][:-1]
			host = ".".join(host)
			connectLog = smtp.connect(host)
			heloLog = smtp.helo("google.com")
			output(connectLog)
			output(heloLog)
		except Exception as exc:
			errorString = "Could not connect to Server: " + host
			errorString += "\nTrying next record (if any)"
			output(errorString)
			output(exc)	
			continue
		else:
			result = False
			break
	if result:
		print "Could not resolve any hosts for: " + emailAddress
		return -1
	try:
		sendLog = smtp.sendmail("test@google.com",emailAddress,"IgnoreMessage")
		output(sendLog)
	except Exception as exc:
		print "Email is not valid."
		output(exc)
	else:
		print "Email: " + emailAddress + " is valid!"
		validList.append(emailAddress)

#Print more output if verbose argument is given
def output(string):
	if verbose:
		print string

#Print the documentation
def printHelp():
	print ""
	print "Verify if email addresses are valid by checking SMTP server\n"
	
	print "Usage:\n\tpython email-verifier.py -e <email> -v\n"
	print "Arguments:\n"
	print "-h or --help","This help".rjust(28)
	print "-v or --verbose","Increases verbosity".rjust(35)
	print "-e or --email <email>","Specify one email address to check".rjust(44)
	print "-f or --file <file>","Specify a file of emails delimeted by line".rjust(54)
	print "\nExample:\n\tpython email-verifier.py -e admin@example.org -v"
	print "\tpython email-verifier.py --file email.txt\n"
	quit()

verbose=False
suppliedInput = 0

if not (len(sys.argv) == 3 or len(sys.argv) == 4):
	printHelp()

for i in range(1,len(sys.argv)):
	if sys.argv[i] == "-h" or sys.argv[i] == "--help":
		printHelp()
	elif sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
		verbose=True
		continue
	elif sys.argv[i] == "-e" or sys.argv[i] == "--email":
		if suppliedInput == 0:
			inputEmail = sys.argv[i+1]
			suppliedInput = 1
		else:
			printHelp()
	elif sys.argv[i] == "-f" or sys.argv[i] == "--file":
		if suppliedInput == 0:
			inputFile = sys.argv[i+1]
			suppliedInput = 2
		else:
			printHelp()

validList = []
if suppliedInput == 0:
	printHelp()
elif suppliedInput == 1:
	host = getHost(inputEmail)
	if not host == -1:
		if not resolveMX(host) == -1:
			checkEmail(inputEmail)
elif suppliedInput == 2:
	try:
		file = open(inputFile,"r")
	except Exception as exc:
		print "Could not open '" + inputFile + "' for reading"
		output(exc)
		quit()
	else:
		for email in file:
			email = email.replace("\n","")
			print "Checking: " + email
			host = getHost(email)	
			if host == -1:
				continue
			elif resolveMX(host) == -1:
				continue
			elif checkEmail(email) == -1:
				continue
if validList:
	print "\nValid Emails: \n=========="
	for item in validList:
		print item
	print ""
