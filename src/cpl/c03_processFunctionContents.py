#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx                   import *
from cpl.c02_redirectGlobal import *






# -------- CONDITIONAL STATEMENTS --------

#if - elf - els
def processIfStm(ZCI):
	pass

def processElfStm(ZCI):
	pass

def processElsStm(ZCI):
	pass



#switch cases
def processSwiStm(ZCI):
	pass






# -------- LOOP STATEMENTS --------

#for
def processForStm(ZCI):
	pass



#while
def processWhiStm(ZCI):
	pass






# -------- JUMPS --------

#return keyword
def processRetJmp(ZCI):
	pass






# -------- EXECUTION --------

#compilation
def c03_processFunctionContents(zCtx):
	zCtx.debugSepLine()
	zCtx.debug("=================================================================================")
	zCtx.debug("=================== C03 PROCESS FUNCTION CONTENTS : beginning ===================")
	zCtx.debug("=================================================================================")
	zCtx.deepDebugPause()

	#for each function
	for f in zCtx.cpl.fcts:

		#skip LLI fcts
		if f.content is None:
			continue

		#process content
		for ZCI in f.content:
			initialCtx = ZCI.ctx.copy()
			ZCIDeepDebug(ZCI, "Treating local ZCI \"" + ZCI.textFormat() + '\"', printSubCtxs=True)

			#read 1st ZCI word
			firstWord = readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)



			#CASE 1 - BEGINNING WITH KEYWORD AND FORBIDDEN

			#bigrams
			if len(firstWord) == 2:
				if str_cmp("if", firstWord):
					processIfStm(ZCI)
					continue

			#trigrams
			elif len(firstWord) == 3:

				#1.1 - jumps
				if str_cmp("brk", firstWord):
					endOfZCI(ZCI, "break jump ZCI (JMP_BRK).")
					continue
				if str_cmp("ctn", firstWord):
					endOfZCI(ZCI, "break jump ZCI (JMP_BRK).")
					continue
				if str_cmp("ret", firstWord):
					processRetJmp(ZCI)
					continue

				#1.2 - statements
				if str_cmp("elf", firstWord):
					processElfStm(ZCI)
					continue
				if str_cmp("els", firstWord):
					processElsStm(ZCI)
					continue
				if str_cmp("for", firstWord):
					processForStm(ZCI)
					continue
				if str_cmp("while", firstWord):
					processWhiStm(ZCI)
					continue
				if str_cmp("swi", firstWord):
					processSwiStm(ZCI)
					continue

				#1.3 - remaining imports (should never occur)
				if str_cmp("imp", firstWord):
					ZCIInternal(ZCI, "Must not have any importation remaining at that step.")



				#CASE 3 - BEGINNING WITH KEYWORD AND ALLOWED

				#trigrams requiring a following blank
				if ZCI.txt[3] in BLANKS:

					#2.1 - library linking
					if str_cmp("lnk", firstWord):
						ZCIError(ZCI, "SDL linking ZCI are only allowed in global scope (EXT_LNK).")

					#2.2 - type declaration DCL_TYP
					if str_cmp("typ", firstWord):
						ZCIError(ZCI, "Type declaration ZCIs are only allowed in global scope (DCL_TYP).")

					#2.3 - Enumerate declaration DCL_ENM
					if str_cmp("enm", firstWord):
						processEnmDcl(ZCI, f.scope)
						continue

					#2.4 - Function declaration
					if str_cmp("fct", firstWord):
						ZCIError(ZCI, "Function declaration ZCI are only allowed in global scope (DCL_FCT).") #forward to function name directly

					#2.5 - Constant data item declaration
					if str_cmp("cst", firstWord):
						jumpBlankZone(ZCI, "Constant keyword in data item declaration ZCI (DCL_DAT).")
						processDclDat(ZCI, f.scope, False, True, forbidTypKeyword=False) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FOR THE MOMENT, EVERYBODY CAN FREELY USE "typ" KEYWORD IN FCT CONTENT
						continue



			#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

			#reset ZCI at initial state & try parsing it, no other possibility for a local ZCI
			ZCI.resetCtx(initialCtx)
			processRemainingZCI(ZCI, f.scope, forbidTypKeywordInDatDcl=False)

	#debug
	zCtx.debug("===========================================================================")
	zCtx.debug("=================== C03 PROCESS FUNCTION CONTENTS : end ===================")
	zCtx.debug("===========================================================================")
	zCtx.debugSepLine()
	zCtx.deepDebugPause()

	#debug output file
	zCtx__cplStep_debugZCIs(zCtx, "03")
