#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import sys
import subprocess






# -------- TOOLS --------

#tabulation used for output
TERM__OUTPUT_TAB = "\t" #"|   "

#exact range
def Term__width():
	return int(subprocess.check_output(["tput","cols"])[:-1])

def Term__fillLine(c, stream=sys.stdout):
	stream.write(c * Term__width())

def Term__drawSepLine(stream=sys.stdout):
	Term__fillLine('_', stream=stream)
	stream.write("\n")
