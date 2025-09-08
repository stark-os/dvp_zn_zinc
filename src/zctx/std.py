#!/usr/bin/python3



# -------- IMPORTATIONS --------

#charsets
import string

#std
from std.string     import *
from std.path       import *
from std.list       import *
from std.io         import *
from std.parsingCtx import *
from std.int        import *






# -------- STD Z --------

#charsets
STR__BINARY                = ('0', '1')
STR__DECIMAL               = string.digits
STR__OCTAL                 = string.digits[:-2]
STR__HEXADECIMAL_LOWERCASE = string.hexdigits[:-6]

#local-python version of atm
ATM__BOO = 0
ATM__S1  = 1
ATM__U1  = 2
ATM__S2  = 3
ATM__U2  = 4
ATM__S4  = 5
ATM__U4  = 6
ATM__S8  = 7
ATM__U8  = 8
ATM__PTR = 9
ATM__CHR = 10
ATM__STR = 11
ATM__CALL     = 12
ATM__ZCI      = 13
ATM__VALUE    = 14
ATM__DATAITEM = 15
ATM__TYP      = 16
ATM__TYP_COMMONDATA = 17
ATM__SCP = 18
ATM__ASG = 19
ATM__STM = 20
ATM__FCT = 21
ATM__OPSEQ  = 22
ATM__POCALL = 23
ATM__LST = 24
ATM__ATM = 99
class atm:
	def __init__(self, id, data):
		self.id   = id   #ulng
		self.data = data #ulng





