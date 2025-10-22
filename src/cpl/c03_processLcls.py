#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *
from cpl.c02_redirectGbl import *






# -------- CONDITIONAL STATEMENTS --------

#if - elf - els
def processIfStm(ZCI, tgtFct, scope):
	ZCIDbg(ZCI, "Processing IF STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#read condition
	res = stm_if()
	v   = readVal(ZCI, "condition in IF statement (STM_IF_).", scope)
	res.conds.append(v)
	ZCIDeepDbg(ZCI, "Added IF statement condition: " + v.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in IF statement in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDeepDbg(ZCI, "Extracting IF statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction of IF statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	subScp = newScp(parent=scope)
	readLclScp(scpZCIs, tgtFct, subScp)
	res.scopes.append(subScp)

	#add statement
	scope.exes.append(res)

	#end of ZCI expected
	endOfZCI(ZCI, "if statement in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg(ZCI, "Processed IF STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()

def processElfStm(ZCI, scope, tgtFct):
	pass

def processElsStm(ZCI, scope, tgtFct):
	pass



#switch cases
def processSwiStm(ZCI, scope, tgtFct):
	pass






# -------- LOOP STATEMENTS --------

#for
def processForStm(ZCI, scope, tgtFct):
	pass



#while
def processWhiStm(ZCI, scope, tgtFct):
	pass






# -------- JUMPS --------

#return keyword
def processRetJmp(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing RET JMP in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#try read ret val if given
	retVal = None
	if not ZCI.reachedEnd():
		retVal = readVal(ZCI, "Return value in function " + tgtFct.name + " (JMP_RET).", scope)

	#retVal must match with fct ret requirements (void/!void)
	if f.retType == TYPE_ID__UNKNOWN:
		if retVal is not None:
			ZCIErr(ZCI, "Must return nothing (void function " + tgtFct.name + " targetted, JMP_RET).")
	else:
		if retVal is None:
			ZCIErr(ZCI, "Must return a value (!void function " + tgtFct.name+ " targetted, JMP_RET).")

	#add jmp
	scope.exes.append( atm(ATM__JMP, jmp(JMP__RET, retVal)) )

	#end of ZCI expected
	endOfZCI(ZCI, "return jump in function " + tgtFct.name + " (JMP_RET).")
	retValTxt = "<void>"
	if retVal is not None:
		retValTxt = retVal.toStr()
	ZCIDbg(ZCI, "Processed RET JMP in function " + tgtFct.name + " with given value " + retValTxt)
	ZCI.deepDbgPause()






# -------- EXECUTION --------

#read given ZCIs => add them to given scope
def readLclScope(ZCIs, scope, tgtFct): #tgtFct is for debug
	for ZCI in ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDeepDbg(ZCI, "Treating local ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=True)

		#read 1st ZCI word
		firstWord = readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)[1]



		#CASE 1 - BEGINNING WITH KEYWORD AND FORBIDDEN

		#bigrams
		if len(firstWord) == 2:
			if str_cmp("if", firstWord):
				processIfStm(ZCI, scope, tgtFct)
				continue

		#trigrams
		elif len(firstWord) == 3:

			#1.1 - jumps
			if str_cmp("brk", firstWord):
				scope.exes.append( jmp(JMP__BRK) )
				endOfZCI(ZCI, "break jump ZCI (JMP_BRK).")
				continue
			if str_cmp("ctn", firstWord):
				scope.exes.append( jmp(JMP__CTN) )
				endOfZCI(ZCI, "break jump ZCI (JMP_BRK).")
				continue
			if str_cmp("ret", firstWord):
				processRetJmp(ZCI, scope, tgtFct)
				continue

			#1.2 - statements
			if str_cmp("elf", firstWord):
				processElfStm(ZCI, scope, tgtFct)
				continue
			if str_cmp("els", firstWord):
				processElsStm(ZCI, scope, tgtFct)
				continue
			if str_cmp("for", firstWord):
				processForStm(ZCI, scope, tgtFct)
				continue
			if str_cmp("while", firstWord):
				processWhiStm(ZCI, scope, tgtFct)
				continue
			if str_cmp("swi", firstWord):
				processSwiStm(ZCI, scope, tgtFct)
				continue

			#1.3 - remaining imports (should never occur)
			if str_cmp("imp", firstWord):
				ZCIInt(ZCI, "Must not have any importation remaining at that step.")



			#CASE 3 - BEGINNING WITH KEYWORD AND ALLOWED

			#trigrams requiring a following blank
			if ZCI.txt[3] in BLANKS:

				#2.1 - library linking
				if str_cmp("lnk", firstWord):
					ZCIErr(ZCI, "SDL linking ZCI are only allowed in global scope (EXT_LNK).")

				#2.2 - type declaration DCL_TYP
				if str_cmp("typ", firstWord):
					ZCIErr(ZCI, "Type declaration ZCIs are only allowed in global scope (DCL_TYP).")

				#2.3 - Enumerate declaration DCL_ENM
				if str_cmp("enm", firstWord):
					processEnmDcl(ZCI, scope, tgtFct)
					continue

				#2.4 - Function declaration
				if str_cmp("fct", firstWord):
					ZCIErr(ZCI, "Function declaration ZCI are only allowed in global scope (DCL_FCT).")

				#2.5 - Function forwarding
				if str_cmp("fwd", firstWord):
					ZCIErr(ZCI, "Function forwarding ZCI are only allowed in global scope (DCL_FWD).")

				#2.6 - Constant data item declaration
				if str_cmp("cst", firstWord):
					jumpBlankZone(ZCI, "Constant keyword in data item declaration ZCI (DCL_DAT).")
					processDclDat(ZCI, scope, tgtFct, True)
					continue



		#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

		#reset ZCI at initial state & try parsing it, no other possibility for a local ZCI
		ZCI.resetCtx(initialCtx)
		processRemainingZCI(ZCI, scope, tgtFct)



#compilation
def c03_processLcls(zCtx):
	zCtx.step = STEP.C03
	zCtx.dbgSepLine()
	zCtx.dbg("=================================================================================")
	zCtx.dbg("========================== C03 PROCESS LCLs : beginning =========================")
	zCtx.dbg("=================================================================================")
	zCtx.deepDbgPause()

	#get main fct if existing
	mainFct = zCtx__getFctFromName(zCtx, "GFmain")

	#case 1: executable program => focus on main only
	if zCtx.cpl.mode == CPL__MODE_EXE:
		if mainFct is None:
			zCtx.err("Missing \"main\" function to compile as executable.", prtSubCtxs=False, prtLine=False)

		#process fct scope & remove its content ZCIs
		readLclScope(mainFct.content, mainFct.scope, mainFct)
		mainFct.content = None

	#case 2: SDL
	elif zCtx.cpl.mode == CPL__MODE_SDL:
		for f in zCtx.cpl.fcts:

			#target only public fct and skip LLI or already processed fcts
			if not f.isPub or f.content is None:
				continue

			#can only process dcn-independant fcts
			if f.dcnDep:
				zCtx.dbg("Method \"" + f.name + "\" is public but also dcn-dependant => not processing it directly.")
				continue

			#process fct scope & remove its content ZCIs
			readLclScope(f.content, f.scope, f)
			f.content = None

	#unknown cpl mode
	else:
		zCtx.int("Unknown compilation mode with id " + str(zCtx.cpl.mode), prtSubCtxs=False, prtLine=False)

	#debug
	zCtx.dbg("===========================================================================")
	zCtx.dbg("========================== C03 PROCESS LCLs : end =========================")
	zCtx.dbg("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.deepDbgPause()

	#debug output file
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		#writeFIle("dbg/" + ..., ...)
