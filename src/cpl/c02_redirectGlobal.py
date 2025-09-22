#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#std
from std.string import *

#internal
from zctx import *
from pcpl.p3_splitZCIsAndImport import *






# -------- EXT_LNK --------

#external linking
def processLnk(ZCI):
	ZCIDebug(ZCI, "Processing SDL addition.", printSubCtxs=True, printLine=False)
	jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

	#library linking path
	path = os.path.realpath( readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS_EXTENDED) )
	endOfZCI(ZCI, "library linking ZCI (EXT_LNK).")

	#check existence
	if not os.path.isfile(path):
		ZCIError(ZCI, "Shared & Dynamically Linked (SDL) library " + path + " not found.")
	ZCIDebug(ZCI, "SDL file \"" + path + "\" found.", printLine=False)

	#add link
	if path not in zCtx.cpl.linkedLibs:
		zCtx.cpl.linkedLibs.append(path)
		ZCIDebug(ZCI, "Added SDL \"" + path + "\" to linking list.")
	else:
		ZCIDebug(ZCI, "SDL \"" + path + "\" already in linking list => skipping it.")






# -------- DCL_TYP --------

#type declaration
def processTypeDcl(ZCI):
	ZCIDebug(ZCI, "Processing type declaration.", printSubCtxs=True, printLine=False)
	jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True)
	if len(ZCI.modPrefix) == 0:
		fullName = "GU" + rawName
	else:
		fullName = ZCI.modPrefix + 'U' + rawName

	#check already existing
	if ZCI.getTypeIDFromName(fullName) != TYPE_ID__UNKNOWN:
		modPrefixText = ""
		if len(ZCI.modPrefix) != 0:
			modPrefixText = unprefixizeMod(ZCI.modPrefix)
		ZCIError(ZCI, "Type " + modPrefixText + rawName.replace("__", '_') + " already exists, can't declare a new one with the same name (DCL_TYP).")
	ZCIDeepDebug(ZCI, "New type does not exist yet.", printLine=False)

	#explicit declination degree if any
	dcnDeg = 0
	if ZCI.get() == '[':
		peerIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		ZCI.inc()

		#skip beginning blanks
		optionalBlanks(ZCI, "declination degree in type declaration ZCI (DCL_TYP)", blanks=BLANKS_EXTENDED)

		#strip ending blanks
		beginningIdx = ZCI.ctx.icontent.idx
		dcnDegText   = str_stripEnd( str_sub(ZCI.ctx.icontent.s, start=beginningIdx, stop=peerIdx-1), charset=BLANKS_EXTENDED)

		#non-integer dcnDeg
		if not str_isConvertible_int(dcnDegText):
			ZCIError(ZCI, "Invalid explicit declination degree given (must be an integer).")

		#negative dcnDeg
		dcnDeg = int(dcnDegText)
		if dcnDeg < 0:
			ZCIError(ZCI, "Invalid explicit declination degree given (must be positive).")

		#forward after includer
		ZCI.forward(peerIdx - beginningIdx + 1)
	ZCIDeepDebug(ZCI, "New type is declinable of degree " + str(dcnDeg), printLine=False)

	#must be followed by blanks once more
	if ZCI.get() not in BLANKS:
		ZCIError(ZCI, "Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
	jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

	#add generic type for the moment (it is incomplete: we don't know if it is a structure, if it has a parent...)
	newTypeID   = ZCI.zCtx.cpl.newTyp(fullName, dcnDeg)
	newTypeInst = ZCI.getTypeInstanceFromID(newTypeID)
	ZCIDebug(ZCI, "Explicitely added type " + newTypeInst.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		ZCIDebug(ZCI, "Type declaration is via structure syntax.", printLine=False)
		newTypeInst.dcnCommon.size   = ZCI.zCtx.ptrSize
		newTypeInst.dcnCommon.nature = NATURE__STC

		#reading fields
		newTypeInst.dcnCommon.fields = readDataItemSequence(
			ZCI, "type declaration ZCI (DCL_TYP).",
			ZCI.zCtx.cpl.gblScp,
			cstValuesOnly = True
		)
		if len(newTypeInst.dcnCommon.fields) == 0:
			ZCIError(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDataItemSequence cannot return 0-length list)

		#update stcSize
		newTypeInst.computeStcSize(ZCI.zCtx.cpl.types)

	#process type content: type-copy syntax
	else:
		ZCIDebug(ZCI, "Type declaration is via type-copy syntax.", printLine=False)
		parentID   = readType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		parentInst = ZCI.getTypeInstanceFromID(parentID)

		#copying itself, no matter the declination (error case seems obvious, though required)
		if parentInst.dcnCommon == newTypeInst.dcnCommon:
			ZCIError(ZCI, "Type cannot be declared as a copy of itself or one of its declination.")

		#copy every important field from parent
		newTypeInst.dcnCommon.size   = parentInst.dcnCommon.size
		newTypeInst.dcnCommon.nature = parentInst.dcnCommon.nature
		newTypeInst.dcnCommon.fields = parentInst.dcnCommon.fields
		newTypeInst.dcnCommon.parent = parentID

	#end of ZCI expected
	endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	ZCIDebug(ZCI, "Type declaration " + newTypeInst.name + " processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(ZCI, scope):
	ZCIDebug(ZCI, "Processing enumerate declaration.", printSubCtxs=True, printLine=False)
	jumpBlankZone(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM)")

	#get full enm name
	rawName  = readName(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM).", doubleUnderscores=True)
	fullName = getDataItemModPrefixFromScope(ZCI, scope) + rawName

	#must be followed by braces includer
	optionalBlanks(ZCI, "fields inside braces includer in enumerate declaration ZCI (DCL_ENM).", blanks=BLANKS_EXTENDED)
	if ZCI.get() != '{':
		ZCIError(ZCI, "Missing fields inside braces includer in enumerate declaration ZCI (DCL_ENM).")

	#read fields
	fields = readDataItemSequence(
		ZCI, "enumerate declaration ZCI (DCL_ENM).",
		scope,
		cstValuesOnly        = True,
		allowUnsolvableTypes = True
	)
	for di in fields:
		if di.Type != TYPE_ID__UNKNOWN: #no type must be found (neither explicit type given or initial value)
			ZCIError(ZCI, "No explicit type or value is allowed in enumerate declaration (DCL_ENM).")

	#compute which type will be used
	ZCIDeepDebug(ZCI, "Enumerate length: " + str(len(fields)), printLine=False)
	if len(fields) <= 0x1_00:
		ZCIDeepDebug(ZCI, "Enumerate length indexing can be contained in U1 => using that type for them.", printLine=False)
		t = ZCI.zCtx.rootTypes[RT__U1]
	elif len(fields) <= 0x1_00_00:
		ZCIDeepDebug(ZCI, "Enumerate length indexing can be contained in U2 => using that type for them.", printLine=False)
		t = ZCI.zCtx.rootTypes[RT__U2]
	elif len(fields) <= 0x1_00_00_00_00:
		ZCIDeepDebug(ZCI, "Enumerate length indexing can be contained in U4 => using that type for them.")
		t = zCtx.rootTypes[RT__U4]
	else:
		ZCIError(ZCI, "Too much fields in enumerate (congrats for reaching that error, how did you managed to get it ?).")

	#fullfill fields
	for f in range(len(fields)):
		fields[f].Type  = t
		fields[f].value = value(t, atm(ATM__PTR, f), Cst=True) #value stored as it was a ptr to be cashted into type t

	#create enumerate
	enmDI = dataItem(t, fullName, True, None, Cst=True, fields=fields)
	checkAlreadyDeclaredDataItemOrField(ZCI, enmDI, scope.dataItems)
	scope.dataItems.append(enmDI)

	#end of ZCI expected
	endOfZCI(ZCI, "enumerate declaration ZCI (DCL_ENM).")
	ZCIDebug(ZCI, "Enumerate declaration processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()






# -------- DCL_FCT --------

#function declaration
def processFctDcl(ZCI):
	ZCIDebug(ZCI, "Processing function declaration.", printSubCtxs=True)

	#function name: maybe it is type related (method) => try reading a type
	methodType = readType(ZCI, "function name in function declaration ZCI (DCL_FCT).", errorIfNotExisting=False)

	#method name must be followed by a dot
	isMethod = (methodType != TYPE_ID__UNKNOWN)
	if isMethod:
		if ZCI.get() != '.':
			ZCIError(ZCI, "Expected a dot '.' after type given in method name.")
		ZCI.inc()

	#read function name
	rawName = readName(ZCI, "function name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True, whitelist=FCT_NAME_CHARSET)

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
	for p in params: #add "lcl" module prefix
		p.name = 'L' + p.name

	#targetting operator
	isOpe = (rawName in OPERATOR_FCTNAME2SYMBOL.keys())

	#case 1: regular function
	if not isOpe:

		#additionnal check: name availability !HERE, WE WANT TO GUARANTEE NO CONFUSION BETWEEN GBL DI NAMES & FCT NAMES. USER CODE CAN HAVE AMBIGUITY, BUT Z NOTATION CAN'T: THIS IS WHY WE USE A "TMP PREFIXED NOTATION" TO CHECK THEM TEMPORARILY.
		if not isMethod:
			equivalentDIName = getDataItemModPrefixFromScope(ZCI, ZCI.zCtx.cpl.gblScp)
			for gdi in ZCI.zCtx.cpl.gblScp.dataItems:
				if gdi.name == equivalentDIName:
					ZCIError(ZCI, "Unable to declare function \"" + ZCI.modPrefix + rawName + "\" because a global data item with the same name already exist (avoiding confusion).")

		#build full function name
		fullName = getFctNameFromPrefixedName(ZCI, ZCI.modPrefix + rawName, methodOf=methodType)

	#case 2: operator
	else:
		if isMethod:
			ZCIError(ZCI, "Operator functions cannot be used as methods for a given type (type " + ZCI.getTypeNameFromID(methodType) + " targetted for operator " + OPERATOR_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]] + ").")

		#build full function name
		fullName = 'O' + OPERATOR_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]]
		for p in params:
			fullName += '_' + ZCI.getTypeNameFromID(p.Type)

	#check if function/method/operator already exists
	if getFctFromName(ZCI, fullName) is not None:
		ZCIError(ZCI, "Already have a function/method/operator with name " + fullName)

	#return type: void
	optionalBlanks(ZCI, None)
	if ZCI.get() == '{':
		retType = TYPE_ID__UNKNOWN

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
	#ZCI.zCtx.debugMode     = DBG_MODES[DBG__P3]
	#ZCI.zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__P3]
	content = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl           = False,
		modPrefix     = ZCI.modPrefix,
		maxIdxAllowed = ZCI.pairs[ZCI.ctx.icontent.idx]-1
	)
	#ZCI.zCtx.debugMode     = DBG_MODES[DBG__C02]
	#ZCI.zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__C02]
	ZCI.inc()
	ZCIDeepDebug(ZCI, "End of extraction for function \"" + fullName + "\".")

	#create fct instance
	f = newFct(fullName, retType, params, ZCI.zCtx.cpl.gblScp, content)

	#add params as available data items in fct scope
	for p in params:
		f.scope.dataItems.append(p)

	#store result into cpl fcts
	ZCI.zCtx.cpl.fcts.append(f)
	ZCIDeepDebug(ZCI, "Added to CPL data: " + f.toStr(ZCI), printSubCtxs=False, printLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "function declaration ZCI (DCL_FCT).")
	ZCIDebug(ZCI, "Function declaration processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()






# -------- REMAINING ZCIs: VFC_VFC, ASG_ASG, DCL_DAT --------

#data item assignment only (assigning to existing destination) WARNING: ZCI must be RIGHT BEFORE SRC VALUE !
def processAsg(ZCI, scope, inGblScp, dstDI):
	ZCIDebug(ZCI, "Processing data item assignment (ASG_ASG).", printSubCtxs=True, printLine=False)

	#read src value to be assigned
	srcValue = readValue(ZCI, "source value in assignment (ASG_ASG).", scope, cstOnly=inGblScp)

	#add execution to concerned scope
	scope.exes.append( atm(ATM__ASG, asg(dstDI, srcValue)) )

	#end of ZCI expected
	endOfZCI(ZCI, "data item assignment (ASG_ASG).")

	#debug
	ZCIDebug(ZCI, "Data item assignment processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()



#data item declaration (including assignment with initial value)
def processDclDat(ZCI, scope, inGblScp, isCst, forbidTypKeyword=True):
	ZCIDebug(ZCI, "Processing data item declaration (DCL_DAT).", printSubCtxs=True, printLine=False)

	#read the whole ZCI from the start
	di = readDataItem(ZCI, "Data item declaration (DCL_DAT).", scope, cstInitialValueOnly=inGblScp)

	#check the use of "typ" keyword in dcl type (this is only possible in declinations btw: "ref[typ] a = ...")
	if forbidTypKeyword:
		if ZCI.checkIDRecursivelyInType(di.Type, ZCI.zCtx.typKeyword):
			ZCIError(ZCI, "Cannot use keyword \"typ\" as type in data item declaration here.")

	#don't allow the use of module notation in name when declaring !
	givenModPrefix = extractModPrefix(di.name)
	if len(givenModPrefix) != 0:
		ZCIError(ZCI, "Cannot use module notation in name when declaring a data item (DCL_DAT detected, declare inside module instead).")

	#set some important info to the NEWLY CREATED data item
	di.name = getDataItemModPrefixFromScope(ZCI, scope) + di.name
	di.Cst  = isCst

	#add declaration to scope
	checkAlreadyDeclaredDataItemOrField(ZCI, di, scope.dataItems) #check already existing
	scope.dataItems.append(di)

	#end of ZCI expected
	endOfZCI(ZCI, "data item declaration ZCI (DCL_DAT).")

	#debug
	ZCIDebug(ZCI, "Data item declaration processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()



#concerns more step 3 actually
def processVFC(ZCI, scope, inGblScp):
	ZCIDebug(ZCI, "Processing void returning function call (VFC_VFC).", printSubCtxs=True, printLine=False)

	#local scope only
	if inGblScp:
		ZCIError(ZCI, "Detected void returning function call but this is only allowed in local scope (VFC_VFC).")

	#read ZCI content as reading a value: it MUST be a call (either operator, !VFC or VFC)
	v = readValue(ZCI, "void returning function call (VFC_VFC).", scope)
	if v.vdata.id != ATM__CALL:
		ZCIError(ZCI, "Invalid ZCS, unknown ZCI given. (Expected a void returning function call, VFC_VFC).")

	#store call in scope exe <---- Note that we don't care about the return type for the moment, it can be anything
	scope.exes.append(v.vdata)

	#end of ZCI expected
	endOfZCI(ZCI, "void returning function call (VFC_VFC).")

	#debug
	ZCIDebug(ZCI, "Void returning function call processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()



#remaining ZCIs can be DCL_DAT, ASG_ASG or VFC_VFC (the last one only allowed in local scope)
def processRemainingZCI(ZCI, scope, forbidTypKeywordInDatDcl=True):

	#being in global scope affects further behaviors
	inGblScp = False
	if scope == ZCI.zCtx.cpl.gblScp:
		inGblScp = True

	#try reading a type (in a separated copy, in all cases we will have to read from the start)
	tmpCopy = ZCI.copy()
	tID     = readType(tmpCopy, None, errorIfNotExisting=False)

	#starting with a type name => DCL_DAT, else => can be anything
	if tID == TYPE_ID__UNKNOWN:

		#try getting a name
		name = readName(tmpCopy, None, parseModPrefixes=True, modPrefixes_asHeaderOnly=True)

		#no name => can only be a VFC_VFC
		if len(name) == 0:
			processVFC(ZCI, scope, inGblScp)
			return

		#got a name, well OK, but it can still be a VFC_VFC... unless we don't have asg symbol !
		optionalBlanks(tmpCopy, None)
		if readSymbol(tmpCopy) != SYMBOL__ASG:
			processVFC(ZCI, scope, inGblScp)
			return

		#already have a data item with that name => ASG_ASG then
		di = getDataItemFromPrefixedName(name, scope)
		if di is not None:

			#forward right before value
			tmpCopy.forward(SYMBOL_LENGTHS[SYMBOL__ASG])
			optionalBlanks(tmpCopy, None)

			#process ASG_ASG
			ZCI.forwardAlike(tmpCopy)
			processAsg(ZCI, scope, inGblScp, di)
			return

	#in every other cases => DCL_DAT
	processDclDat(ZCI, scope, inGblScp, False, forbidTypKeyword=forbidTypKeywordInDatDcl)






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):
	zCtx.debugSepLine()
	zCtx.debug("=================================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.debug("=================================================================================")
	zCtx.deepDebugPause()

	#analyse every global ZCI
	for ZCI in zCtx.ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDeepDebug(ZCI, "Treating global ZCI \"" + ZCI.textFormat() + '\"', printSubCtxs=True)

		#read 1st ZCI word
		firstWord = readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)



		#CASE 1 - BEGINNING WITH KEYWORD AND FORBIDDEN

		#bigrams
		if len(firstWord) == 2:
			if str_cmp("if", firstWord):
				ZCIError(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")

		#trigrams
		elif len(firstWord) == 3:

			#1.1 - jumps
			if str_cmp("brk", firstWord):
				ZCIError(ZCI, "BREAK jumps are not allowed in global scope (JMP_BRK detected).")
			if str_cmp("ctn", firstWord):
				ZCIError(ZCI, "CONTINUE jumps are not allowed in global scope (JMP_CTN detected).")
			if str_cmp("ret", firstWord):
				ZCIError(ZCI, "RETURN jumps are not allowed in global scope (JMP_RET detected).")

			#1.2 - statements
			if str_cmp("elf", firstWord) or str_cmp("els", firstWord):
				ZCIError(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")
			if str_cmp("for", firstWord):
				ZCIError(ZCI, "FOR statements are not allowed in global scope (STM_FOR detected).")
			if str_cmp("while", firstWord):
				ZCIError(ZCI, "WHILE statements are not allowed in global scope (STM_WHI detected).")
			if str_cmp("swi", firstWord):
				ZCIError(ZCI, "SWITCH statements are not allowed in global scope (STM_SWI detected).")

			#1.3 - remaining imports (should never occur)
			if str_cmp("imp", firstWord):
				ZCIInternal(ZCI, "Must not have any importation remaining at that step.")



			#CASE 3 - BEGINNING WITH KEYWORD AND ALLOWED

			#trigrams requiring a following blank
			if ZCI.txt[3] in BLANKS:

				#2.1 - library linking
				if str_cmp("lnk", firstWord):
					processLnk(ZCI)
					continue

				#2.2 - type declaration DCL_TYP
				if str_cmp("typ", firstWord):
					processTypeDcl(ZCI)
					continue

				#2.3 - Enumerate declaration DCL_ENM
				if str_cmp("enm", firstWord):
					processEnmDcl(ZCI, ZCI.zCtx.cpl.gblScp)
					continue

				#2.4 - Function declaration
				if str_cmp("fct", firstWord):
					jumpBlankZone(ZCI, "Function name in function declaration ZCI (DCL_FCT).") #forward to function name directly
					processFctDcl(ZCI)
					continue

				#2.5 - Constant data item declaration
				if str_cmp("cst", firstWord):
					jumpBlankZone(ZCI, "Constant keyword in data item declaration ZCI (DCL_DAT).")
					processDclDat(ZCI, zCtx.cpl.gblScp, True, True)
					continue



		#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

		#reset ZCI at initial state & try parsing it, no other possibility for a global ZCI
		ZCI.resetCtx(initialCtx)
		processRemainingZCI(ZCI, zCtx.cpl.gblScp)

	#debug
	zCtx.debug("===========================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.debug("===========================================================================")
	zCtx.debugSepLine()
	zCtx.deepDebugPause()

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "02")
