#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c06_mergeConsecutiveAsg(zCtx):
	zCtx.updateLogLvl(STEP.C06)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("====================== C06 MERGE CONSECUTIVE ASG : beginning ====================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#only gbl scp for the moment
	e = 0
	while e < len(zCtx.cpl.gblScp.exes):

		#focus on ASG_ASG only
		if zCtx.cpl.gblScp.exes[e].id == ATM__ASG:
			a = zCtx.cpl.gblScp.exes[e].dat

			#asg into a datItm => can only be a gblDI => rm asg & set init val directly instead
			if a.dst.vdat.id == ATM__DATITM:
				gDI         = a.dst.vdat.dat
				gDI.inited  = True
				gDI.initVal = a.src

			#remove cur exe
			zCtx.cpl.gblScp.exes = lst_remove(zCtx.cpl.gblScp.exes, e)
			e -= 1

		#nxt exe
		e += 1

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("====================== C06 MERGE CONSECUTIVE ASG : end ====================")
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
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c06.dl", output)
