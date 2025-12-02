# -------- SEMANTIC --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< pffffffffffffffffff...
from zctx import *

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
