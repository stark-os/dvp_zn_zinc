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
	if ZCI.zCtx.getType(fullName) is not None:
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
	newType = newTyp(fullName, dcnDeg)
	ZCI.zCtx.cpl.types.append(newType)
	ZCIDebug(ZCI, "Explicitely added type " + newType.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		ZCIDebug(ZCI, "Type declaration is via structure syntax.", printLine=False)
		newType.commonDcnData.size   = ZCI.zCtx.rootTypes[RT__PTR].size
		newType.commonDcnData.nature = NATURE__STRUCTURE

		#reading fields
		newType.commonDcnData.fields = readDataItemSequence(
			ZCI, "type declaration ZCI (DCL_TYP).",
			ZCI.zCtx.cpl.gblScp,
			cstValuesOnly = True
		)
		if len(newType.commonDcnData.fields) == 0:
			ZCIError(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDataItemSequence cannot return 0-length list)

		#update stcSize
		newType.computeStcSize()

	#process type content: type-copy syntax
	else:
		ZCIDebug(ZCI, "Type declaration is via type-copy syntax.", printLine=False)
		parent = readType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		if parent.commonDcnData == newType.commonDcnData:
			ZCIError(ZCI, "Type cannot be declared as a copy of itself or one of its declination.") #seems obvious, but anyway
		newType.commonDcnData.size   = parent.commonDcnData.size
		newType.commonDcnData.nature = parent.commonDcnData.nature
		newType.commonDcnData.parent = parent

	#end of ZCI expected
	endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	ZCIDebug(ZCI, "Type declaration " + newType.name + " processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(ZCI, scope):
	ZCIDebug(ZCI, "Processing enumerate declaration.", printSubCtxs=True, printLine=False)
	jumpBlankZone(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM)")

	#set scope prefix
	if scope == ZCI.zCtx.cpl.gblScp:
		if len(ZCI.modPrefix) == 0:
			scpPrefix = ZCI.modPrefix + 'E' #global "element" (not "enumerate", there is no distinction with other data items)
		else:
			scpPrefix = "GE"
	else:
		scpPrefix = 'L' #"local" element

	#get full enm name
	rawName  = readName(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM).", doubleUnderscores=True)
	fullName = scpPrefix + rawName

	#must be followed by braces includer
	optionalBlanks(ZCI, "fields inside braces includer in enumerate declaration ZCI (DCL_ENM).", blanks=BLANKS_EXTENDED)
	if ZCI.get() != '{':
		ZCIError(ZCI, "Missing fields inside braces includer in enumerate declaration ZCI (DCL_ENM).")

	#read fields
	fields = readDataItemSequence(
		ZCI, "enumerate declaration ZCI (DCL_ENM).",
		scope,
		cstValuesOnly      = True,
		allowUnsolvedTypes = True
	)
	for di in fields:
		if di.Type != None: #no type must be found (neither explicit type given or initial value)
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
	checkAlreadyDeclaredDataItemOrField(ZCI, scope.dataItems, fullName)
	scope.dataItems.append( dataItem(t, fullName, True, None, Cst=True, fields=fields) )

	#end of ZCI expected
	endOfZCI(ZCI, "enumerate declaration ZCI (DCL_ENM).")
	ZCIDebug(ZCI, "Enumerate declaration processed.", printLine=False)
	ZCI.zCtx.deepDebugPause()






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.debug("=================================================================================\n\n\n\n")

	#prepare result for next step
	unprocessedZCIs = (
		[], #function declarations
		[]  #assignments
	)

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDeepDebug(ZCI, "Treating ZCI " + ZCI.textFormat(), printSubCtxs=True)

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
					jumpBlankZone(ZCI, "Function name in function declaration ZCI (DCL_FCT).")
					unprocessedZCIs[0].append(ZCI) #to be processed later, and also forwarded ZCI to function name.
					continue



		#CASE 3 - ASSIGNMENT OR FUNCTION

		#will be treated later => store it for now
		ZCI.resetCtx(initialCtx)
		unprocessedZCIs[1].append(ZCI)

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "02")

	#return unprocessed ZCIs
	return unprocessedZCIs
