#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- DCL_FCT --------

#function declaration
def readFctDcl(ZCI):
	ZCIDebug(ZCI, "Processing function declaration.", printSubCtxs=True)

	#function name
	rawName = readName(ZCI, "function name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True, whitelist=FCT_NAME_CHARSET, parseModPrefixes=True, modPrefix_asHeaderOnly=True)
	dotCnt  = rawName.count('.')

	#regular function
	if dotCnt == 0:
		fullName = ZCI.modPrefix + 'F' + rawName

	#method
	elif dotCnt == 1:
		dotIdx = rawName.index('.')

		#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO 4th

		#look for method type
		#targettedType = None
		#for t in zCtx.cpl.types:
		#	if t.name == 

		fullName = "METHOD" #ZCI.modulePrefix + 'T' + targettedType.name + '_' + rawName

	#error case
	else:
		ZCIError(ZCI, "Invalid function name, multiple dot separators found.")

	#parameters
	params = readDataItemSequence(
		ZCI, "function declaration ZCI (DCL_FCT)",
		ZCI.zCtx.cpl.gblScp,
		cstValuesOnly = True,
		allowEmpty    = True
	)

	#return type
	optionalBlanks(ZCI, None)
	if ZCI.get() == '{':
		pass #VOID <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	else:
		retType = readType(ZCI, "return type in function declaration ZCI (DCL_FCT)")

	#content
	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO

	#result
	return newFct(fullName, None, params, ZCI.zCtx.cpl.gblScp)






# -------- EXECUTION --------

#compilation
def c03_assignmentsAndFunctions(zCtx, unprocessedZCIs):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : beginning ===============")
	zCtx.debug("=================================================================================\n\n\n\n")

	#global assignments
	for ZCI in unprocessedZCIs[1]:
		pass

	#functions
	for ZCI in unprocessedZCIs[0]:
		zCtx.cpl.fcts.append( readFctDcl(ZCI) )

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : end ===============")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "03")
