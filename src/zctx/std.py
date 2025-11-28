#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import sys

#charsets
import string

#std
from std.string            import *
from std.path              import *
from std.list              import *
from std.io                import *
from std.log               import *
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
ATM__BOL = 0
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
ATM__ZCI = 12
ATM__VAL = 13
ATM__TYP = 14
ATM__SCP = 15
ATM__ASG = 16
ATM__JMP = 17
ATM__FCT = 18
ATM__CALL    = 19
ATM__DATITM  = 20
ATM__STM_IF  = 21
ATM__STM_WHI = 22
ATM__STM_SWI = 23
ATM__TYP_DCNCOMMON = 24
ATM__OPSEQ         = 25
ATM__POCALL        = 26
ATM__LST           = 27
ATM__LST_VAL       = 28
ATM__LST_ATM       = 29
ATM__FMAP_STR_VAL  = 30
ATM__ATM = 99
class atm:
	def __init__(sbj, id, dat):
		sbj.id  = id  #ulng
		sbj.dat = dat #ulng


	def toStr(sbj, depth=0):
		d0  = TERM__OUTPUT_TAB *  depth
		res = "\n" + d0 + "_:\"atm\"\n"
		res += d0 + "id:" + str(sbj.id) + "\n"

		#itm
		if sbj.id in (
			ATM__ZCI,	ATM__VAL,		ATM__TYP,		ATM__DATITM,
			ATM__SCP,	ATM__ASG,		ATM__JMP,		ATM__TYP_DCNCOMMON,
			ATM__FCT,	ATM__OPSEQ, 	ATM__POCALL,	ATM__STM_IF,
			ATM__CALL,	ATM__STM_WHI,	ATM__STM_SWI,
			ATM__ATM
		):
			res += d0 + "dat:" + sbj.dat.toStr(depth=depth+1)

		#boolean
		elif sbj.id == ATM__BOL:
			if sbj.dat:
				res += "dat:true"
			res += "dat:false"

		#numerical
		elif sbj.id == ATM__S8:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 2) + '\"'
		elif sbj.id == ATM__U8:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 2) + '\"'
		elif sbj.id == ATM__S16:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 4) + '\"'
		elif sbj.id == ATM__U16:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 4) + '\"'
		elif sbj.id == ATM__S32:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 8) + '\"'
		elif sbj.id == ATM__U32:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 8) + '\"'
		elif sbj.id == ATM__S64:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 16) + '\"'
		elif sbj.id == ATM__U64:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 16) + '\"'
		elif sbj.id == ATM__REF:
			res += d0 + "dat:\"R" + hexOnN(sbj.dat, 16) + '\"'

		#lists
		elif sbj.id in (ATM__LST_VAL, ATM__LST_ATM, ATM__LST):
			res += d0 + "dat:["
			for e in sbj.dat:
				res += e.toStr(depth=depth+1) + ","
			res += '\n' + d0 + ']'

		#fmaps
		elif sbj.id == ATM__FMAP_STR_VAL:
			res += d0 + "dat:{"
			for k in sbj.dat.keys():
				res += '\n' + d0 + TERM__OUTPUT_TAB + '\"' + k + "\":" + sbj.dat[k].toStr(depth=depth+2) + ',' #recursive call
			res += '\n' + d0 + '}'

		#text
		elif sbj.id == ATM__CHR:
			res += d0 + "dat:'" + sbj.dat + '\''
		elif sbj.id == ATM__STR:
			res += d0 + "dat:\"" + sbj.dat + '"'
		return res

