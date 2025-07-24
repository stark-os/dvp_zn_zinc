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
def processLnk(zCtx, ZCI):
	zCtx.ZCIDebug(ZCI, "Processing SDL addition.", printSubCtxs=True)
	zCtx.jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

	#library linking path
	path = os.path.realpath( zCtx.readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS_EXTENDED) )
	zCtx.endOfZCI(ZCI, "library linking ZCI (EXT_LNK).")

	#check existence
	if not os.path.isfile(path):
		zCtx.ZCIError(ZCI, "Shared & Dynamically Linked (SDL) library " + path + " not found.")
	zCtx.debug("SDL file \"" + path + "\" found.")

	#add link
	if path not in zCtx.cpl.linkedLibs:
		zCtx.cpl.linkedLibs.append(path)
		zCtx.ZCIDebug(ZCI, "Added SDL \"" + path + "\" to linking list.")
	else:
		zCtx.ZCIDebug(ZCI, "SDL \"" + path + "\" already in linking list => skipping it.")






# -------- DCL_TYP --------

#type declaration

def processTypeDcl(zCtx, ZCI):
	zCtx.ZCIDebug(ZCI, "Processing type declaration.", printSubCtxs=True)
	zCtx.jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = zCtx.readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True)
	if len(ZCI.modulePrefix) == 0:
		fullName = "GU" + rawName
	else:
		fullName = ZCI.modulePrefix + 'U' + rawName

	#check already existing
	if zCtx.getType(fullName) is not None:
		modulePrefixText = ""
		if len(ZCI.modulePrefix) != 0:
			modulePrefixText = unprefixizeModule(ZCI.modulePrefix)
		zCtx.ZCIError(ZCI, "Type " + modulePrefixText + rawName.replace("__", '_') + " already exists, can't declare a new one with the same name (DCL_TYP).")
	zCtx.deepDebug("New type does not exist yet.")

	#explicit declination degree if any
	dcnDeg = 0
	if ZCI.get() == '[':
		peerIndex = ZCI.pairs[ZCI.ctx.icontent.index]
		ZCI.inc()

		#skip beginning blanks
		zCtx.optionnalBlanks(ZCI, "declination degree in type declaration ZCI (DCL_TYP)", blanks=BLANKS_EXTENDED)

		#strip ending blanks
		beginningIndex = ZCI.ctx.icontent.index
		dcnDegText = str_stripEnd( str_sub(ZCI.ctx.icontent.s, start=beginningIndex, stop=peerIndex-1), charset=BLANKS_EXTENDED)

		#non-integer dcnDeg
		if not str_isConvertible_int(dcnDegText):
			zCtx.ZCIError(ZCI, "Invalid explicit declination degree given (must be an integer).")

		#negative dcnDeg
		dcnDeg = int(dcnDegText)
		if dcnDeg < 0:
			zCtx.ZCIError(ZCI, "Invalid explicit declination degree given (must be positive).")

		#forward after includer
		ZCI.forward(peerIndex - beginningIndex + 1)
	zCtx.deepDebug("New type is declinable of degree " + str(dcnDeg))

	#must be followed by blanks once more
	if ZCI.get() not in BLANKS:
		zCtx.ZCIError(ZCI, "Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
	zCtx.jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

	#add generic type for the moment (it is incomplete: we don't know if it is a structure, if it has a parent...)
	newType = newTyp(fullName, dcnDeg)
	zCtx.cpl.types.append(newType)
	zCtx.ZCIDebug(ZCI, "Explicitely added type " + newType.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		zCtx.debug("Type declaration is via structure syntax.", printLine=False)
		newType.commonDcnData.size   = zCtx.SIZE__LNG
		newType.commonDcnData.nature = NATURE__STRUCTURE

		#reading fields
		newType.commonDcnData.fields = zCtx.readDataItemSequence(
			ZCI, "type declaration ZCI (DCL_TYP).",
			zCtx.cpl.globalScope,
			cstValuesOnly = True
		)
		if len(newType.commonDcnData.fields) == 0:
			zCtx.ZCIError(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDataItemSequence cannot return 0-length list)

		#update stcSize
		newType.computeStcSize()

	#process type content: type-copy syntax
	else:
		zCtx.debug("Type declaration is via type-copy syntax.", printLine=False)
		parent = zCtx.readType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		if parent.commonDcnData == newType.commonDcnData:
			zCtx.ZCIError(ZCI, "Type cannot be declared as a copy of itself or one of its declination.") #seems obvious, but anyway
		newType.commonDcnData.size   = parent.commonDcnData.size
		newType.commonDcnData.nature = parent.commonDcnData.nature
		newType.commonDcnData.parent = parent

	#end of ZCI expected
	zCtx.endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	zCtx.debug("Type declaration " + newType.name + " processed.")
	zCtx.deepDebugPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(zCtx, ZCI, scope):
	zCtx.ZCIDebug(ZCI, "Processing enumerate declaration.", printSubCtxs=True)
	zCtx.jumpBlankZone(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM)")

	#set scope prefix
	if scope == zCtx.cpl.globalScope:
		if len(ZCI.modulePrefix) == 0:
			scopePrefix = ZCI.modulePrefix + 'E' #global "element" (not "enumerate", there is no distinction with other data items)
		else:
			scopePrefix = "GE"
	else:
		scopePrefix = 'L' #"local" element

	#get full enm name
	rawName  = zCtx.readName(ZCI, "Enumerate name in enumerate declaration ZCI (DCL_ENM).", doubleUnderscores=True)
	fullName = scopePrefix + rawName

	#must be followed by braces includer
	zCtx.optionnalBlanks(ZCI, "fields inside braces includer in enumerate declaration ZCI (DCL_ENM).", blanks=BLANKS_EXTENDED)
	if ZCI.get() != '{':
		zCtx.ZCIError(ZCI, "Missing fields inside braces includer in enumerate declaration ZCI (DCL_ENM).")

	#read fields
	fields = zCtx.readDataItemSequence(
		ZCI, "enumerate declaration ZCI (DCL_ENM).",
		scope,
		cstValuesOnly      = True,
		allowUnsolvedTypes = True
	)
	for di in fields:
		if di.Type != None: #no type must be found (neither explicit type given or initial value)
			zCtx.ZCIError(ZCI, "No explicit type or value is allowed in enumerate declaration (DCL_ENM).")

	#compute which type will be used
	zCtx.deepDebug("Enumerate length: " + str(len(fields)))
	if len(fields) <= 0x1_00:
		zCtx.deepDebug("Enumerate length indexing can be contained in BYT => using that type for them.")
		t = zCtx.rootTypes[RT__BYT]
	elif len(fields) <= 0x1_00_00:
		zCtx.deepDebug("Enumerate length indexing can be contained in SHR => using that type for them.")
		t = zCtx.rootTypes[RT__SHR]
	elif len(fields) <= 0x1_00_00_00_00:
		zCtx.deepDebug("Enumerate length indexing can be contained in INT => using that type for them.")
		t = zCtx.rootTypes[RT__INT]
	else:
		zCtx.ZCIError(ZCI, "Too much fields in enumerate (congrats for reaching that error, how did you managed to get it ?).")

	#fullfill fields
	for f in range(len(fields)):
		fields[f].Type = t
		fields[f].value = value(t, atm(ATM__ULNG, f), constant=True) #value stored as it was a ulng literal to be cashted into type t

	#create enumerate
	zCtx.checkAlreadyDeclaredDataItemOrField(ZCI, scope.dataItems, fullName)
	scope.dataItems.append( dataItem(t, fullName, True, None, constant=True, fields=fields) )

	#end of ZCI expected
	zCtx.endOfZCI(ZCI, "enumerate declaration ZCI (DCL_ENM).")
	zCtx.debug("Enumerate declaration processed.")
	zCtx.deepDebugPause()






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.debug("=================================================================================\n\n\n\n")

	#prepare result for next step
	unprocessedZCIs = []

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialCtx = ZCI.ctx.copy()
		zCtx.ZCIDeepDebug(ZCI, "Treating ZCI " + ZCI.textFormat(), printSubCtxs=True)

		#read 1st ZCI word
		firstWord = zCtx.readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)



		#CASE 1 - BEGINNING WITH KEYWORD AND FORBIDDEN

		#bigrams
		if len(firstWord) == 2:
			if str_cmp("if", firstWord):
				zCtx.ZCIError(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")

		#trigrams
		elif len(firstWord) == 3:

			#1.1 - jumps
			if str_cmp("brk", firstWord):
				zCtx.ZCIError(ZCI, "BREAK jumps are not allowed in global scope (JMP_BRK detected).")
			if str_cmp("ctn", firstWord):
				zCtx.ZCIError(ZCI, "CONTINUE jumps are not allowed in global scope (JMP_CTN detected).")
			if str_cmp("ret", firstWord):
				zCtx.ZCIError(ZCI, "RETURN jumps are not allowed in global scope (JMP_RET detected).")

			#1.2 - statements
			if str_cmp("elf", firstWord) or str_cmp("els", firstWord):
				zCtx.ZCIError(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")
			if str_cmp("for", firstWord):
				zCtx.ZCIError(ZCI, "FOR statements are not allowed in global scope (STM_FOR detected).")
			if str_cmp("while", firstWord):
				zCtx.ZCIError(ZCI, "WHILE statements are not allowed in global scope (STM_WHI detected).")
			if str_cmp("swi", firstWord):
				zCtx.ZCIError(ZCI, "SWITCH statements are not allowed in global scope (STM_SWI detected).")

			#1.3 - remaining imports (should never occur)
			if str_cmp("imp", firstWord):
				zCtx.ZCIInternal(ZCI, "Must not have any importation remaining at that step.")



			#CASE 3 - BEGINNING WITH KEYWORD AND ALLOWED

			#trigrams requiring a following blank
			if ZCI.text[3] in BLANKS:

				#2.1 - library linking
				if str_cmp("lnk", firstWord):
					processLnk(zCtx, ZCI)
					continue

				#2.2 - type declaration DCL_TYP
				if str_cmp("typ", firstWord):
					processTypeDcl(zCtx, ZCI)
					continue

				#2.3 - Enumerate declaration DCL_ENM
				if ZCI.text.startswith("enm"):
					processEnmDcl(zCtx, ZCI, zCtx.cpl.globalScope)
					continue



		#CASE 3 - ASSIGNMENT OR FUNCTION

		#will be treated later => store it for now
		ZCI.resetCtx(initialCtx)
		unprocessedZCIs.append(ZCI)

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx.cplStep_debugZCIs("02")

	#return unprocessed ZCIs
	return unprocessedZCIs
