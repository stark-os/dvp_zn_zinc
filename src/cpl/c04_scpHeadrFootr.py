#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- SCP HEADER & FOOTER --------

#collapse recursively in inner scopes
def collapseScpHeaderAndFooter(scope):
	scope.exes = scope.header + scope.exes + scope.footer

	#inner scopes
	for x in scope.exes:
		if x.id == ATM__STM_IF:
			collapseScpHeaderAndFooter(x.dat.ifScope)
			if x.dat.elsScope is not None:
				collapseScpHeaderAndFooter(x.dat.elsScope)
		elif x.id == ATM__STM_WHI:
			collapseScpHeaderAndFooter(x.dat.scope)
		elif x.id == ATM__STM_SWI:
			for s in x.dat.scopes:
				collapseScpHeaderAndFooter(s)






# -------- EXECUTION --------

#main
def c04_scpHeadrFootr(zCtx):
	zCtx.updateLogLvl(STEP.C04)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================= C04 SCP HEADR FOOTR : beginning =======================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#collapse header & footer for every scope (recursively)
	collapseScpHeaderAndFooter(zCtx.cpl.gblScp)
	for f in zCtx.cpl.fcts:
		collapseScpHeaderAndFooter(f.scope)

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================== C04 SCP HEADR FOOTR : end ========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#gather every scope
		output = zCtx.cpl.gblScp.toStr()
		for f in zCtx.cpl.fcts:
			output += f.scope.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c04.dl", output)
