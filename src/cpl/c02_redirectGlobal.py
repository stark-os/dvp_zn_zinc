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
	zCtx.jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

	#library linking path
	path = os.path.realpath( zCtx.readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS_EXTENDED) )
	if not ZCI.reachedEnd():
		zCtx.ZCIError(ZCI, "Too much elements in library linking ZCI (EXT_LNK); should stop here.")

	#check existence
	if not os.path.isfile(path):
		zCtx.ZCIError(ZCI, "Shared & Dynamically Linked (SDL) library " + path + " not found.")

	#add link
	if path not in zCtx.cpl.dataResult.linkedLibs:
		zCtx.cpl.dataResult.linkedLibs.append(path)






# -------- DCL_TYP --------

#structure
def processTypeDcl(zCtx, ZCI):
	zCtx.jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = zCtx.readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).")
	if len(ZCI.modulePrefix) == 0:
		fullName = "GU" + rawName.replace('_', "__")
	else:
		fullName = ZCI.modulePrefix + 'U' + rawName.replace('_', "__")

	#check already existing
	for t in zCtx.cpl.ztypes:
		if fullName == t.name:
			modulePrefixText = ""
			if len(ZCI.modulePrefix) != 0:
				modulePrefixText = unprefixizeModule(ZCI.modulePrefix)
			zCtx.ZCIError(ZCI, "Type " + modulePrefixText + rawName + " already exists, can't declare a new one with the same name (DCL_TYP).")

	#explicit declination degree if any
	dcnDeg = 0
	if ZCI.get() == '[':
		dcnDegTextCtx, dcnDegText = zCtx.getIncluderStrippedContent(ZCI, "type declination degree block.")

		#non-integer dcnDeg
		if not str_isConvertible_int(dcnDegText):
			ZCI.updateCtx(dcnDegTextCtx)
			zCtx.ZCIError(ZCI, "Invalid explicit declination degree given (must be an integer).")

		#negative dcnDeg
		dcnDeg = int(dcnDegText)
		if dcnDeg < 0:
			ZCI.updateCtx(dcnDegTextCtx)
			zCtx.ZCIError(ZCI, "Invalid explicit declination degree given (must be positive).")

	#must be followed by blanks once more
	if ZCI.get() not in BLANKS:
		zCtx.ZCIError(ZCI, "Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
	zCtx.jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

	#process type content
	if ZCI.get() == '{':
		newZType = ztyp(
			fullName, dcnDeg,
			zCtx.SIZE__LNG,
			True,
			fields = zCtx.readKeyValueFields(ZCI)
		)
	else:
		parent   = zCtx.readZType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		newZType = ztyp(
			fullName, dcnDeg,
			parent.size,
			parent.isStc,
			parent = parent
		)

	#add new type
	zCtx.cpl.ztypes.append(newZType)
	print("EXPLICITELY ADDING TYPE [" + newZType.name + "] with dcnDeg [" + str(newZType.dcnDeg) + "]")

	#end of ZCI expected
	zCtx.endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(zCtx, ZCI, global_=False):
	pass






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):

	#remaining ZCIs for further steps
	functionZCIs = []

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialLineNbr = ZCI.ctx.lineNbr
		initialColmNbr = ZCI.ctx.colmNbr
		ZCIText        = ZCI.ctx.icontent.s

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



		#CASE 2 - BEGINNING WITH KEYWORD AND ALLOWED

		#trigrams requiring a following blank
		if ZCIText[3] in BLANKS:
			ZCI.ctx.lineNbr        = initialLineNbr #reset ctx as if we were right after trigram
			ZCI.ctx.colmNbr        = initialColmNbr + 2
			ZCI.ctx.icontent.index = 2

			#2.1 - library linking
			if ZCIText.startswith("lnk"):
				processLnk(zCtx, ZCI)
				continue

			#2.2 - type declaration DCL_TYP
			if ZCIText.startswith("typ"):
				processTypeDcl(zCtx, ZCI)
				continue

			#2.3 - ENM
			if ZCIText.startswith("enm"):
				processEnmDcl(zCtx, ZCI, global_=True)
				continue



		#CASE 3 - BEGINNING WITH NAME

		#other possibilities
		#print("Undefined yet.")

	#debug output file
	zCtx.cplStep_debugZCIs("02")

	#result
	return functionZCIs
