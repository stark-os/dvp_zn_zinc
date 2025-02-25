#!/usr/bin/python3



# -------- IMPORTATIONS --------

#charsets
import string






# -------- TOOLS --------

#conversions
def chr_hex(c):
	return hex(ord(c))[2:]

#printable
def chr_isPrintable(c):
	return c in string.printable[:-5]
