# -------- IMPORTATIONS --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< pffffffffffffffffff...
from zctx import *






# -------- SEMANTIC --------

#output
OBV__SEP = '\t'

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
	def __init__(sbj, ist, args, begBlanks):
		sbj.ist       = ist  #str
		sbj.args      = args #lst[str]
		sbj.begBlanks = begBlanks #str

	def toStr(sbj):
		res = sbj.begBlanks + sbj.ist
		for a in sbj.args:
			res += OBV__SEP + a
		return res



#extract OBV ist & args from line
def obvParse(rawLine):
	commentIdx = str_findFirstChr(rawLine, '#')
	if commentIdx != -1:
		rawLine = str_sub(rawLine, stop=commentIdx-1)

	#strip
	line        = str_stripBeg(rawLine)
	begBlankLen = len(rawLine) - len(line)
	line        = str_stripEnd(line)

	#args
	args = line.split(OBV__SEP)[1:]
	a = 0
	while a < len(args):
		if len(args[a]) == 0:
			args = lst_remove(args, a)
		else:
			a += 1

	#parse
	return obvExe(line[:3], args, rawLine[:begBlankLen])

def obvExe_isCpy(ist, includeFromV=True):
	res = ist in ("d2d","d2r", "r2d","r2r")
	if includeFromV and not res:
		return ist in ("v2d","v2r")
	return res



#size
def obvExe_cpyIst_getSize(zCtx, ox):
	size = zCtx.smaxSize
	if ox.ist[0] == 'v':
		size = int( len(ox.args[0])/2 )
	elif ox.ist[0] == 'd' and ox.ist[2] == 'd':
		size = str_hex_toS16(ox.args[2])
	return size

def obvExe_setSizeIfNeeded(ox, size): #zCtx, ox, size):
	if ox.ist[0] == 'd' and ox.ist[2] == 'd':
		if len(ox.args) == 2:
			ox.args.append("")
		#if len(ox.args) != 3:
		#	zCtx.int("d2d ist has more or less than 2 or 3 args.", prtSubCtxs=False, prtLine=False)
		ox.args[2] = hexOnN(size, 4)
