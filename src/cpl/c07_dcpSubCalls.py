#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- ZCI OPERATIONS --------

#type
def dcpSubCalls(zCtx, c, scope):
	zCtx.dbg0("Decomposing subcalls in call \"" + c.name + "\".")

	pass

	zCtx.dbg0("Decomposed subcalls.")






# -------- EXECUTION --------

#main
def c07_dcpSubCalls(zCtx):
	zCtx.updateLogLvl(STEP.C07)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C07 DCP SUB CALLS : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#debug
	output = ""

	#for each call val in the whole prg (should not have calls in gbl scp)
	#for f in zCtx.cpl.fcts:
	#	for di in f.scope.datItms:
	#		if di.inited:
	#			

	#	#VFC_VFC
	#	dcpSubCalls(zCtx, c, scope)

	#	#debug
	#	if log_lvl[0] >= LOG__LVL_DBG0:
	#		output += c

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C07 UNPARSE AS C : end =========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c07.dl", output)
