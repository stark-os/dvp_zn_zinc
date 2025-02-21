#!/usr/bin/python3



# -------- TOOLS --------

#read - write
def readFile(filename):
	f = open(filename, "r")
	data = f.read()
	f.close()
	return data

def writeFile(filename, content):
	f = open(filename, "w")
	f.write(content)
	f.close()
