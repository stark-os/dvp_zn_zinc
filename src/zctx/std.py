#!/usr/bin/python3



# -------- IMPORTATIONS --------

#charsets
import string

#std
from std.string            import *
from std.path              import *
from std.list              import *
from std.io                import *
from std.parsingCtx        import *
from std.int               import *
from std.term              import *
from std.math_combinations import *

#dreamlands
import std.dreamlands as dreamlands
import std.config     as config






# -------- STD Z --------

#charsets
STR__BINARY                = ('0', '1')
STR__DECIMAL               = string.digits
STR__OCTAL                 = string.digits[:-2]
STR__HEXADECIMAL_LOWERCASE = string.hexdigits[:-6]

#local-python version of atm
ATM__BOO = 0
ATM__S8  = 1
ATM__U8  = 2
ATM__S16 = 3
ATM__U16 = 4
ATM__S32 = 5
ATM__U32 = 6
ATM__S64 = 7
ATM__U64 = 8
ATM__REF = 9
ATM__CHR = 10
ATM__STR = 11
ATM__CALL     = 12
ATM__ZCI      = 13
ATM__VALUE    = 14
ATM__DATAITEM = 15
ATM__TYP      = 16
ATM__TYP_DCNCOMMON = 17
ATM__SCP = 18
ATM__ASG = 19
ATM__STM = 20
ATM__FCT = 21
ATM__OPSEQ          = 22
ATM__POCALL         = 23
ATM__LST            = 24
ATM__LST_VALUE      = 25
ATM__LST_ATM        = 26
ATM__FMAP_STR_VALUE = 27
ATM__ATM = 99
class atm:
	def __init__(sbj, id, data):
		sbj.id   = id   #ulng
		sbj.data = data #ulng









