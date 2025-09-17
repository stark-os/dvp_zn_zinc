#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *
from zctx                       import *






# -------- DCL_FCT --------

#function declaration
def readFctDcl(ZCI):
	ZCIDebug(ZCI, "Processing function declaration.", printSubCtxs=True)

	#function name: maybe it is type related (method) => try reading a type
	methodType = readType(ZCI, "function name in function declaration ZCI (DCL_FCT).", errorIfNotExisting=False)

	#method name must be followed by a dot
	isMethod = (methodType != TYPE_ID__NOT_FOUND)
	if isMethod:
		if ZCI.get() != '.':
			ZCIError(ZCI, "Expected a dot '.' after type given in method name.")
		ZCI.inc()

	#read function name
	rawName = readName(ZCI, "function name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True, whitelist=FCT_NAME_CHARSET)

	#check name availability !HERE, WE WANT TO GUARANTEE NO CONFUSION BETWEEN GBL DI NAMES & FCT NAMES. USER CODE CAN HAVE AMBIGUITY, BUT Z NOTATION CAN'T: THIS IS WHY WE USE A "TMP PREFIXED NOTATION" TO CHECK THEM TEMPORARILY.
	tmpPrefixedName = ZCI.modPrefix + rawName
	for gdi in ZCI.zCtx.cpl.gblScp.dataItems:
		if gdi.name == tmpPrefixedName:
			ZCIError(ZCI, "Unable to declare function \"" + modPrefixedName + "\" (tmp prefixed notation) because a global data item with the same name already exist.")

	#build full function name (with real prefixing this time)
	fullName = ZCI.modPrefix
	if isMethod:
		fullName += 'T' + ZCI.getTypeNameFromID(methodType) + '_'
	fullName += 'F' + rawName

	#must be followed by parameters between parentheses includer
	if ZCI.get() != '(':
		ZCIError(ZCI, "Expected parameters between parentheses includer right after function name.")

	#parameters
	params = readDataItemSequence(
		ZCI, "function declaration ZCI (DCL_FCT)",
		ZCI.zCtx.cpl.gblScp,
		cstValuesOnly = True,
		allowEmpty    = True
	)

	#return type: void
	optionalBlanks(ZCI, None)
	if ZCI.get() == '{':
		retType = TYPE_ID__NOT_FOUND

	#return type: explicitly given
	else:
		retType = readType(ZCI, "return type in function declaration ZCI (DCL_FCT)")

		#move to function content
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
		if ZCI.get() != '{':
			ZCIError(ZCI, "Expected to have function content after return type given (braces includer).")
	ZCIDeepDebug(ZCI, "Return type detected \"" + ZCI.getTypeNameFromID(retType) + "\".")

	#content
	ZCIDeepDebug(ZCI, "Extracting function \"" + fullName + "\"'s content.")
	content = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl           = False,
		modPrefix     = ZCI.modPrefix,
		maxIdxAllowed = ZCI.pairs[ZCI.ctx.icontent.idx]-1
	)
	ZCIDeepDebug(ZCI, "End of extraction for function \"" + fullName + "\".")

	#result
	return newFct(fullName, retType, params, ZCI.zCtx.cpl.gblScp, content)






# -------- EXECUTION --------

#compilation
def c03_assignmentsAndFunctions(zCtx, fctZCIs):
	zCtx.debugSepLine()
	zCtx.debug("=================================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : beginning ===============")
	zCtx.debug("=================================================================================")
	zCtx.deepDebugPause()

	#for each function
	for fZCI in fctZCIs:

		#process DCL_FCT
		f = readFctDcl(fZCI)
		zCtx.cpl.fcts.append(f)

		#process internal content
		#for ZCI in f.content:
		#	...

	#debug
	zCtx.debug("===========================================================================")
	zCtx.debug("================ C03 GLOBAL ASSIGNMENTS AND FUNCTIONS : end ===============")
	zCtx.debug("===========================================================================")
	zCtx.debugSepLine()
	zCtx.deepDebugPause()

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "03")
