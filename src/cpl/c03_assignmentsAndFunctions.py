#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- DCL_FCT --------

#function declaration
def readFctDcl(zCtx, ZCI):
	zCtx.ZCIDebug(ZCI, "Processing function declaration.", printSubCtxs=True)

	#function name
	rawName = zCtx.readName(ZCI, "function name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True, whitelist=FCT_NAME_CHARSET, parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)
	dotCnt  = rawName.count('.')

	#regular function
	if dotCnt == 0:
		fullName = ZCI.modulePrefix + 'F' + rawName

	#method
	elif dotCnt == 1:
		dotIndex = rawName.index('.')

		#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO 4th

		#look for method type
		#targettedType = None
		#for t in zCtx.cpl.types:
		#	if t.name == 

		fullName = "METHOD" #ZCI.modulePrefix + 'T' + targettedType.name + '_' + rawName

	#error case
	else:
		zCtx.ZCIError("Invalid function name, multiple dot separators found.")

	#parameters
	params = zCtx.readDataItemSequence(
		ZCI, "function declaration ZCI (DCL_FCT)",
		zCtx.cpl.globalScope,
		cstValuesOnly = True,
		allowEmpty    = True,
		inFctDcl      = True
	)

	#return type
	zCtx.optionnalBlanks(ZCI, None)
	if ZCI.get() == '{':
		pass #VOID <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	else:
		retType = zCtx.readType(ZCI, "return type in function declaration ZCI (DCL_FCT)")

	#content
	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO

	#result
	return zCtx.newFct(fullName, None, params)






# -------- EXECUTION --------

#compilation
def c03_assignmentsAndFunctions(zCtx, unprocessedZCIs):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : beginning ===============")
	zCtx.debug("=================================================================================\n\n\n\n")

	#global assignments
	for ZCI in unprocessedZCIs[1]:
		pass #readFctDcl(zCtx, ZCI)

	#functions
	for ZCI in unprocessedZCIs[0]:
		zCtx.cpl.functions.append( readFctDcl(zCtx, ZCI) )

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : end ===============")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx.cplStep_debugZCIs("03")
