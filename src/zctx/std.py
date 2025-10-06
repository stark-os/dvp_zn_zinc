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
ATM__STM_FOR = 22
ATM__STM_WHI = 23
ATM__STM_SWI = 24
ATM__TYP_DCNCOMMON = 25
ATM__OPSEQ         = 26
ATM__POCALL        = 27
ATM__LST           = 28
ATM__LST_VAL       = 29
ATM__LST_ATM       = 30
ATM__FMAP_STR_VAL  = 31
ATM__ATM = 99
class atm:
	def __init__(sbj, id, dat):
		sbj.id  = id  #ulng
		sbj.dat = dat #ulng


	def toStr(sbj, depth=0):
		dm1 = TERM__OUTPUT_TAB * (depth-1)
		d0  = TERM__OUTPUT_TAB *  depth
		d1  = d0  + TERM__OUTPUT_TAB
		res = "\n" + d0 + "_:\"atm\"\n"
		res += d0 + "id:" + str(sbj.id) + "\n"

		#itm
		if sbj.id in (
			ATM__ZCI,	ATM__VAL,		ATM__TYP,		ATM__DATITM,
			ATM__SCP,	ATM__ASG,		ATM__JMP,		ATM__TYP_DCNCOMMON,
			ATM__FCT,	ATM__OPSEQ, 	ATM__POCALL,	ATM__STM_IF,
			ATM__CALL,	ATM__STM_FOR,	ATM__STM_WHI,	ATM__STM_SWI,
			ATM__ATM
		):
			res += d0 + "dat:" + sbj.dat.toStr(depth=depth+1)

		#boolean
		elif sbj.id == ATM__BOO:
			if sbj.dat:
				res += "dat:true\n"
			res += "dat:false\n"

		#numerical
		elif sbj.id == ATM__S8:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 2) + "\"\n"
		elif sbj.id == ATM__U8:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 2) + "\"\n"
		elif sbj.id == ATM__S16:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 4) + "\"\n"
		elif sbj.id == ATM__U16:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 4) + "\"\n"
		elif sbj.id == ATM__S32:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 8) + "\"\n"
		elif sbj.id == ATM__U32:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 8) + "\"\n"
		elif sbj.id == ATM__S64:
			res += d0 + "dat:\"S" + hexOnN(sbj.dat, 16) + "\"\n"
		elif sbj.id == ATM__U64:
			res += d0 + "dat:\"U" + hexOnN(sbj.dat, 16) + "\"\n"
		elif sbj.id == ATM__REF:
			res += d0 + "dat:\"R" + hexOnN(sbj.dat, 16) + "\"\n"

		#lists
		elif sbj.id in (ATM__LST_VALUE, ATM__LST_ATM, ATM__LST):
			res += d0 + "dat:["
			for e in sbj.dat:
				res += d1 + e.toStr(depth=depth+1) + ","
			res += "]\n"

		#fmaps
		elif sbj.id == ATM__FMAP_STR_VALUE:
			res += d0 + "dat:{\n"
			for k in sbj.dat.keys():
				res += d1 + '\"' + k + "\":" + sbj.dat[k].toStr(depth=depth+1) + ',' #recursive call
			res += "}\n"

		#text
		elif sbj.id == ATM__CHR:
			res += d0 + "dat:'" + sbj.dat + "'\n"
		elif sbj.id == ATM__STR:
			res += d0 + "dat:\"" + sbj.dat + "\"\n"
		return res + dm1

