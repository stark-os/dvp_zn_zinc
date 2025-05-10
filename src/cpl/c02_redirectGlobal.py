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
	if not ZCI.reachedEnd():
		zCtx.ZCIError(ZCI, "Too much elements in library linking ZCI (EXT_LNK); should stop here.")

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
	for t in zCtx.cpl.ztypes:
		if fullName == t.name:
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
		zCtx.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

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
	newZType = ztyp(fullName, dcnDeg)
	zCtx.cpl.ztypes.append(newZType)
	zCtx.ZCIDebug(ZCI, "Explicitely added type " + newZType.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		zCtx.debug("Type declaration is via structure syntax.", printLine=False)
		newZType.size  = zCtx.SIZE__LNG
		newZType.isStc = True

		#reading fields
		newZType.fields = zCtx.readDataItemSequence(
			ZCI, "type declaration ZCI (DCL_TYP).",
			zCtx.cpl.globalScope,
			cstValuesOnly = True
		)
		if len(newZType.fields) == 0:
			zCtx.ZCIError(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDataItemSequence cannot return 0-length list)

		#update stcSize
		newZType.computeStcSize()

	#process type content: type-copy syntax
	else:
		zCtx.debug("Type declaration is via type-copy syntax.", printLine=False)
		parent = zCtx.readZType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		if parent == newZType:
			zCtx.ZCIError(ZCI, "Type cannot be declared as a copy of itself.") #seems obvious, but anyway
		newZType.size   = parent.size
		newZType.isStc  = parent.isStc
		newZType.parent = parent

	#end of ZCI expected
	zCtx.endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	zCtx.debug("Type declaration " + newZType.name + " processed.")
	zCtx.deepDebugPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(zCtx, ZCI, global_=False):
	zCtx.ZCIDebug(ZCI, "Processing enumerate declaration.", printSubCtxs=True)

'''
	zCtx.jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = zCtx.readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", doubleUnderscores=True)
'''


	zCtx.debug("Enumerate declaration processed.")
	zCtx.deepDebugPause()
	pass






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):
	zCtx.debug("\n\n\n\n")
	zCtx.debug("=================================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.debug("=================================================================================\n\n\n\n")

	#prepare result for next step
	fZCIs = [] #lst[zci]

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialZCICtx = ZCI.ctx.copy()
		zCtx.ZCIDeepDebug(ZCI, "Treating ZCI " + ZCI.textFormat(), printSubCtxs=True)

		#read 1st ZCI word
		firstWord = zCtx.readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_CHARSET)



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
					processEnmDcl(zCtx, ZCI, global_=True)
					continue



		#CASE 3 - ASSIGNMENT OR FUNCTION

		#assignment ASG_ASG /!\ DO NOT USE readType() HERE, THERE MIGHT BE UNSOLVED TYPES THAT MUST NOT BE  /!\
		# #not treated yet => to be stored into zCtx

		#function DCL_FCT
		# #not treated yet => to be stored into zCtx

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("===========================================================================")
	zCtx.debug("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.debug("===========================================================================\n\n\n\n")

	#debug output file
	zCtx.cplStep_debugZCIs("02")

	#return function declaration ZCIs
	return fZCIs
