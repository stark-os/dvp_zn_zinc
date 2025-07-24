#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- DCL_FCT --------

#function declaration
def readFctDcl(zCtx, ZCI):
	zCtx.ZCIDebug(ZCI, "Processing function declaration.", printSubCtxs=True)
	zCtx.jumpBlankZone(ZCI, "Function name in function declaration ZCI (DCL_FCT)")

	#return type
	retType = zCtx.readType(ZCI, "return type in function declaration ZCI (DCL_FCT)")

	#function name
	rawName = zCtx.readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True, whitelist=FCT_NAME_CHARSET, parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)
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

		fullName = ZCI.modulePrefix + 'T' + targettedType.name + '_' + rawName

	#error case
	else:
		zCtx.ZCIError("Invalid function name, multiple dot separators found.")

	#parameters
	params = self.readDataItemSequence(
		ZCI, "function declaration ZCI (DCL_FCT)",
		zCtx.cpl.globalScope,
		cstValuesOnly      = True,
		allowUnsolvedTypes = True
	)

	#self keyword
	for p in range(len(params)):
		if params[p].name == "self":
			self.deepDebug("Detected self keyword => overwritting it with generic self parameter.")
			params[p] = dataItem(
				self.rootTypes[RT__BOO],
				"self",
				True,
				value(self.rootTypes[RT__BOO], True, constant=True)
			)

		#if it is not "self", we must have a valid type
		elif params[p].Type is None:
			self.ZCIError(ZCI, "Missing type or default value to function parameter \"" + params[p].name + "\".")

	#result
	return fct(fullName, params, zCtx.cpl.globalScope)






# -------- EXECUTION --------

#compilation
def c03_assignmentsAndFunctions(zCtx, unprocessedZCIs):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("=================== C03 ASSIGNMENTS AND FUNCTIONS : beginning ===================")
	zCtx.debug("=================================================================================\n\n\n\n")

	#analyse EVERY remaining global ZCI
	for ZCI in unprocessedZCIs:

		#try reading a type
		#Type = zCtx.readType(ZCI, "Determining ZCI kind", nullIfNotExisting=True)
		#if Type is None:
		#	name = zCtx.readName(ZCI, )
		zCtx.fullDebug("GOT " + ZCI.toStr())

		#zCtx.cpl.functions.append(zCtx.readFctDcl(fZCI)) <<<<<<<<<<<<<<<<<<<<<<<<<<< disabled for the moment

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("=================== C03 ASSIGNMENTS AND FUNCTIONS : end ===================")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx.cplStep_debugZCIs("03")
