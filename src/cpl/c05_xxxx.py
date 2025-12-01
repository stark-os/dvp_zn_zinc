#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c05_xxxx(zCtx):
	zCtx.updateLogLvl(STEP.C05)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C05 XXXX : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C05 XXXX : end ========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#gather gbl scp + fcts
		output = zCtx.cpl.gblScp.toStr()
		for f in zCtx.cpl.fcts:
			if not f.ext:
				output += f.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c05.dl", output)
