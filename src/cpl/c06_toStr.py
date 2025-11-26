#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c06_toStr(zCtx):
	zCtx.updateLogLvl(STEP.C06)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("============================= C06 TO STR : beginning ============================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#root prms (enough to tgt every prm)
	#toStr_fcts = [
	#	newFct(),
	#	newFct(),
	#	
	#]

	#stcs
	#for tInst in zCtx.cpl.types:
	#	if tInst.dcnCommon.nature == NATURE__STC:
	#		f = newFct()
	#		toStr_fcts.append(f)

	#add to fcts
	#zCtx.cpl.fcts += toStr_fcts

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("============================= C06 TO STR : end ============================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#all toStr fcts
		output = ""
		for f in toStr_fcts:
			output += f.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c06.dl", output)
