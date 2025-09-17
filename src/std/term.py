#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import subprocess






# -------- TOOLS --------

#exact range
def Term__width():
	return int(subprocess.check_output(["tput","cols"])[:-1])

def Term__fillLine(c):
	print(c * Term__width())

def Term__drawSepLine():
	Term__fillLine('_')
	print()
