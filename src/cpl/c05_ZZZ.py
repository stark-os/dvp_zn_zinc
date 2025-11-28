#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c05_ZZZ(zCtx):
	zCtx.updateLogLvl(STEP.C05)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("============================== C05 ZZZ : beginning ==============================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#zzz...

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("============================== C05 ZZZ : end ==============================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#gather atm info
		output = ""

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c05.dl", output)
