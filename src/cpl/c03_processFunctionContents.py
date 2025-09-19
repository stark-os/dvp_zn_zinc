#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#compilation
def c03_processFunctionContents(zCtx):
	zCtx.debugSepLine()
	zCtx.debug("=================================================================================")
	zCtx.debug("=================== C03 PROCESS FUNCTION CONTENTS : beginning ===================")
	zCtx.debug("=================================================================================")
	zCtx.deepDebugPause()

	#for each function
	for f in zCtx.cpl.fcts:

		#skip LLI fcts
		if f.content is None:
			continue

		#process content
		for ZCI in f.content:

			#
			pass

	#debug
	zCtx.debug("===========================================================================")
	zCtx.debug("=================== C03 PROCESS FUNCTION CONTENTS : end ===================")
	zCtx.debug("===========================================================================")
	zCtx.debugSepLine()
	zCtx.deepDebugPause()

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "03")
