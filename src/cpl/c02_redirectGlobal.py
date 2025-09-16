#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#std
from std.string import *

#internal
from zctx import *






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
	if ZCI.getTypeIDFromName(fullName) != TYPE_ID__NOT_FOUND:
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
		if parentInst.dcnCommon == newTypeInst.dcnCommon:
			ZCIError(ZCI, "Type cannot be declared as a copy of itself or one of its declination.") #seems obvious, but anyway
		newTypeInst.dcnCommon.size   = parentInst.dcnCommon.size
		newTypeInst.dcnCommon.nature = parentInst.dcnCommon.nature
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
		if di.Type != TYPE_ID__NOT_FOUND: #no type must be found (neither explicit type given or initial value)
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






# -------- DCL_DAT & ASG_ASG --------

#data item assignment only (assigning to existing destination) WARNING: ZCI must be RIGHT AFTER destination expression !
def processAsg(ZCI, scope, dstDI):

	#being in global scope affects further behaviors
	inGblScp = False
	if scope == ZCI.zCtx.cpl.gblScp:
		inGblScp = True

	#assignment symbol must follow
	optionalBlanks(ZCI, None)
	if readSymbol(ZCI) != SYMBOL__ASG:
		ZCIError(ZCI, "Expected an assignment symbol here (ASG_ASG ZCI detected).")
	ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])

	#then a value
	v = readValue(ZCI, "assignment ZCI (ASG_ASG).", scope, cstOnly=inGblScp)

	#add execution to concerned scope
	scope.exes.append( atm(ATM__ASG, asg(dstDI, v)) )

	#end of ZCI expected
	endOfZCI(ZCI, "data item assignment ZCI (ASG_ASG).")

	#debug
	ZCIDebug(ZCI, "Data item assignment processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()



#data item declaration (including assignment with initial value)
def processDclDat(ZCI, scope, isCst):

	#being in global scope affects further behaviors
	inGblScp = False
	if scope == ZCI.zCtx.cpl.gblScp:
		inGblScp = True

	#read the whole ZCI from the start
	di = readDataItem(ZCI, "Data item declaration (DCL_DAT).", scope, cstInitialValueOnly=inGblScp)

	#don't allow the use of module notation in name when declaring !
	givenModPrefix = extractModPrefix(di.name)
	if len(givenModPrefix) != 0:
		ZCIError(ZCI, "Cannot use module notation in name when declaring a data item (DCL_DAT ZCI detected, declare inside module instead).")

	#set some important info to the NEWLY CREATED data item
	di.name = getDataItemModPrefixFromScope(ZCI, scope) + di.name #add module prefix to name ONLY IF WE ARE DECLARING !!! Else, we are affecting a regular global data item (even if inside a module)
	di.Cst  = isCst

	#add declaration to scope
	checkAlreadyDeclaredDataItemOrField(ZCI, di, scope.dataItems) #check already existing
	scope.dataItems.append(di)

	#end of ZCI expected
	endOfZCI(ZCI, "data item declaration ZCI (DCL_DAT).")

	#debug
	ZCIDebug(ZCI, "Data item declaration processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()



#data item declaration or assignment
def processDclOrAsg(ZCI, scope):
	ZCIDebug(ZCI, "Processing data item declaration or assignment.", printSubCtxs=True, printLine=False)

	#try getting a "cst" keyword
	initialCtx = ZCI.ctx.copy()
	cstKeyword = readName(ZCI, None)
	isCst      = (cstKeyword == "cst")

	#move on
	if isCst:
		optionalBlanks(ZCI, None) #actually, blanks are not optional here, but we expect to have at least 2 names separated here ("cst <type> ..." or "cst <name> ..." => can be only OK using blanks)
	else:
		ZCI.resetCtx(initialCtx) #constant keyword not found => reset ZCI

	#try reading a type (in a separated copy, in all cases we will have to read from the start)
	tmpCopy = ZCI.copy()
	tID     = readType(tmpCopy, None, errorIfNotExisting=False)

	#not starting with a type name => can possibly be just an assignment without declaration
	if tID == TYPE_ID__NOT_FOUND:

		#get targetted name
		name = readName(tmpCopy, "Data item name in assignment (ASG_ASG).", parseModPrefixes=True, modPrefixes_asHeaderOnly=True)

		#already have a data item with that name => ASG_ASG then
		di = getDataItemFromPrefixedName(name, scope)
		if di is not None:
			ZCI.forwardAlike(tmpCopy)
			processAsg(ZCI, scope, di)
			return

	#also check the use of "typ" keyword, forbidden here
	elif tmpCopy.checkIDRecursivelyInType(tID, tmpCopy.zCtx.typKeyword):
		ZCIError(tmpCopy, "Cannot use keyword \"typ\" in data item declaration.")

	#in every other cases => DCL_DAT
	processDclDat(ZCI, scope, isCst)






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.debug("=================================================================================\n\n\n\n")

	#prepare result for next step
	fctZCIs = []

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDeepDebug(ZCI, "Treating ZCI \"" + ZCI.textFormat() + '\"', printSubCtxs=True)

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
					fctZCIs.append(ZCI) #to be processed later
					continue



		#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

		#reset ZCI at initial state & try parsing it, no other possibility for a global ZCI
		ZCI.resetCtx(initialCtx)
		processDclOrAsg(ZCI, zCtx.cpl.gblScp)

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "02")

	#return unprocessed ZCIs
	return fctZCIs
