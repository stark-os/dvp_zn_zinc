# -------- IMPORTATIONS --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< pffffffffffffffffff...
from zctx import *






# -------- SEMANTIC --------

#output
OBV__SEP = '\t'

#begBlanks for obvExe in fct scope
OBV__BEGBLANKS_FCT = 2* OBV__SEP

#value kinds
OBV__VAL_LIT    = 0
OBV__VAL_DATITM = 1
OBV__VAL_REG    = 2

#regs
OBV__PARAMS = ("p1", "p2", "p3", "p4", "p5", "p6")
OBV__REGS   = OBV__PARAMS + ("r",)






# -------- PARSING --------

#obv
class obvExe:
	def __init__(sbj, ist, sz, args, begBlanks):
		sbj.ist       = ist  #str
		sbj.sz        = sz   #s8
		sbj.args      = args #lst[str]
		sbj.begBlanks = begBlanks #str

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"obvExe\"\n"
		res += d + "ist:\"" + sbj.ist + "\"\n"
		res += d + "sz:" + str(sbj.sz) + '\n'
		res += d + "args:["
		for a in sbj.args:
			res += '"' + a + "\","
		res += ']'
		return res

	def unparse(sbj):
		res = sbj.begBlanks + sbj.ist + hexOnN(sbj.sz, 1)
		for a in sbj.args:
			res += OBV__SEP + a
		return res



#extract OBV ist & args from line
def obvParse(rawLine):
	commentIdx = str_findFirstChr(rawLine, '#')
	if commentIdx == 0:
		return None #empty line => no exe
	if commentIdx != -1:
		rawLine = str_sub(rawLine, stop=commentIdx-1)

	#strip
	line        = str_stripBeg(rawLine)
	begBlankLen = len(rawLine) - len(line)
	line        = str_stripEnd(line)

	#empty line => no exe
	if len(line) == 0:
		return None

	#args
	args = line.split(OBV__SEP)[1:]
	a = 0
	while a < len(args):
		if len(args[a]) == 0:
			args = lst_remove(args, a)
		else:
			a += 1

	#parse
	ox = obvExe(
		line[:3],
		chr_halfHex_toS8(line[3]),
		args,
		rawLine[:begBlankLen]
	)
	obvExe_checkIntegrity(ox)
	return ox

def obvExe_isCpy(ist, includeFromV=True):
	res = ist in ("d2d","d2r", "r2d","r2r")
	if includeFromV and not res:
		return ist in ("v2d","v2r")
	return res



#check args
def mustHaveNArgs(ox, argsNbr):
	if len(ox.args) != argsNbr:
		print("ERROR: Instruction \"" + ox.ist + "\" must have exactly " + str(argsNbr) + " args, got " + str(len(ox.args)) + ".")
		exit(1)

#def argMustBeDatChk(arg):
#	

#def argMustBeReg(arg):
#	

#def argMustBeVal(arg):
#	

def obvExe_checkIntegrity(ox):

	#rsv
	if ox.ist == "rsv":
		mustHaveNArgs(ox, 2)

	#cpy val 2 reg
	elif ox.ist == "v2r":
		mustHaveNArgs(ox, 2)

	#cpy val 2 dat
	elif ox.ist == "v2d":
		mustHaveNArgs(ox, 2)

	#cpy reg 2 reg
	elif ox.ist == "r2r":
		mustHaveNArgs(ox, 2)

	#cpy reg 2 dat
	elif ox.ist == "r2d":
		mustHaveNArgs(ox, 2)

	#cpy dat 2 dat
	elif ox.ist == "d2d":
		mustHaveNArgs(ox, 3)

	#cpy dat 2 reg
	elif ox.ist == "d2r":
		mustHaveNArgs(ox, 2)

	#bck
	elif ox.ist == "bck":
		mustHaveNArgs(ox, 0)

	#ivq
	elif ox.ist == "ivq":
		mustHaveNArgs(ox, 1)

	#fct
	elif ox.ist == "fct":
		mustHaveNArgs(ox, 1)

	#syc
	elif ox.ist == "syc":
		mustHaveNArgs(ox, 0)

	#unknown
	else:
		print("ERROR: Unknown instruction \"" + ox.ist + "\".")
		exit(1)
