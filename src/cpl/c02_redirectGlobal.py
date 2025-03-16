#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#std
from std.string import *

#internal
#from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#
#def a():
#	pass






# -------- EXECUTION --------

#compilation
def c02_redirectGlobal(zCtx):

	#remaining ZCIs for further steps
	functionZCIs = []

	#analyse EVERY ZCI
	for ZCI in zCtx.ZCIs:
		initialLineNbr = ZCT.ctx.lineNbr
		initialColmNbr = ZCT.ctx.colmNbr
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

		#greater than 3
		else:

			#trigrams requiring a following blank
			if ZCIText[3] in BLANKS:
				ZCI.ctx.lineNbr        = initialLineNbr #reset ctx as if we were right after trigram
				ZCI.ctx.colmNbr        = initialColmNbr
				ZCI.ctx.icontent.index = 2



				#2.1 - library linking
				if ZCIText.startswith("lnk"):
					zCtx.jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

					#library linking path
					path = os.path.realpath( zCtx.readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS) )
					if not ZCI.reachedEnd():
						zCtx.ZCIError(ZCI, "Too much elements in library linking ZCI (EXT_LNK); should stop here.")

					#check existence
					if not os.path.isfile(path):
						zCtx.error("Shared & Dynamically Linked (SDL) library " + path + " not found.")

					#add link
					if path not in zCtx.cpl.dataResult.linkedLibs:
						zCtx.cpl.dataResult.linkedLibs.append(path)
					continue



				#2.2 - type declaration DCL_TYP
				if ZCIText.startswith("typ"):
					zCtx.jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

					#type name
					name = zCtx.readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", whitelist=)

					#must be followed by blanks once more
					if ZCI.get() not in BLANKS:
						zCtx.ZCIError("Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
					zCtx.jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

					#type content definition : structure
					#t = ztype()
					if ZCI.get() == '{':
						zCtx.debug("DETECTED STRUCTURE DCL HERE") #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO

					#type content definition : copy
					else:
						zCtx.debug("DETECTED TYPE COPY DCL HERE") #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO

					#if not ZCI.reachedEnd():
					#	zCtx.ZCIError(ZCI, "Too much elements in type declaration ZCI (DCL_TYP); should stop here.")

					#check existence
					#if not os.path.isfile(path):
					#	zCtx.error("Shared & Dynamically Linked (SDL) library " + path + " not found.")

					#add it
					#if path not in zCtx.cpl.dataResult.linkedLibs:
					#	zCtx.cpl.dataResult.linkedLibs.append(path)
					continue



				#2.3 - ENM






			#CASE 3 - BEGINNING WITH NAME

			#other possibilities
			else:
				print("Undefined yet.")

	#result
	return functionZCIs
