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

	#build full function name
	fullName = ZCI.modPrefix
	if isMethod:
		fullName += 'T' + ZCI.getTypeNameFromIDIncludingUnsolved(methodType) + '_' #btw, no unsolved type can be output here
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
	ZCIDeepDebug(ZCI, "Return type detected \"" + ZCI.getTypeNameFromIDIncludingUnsolved(retType) + "\".")

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
