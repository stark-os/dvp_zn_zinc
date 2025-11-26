#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c05_atm(zCtx):
	zCtx.updateLogLvl(STEP.C05)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("============================== C05 ATM : beginning ==============================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#create gnc atm type
	#atmTypeID = newTyp(...)

	#create atm ID enm
	#atmIDs = 
	#for tID in range(len(zCtx.cpl.types)):
	#	

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("============================== C05 ATM : end ==============================")
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
