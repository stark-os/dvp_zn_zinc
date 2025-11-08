#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *
from cpl.c02_redirectGbl import *






# -------- CONDITIONAL STATEMENTS --------

#if - elf - els
def processIfStm(ZCI, scope, tgtFct):
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
		ZCIErr(ZCI, "Expected braces includer after condition in IF statement, in function " + tgtFct.name + " (STM_IF_).")

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
	scope.exes.append( atm(ATM__IF_, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "if statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg(ZCI, "Processed IF STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()

def processElfStm(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing ELF STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#must follow if/elf statement
	lastExe   = None
	lastExeID = -1
	if len(scope.exes) != 0:
		lastExe   = lst_last(scope.exes)
		lastExeID = lastExe.id
	if lastExeID != ATM__IF_:
		ZCIErr(ZCI, "Found lonely \"elf\" keyword, it must be following an IF/ELF statement, in function" + tgtFct.name + " (STM_IF_).")

	#els keyword already detected
	if len(lastExe.dat.scopes) > len(lastExe.dat.conds):
		ZCIErr(ZCI, "Found \"elf\" keyword after \"els\", makes no sens in IF/ELF/ELS statement, in function" + tgtFct.name + " (STM_IF_).")

	#read condition
	v   = readVal(ZCI, "condition in ELF statement (STM_IF_).", scope)
	lastExe.dat.conds.append(v)
	ZCIDeepDbg(ZCI, "Added ELF statement condition: " + v.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in ELF statement, in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDeepDbg(ZCI, "Extracting ELF statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction of ELF statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	subScp = newScp(parent=scope)
	readLclScp(scpZCIs, tgtFct, subScp)
	lastExe.dat.scopes.append(subScp)

	#end of ZCI expected
	endOfZCI(ZCI, "elf statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg(ZCI, "Processed ELF STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()

def processElsStm(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing ELS STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#must follow if/elf statement
	lastExe   = None
	lastExeID = -1
	if len(scope.exes) != 0:
		lastExe   = lst_last(scope.exes)
		lastExeID = lastExe.id
	if lastExeID != ATM__IF_:
		ZCIErr(ZCI, "Found lonely \"els\" keyword, it must be following an IF/ELF statement, in function" + tgtFct.name + " (STM_IF_).")

	#els keyword already detected
	if len(lastExe.dat.scopes) > len(lastExe.dat.conds):
		ZCIErr(ZCI, "Found \"els\" keyword after another \"els\", makes no sens in IF/ELF/ELS statement, in function" + tgtFct.name + " (STM_IF_).")

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after keyword in ELS statement, in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDeepDbg(ZCI, "Extracting ELS statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction of ELS statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	subScp = newScp(parent=scope)
	readLclScp(scpZCIs, tgtFct, subScp)
	lastExe.dat.scopes.append(subScp)

	#end of ZCI expected
	endOfZCI(ZCI, "els statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg(ZCI, "Processed ELS STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()



#switch cases
def processSwiStm(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing SWI STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#read tgt
	res     = stm_swi()
	res.tgt = readVal(ZCI, "target in SWI statement (STM_SWI).", scope)
	ZCIDeepDbg(ZCI, "Added switch statement target: " + res.tgt.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after target in switch statement, in function " + tgtFct.name + " (STM_SWI).")

	#read cases until end of includer
	peerIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	ZCI.inc()
	while True:
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

		#end of switch
		if ZCI.ctx.icontent.idx == peerIdx:
			ZCI.inc()
			break

		#read case value
		v = readVal(ZCI, "case value in SWI statement (STM_SWI).", scope)
		ZCIDeepDbg(ZCI, "Added switch statement case value: " + v.toStr())
		res.cases.append(v)

		#extract ZCIs from it
		ZCIDeepDbg(ZCI, "Extracting SWI statement case sub-scope.")
		subScpZCIs = extractZCIsFromCtx(
			ZCI.zCtx,
			ZCI.ctx, subCtxs=ZCI.subCtxs,
			gbl     = False,
			modPfx  = ZCI.modPfx,
			wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		)
		ZCIDeepDbg(ZCI, "End of extraction of SWI statement case sub-scope.")

		#parse them as inner sub-scp (lcl)
		subScp = newScp(parent=scope)
		readLclScp(scpZCIs, tgtFct, subScp)
		res.scopes.append(subScp)

	#add statement
	scope.exes.append( atm(ATM__SWI, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "swi statement, in function " + tgtFct.name + " (STM_SWI).")
	ZCIDbg(ZCI, "Processed SWI STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()






# -------- LOOP STATEMENTS --------

#for
def processForStm(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing FOR STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)



	#STEP 1: ITER DATITM NAME + KIND DETECTION

	#read iter datItm name
	res     = stm_for()
	iDIName = readName(ZCI, "iteration data item name in FOR statement, in function " + tgtFct.name + " (STM_FOR).", dblUnderscores=True)

	#blank required (avoid confusion)
	if ZCI.get() not in BLANKS:
		ZCIErr(ZCI, "Blank required after iteration data item name in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
	jumpBlankZone(ZCI, None)

	#4 different behaviors
	KIND__ON    = 0
	KIND__IN    = 1
	KIND__OVR   = 2
	KIND__RANGE = 3

	#detect tgt kind
	tmpCopy = ZCI.copy()
	kw      = readName(tmpCopy, None)
	kind    = 0
	if kw == "on":
		kind = KIND__ON
	elif kw == "in":
		kind = KIND__IN
	elif kw == "ovr":
		kind = KIND__OVR
	else:
		kind = KIND__RANGE

	#forward after kw
	if kind != KIND__RANGE:
		ZCI.forwardAlike(tmpCopy)

		#another blank required
		if ZCI.get() not in BLANKS:
			ZCIErr(ZCI, "Blank required after \"" + kw + "\" keyword in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		jumpBlankZone(ZCI, None)



	#STEP 2: ITER LIMIT

	#iter limit
	iLimit      = readVal(ZCI, "value in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
	iDIType     = iLimit.Type
	iDITypeInst = ZCI.getTypeInstanceFromID(iDIType)
	stcType     = iDIType     #only for "in/ovr"
	stcTypeInst = iDITypeInst #only for "in/ovr"

	#extend to ".len"
	if kind in (KIND__IN, KIND__OVR):
		if stcTypeInst.dcnCommon.nature != NATURE__STC:
			ZCIErr(ZCI, "Value given in FOR statement must have structure type, in function " + tgtFct.name + " (STM_FOR).")

		#must have a "len" field
		missingField = True
		for di in iDITypeInst.dcnCommon.fields:
			if di.name == "len":
				iDIType     = di.Type
				iDITypeInst = ZCI.getTypeInstanceFromID(iDIType)
				iLimit      = val(
					iDIType,
					atm(ATM__CALL, call(
						"fa",
						[
							val(ZCI.zCtx.rootTypes[RT__U32], atm(ATM__U32,    stcType), True ),
							val(ZCI.zCtx.rootTypes[RT__REF], atm(ATM__STR,    "len"  ), True ),
							val(stcType,                     atm(ATM__DATITM, iLimit ), False)
						],
						iDIType
					)),
					False
				)
				missingField = False
				break
		if missingField:
			ZCIErr(ZCI, "Value given as limit has no \"len\" field in FOR statement, in function " + tgtFct.name + " (STM_FOR).")

	#limit must be prm
	if iDITypeInst.dcnCommon.nature != NATURE__PRM:
		ZCIErr(ZCI, "Value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")



	#STEP 3: ITER STEP & ITER INIT

	#iter step
	iStep = val(iDIType, ZCI.zCtx.maxPrmOne, True)

	#iter init: range => read a second value
	iInit = None
	if kind == KIND__RANGE:
		iInit = iLimit

		#expected to have colon separator
		if ZCI.get() != ':':
			ZCIErr(ZCI, "Expected a colon ':' separator after first range value in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		ZCI.inc()

		#limit given as 2nd value
		iLimit = readVal(ZCI, "range limit value in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
		if iLimit.Type != iInit.Type:
			ZCIWrn(ZCI, "Limit value doesn't have the same type as the initial one in range FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		if ZCI.getTypeInstanceFromID(iLimit.Type).dcnCommon.nature != NATURE__PRM:
			ZCIErr(ZCI, "Range limit value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")

		#optional 3rd have colon separator
		if ZCI.get() != ':':
			ZCI.inc()

			#step given as 3rd value
			iStep = readVal(ZCI, "range step value in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
			if ZCI.getTypeInstanceFromID(iStep).dcnCommon.nature != NATURE__PRM:
				ZCIErr(ZCI, "Step value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")

	#itm init val: on/in/ovr => zero
	else:
		iInit = ZCI.zCtx.maxPrmZero



	#STEP 4: BUILD ITER COND & EXE

	#complete iter datItm info
	ovrUsrIterDI = None #iter datItm that the USER mentionned, that will not be the actual iter datItm of the FOR (ovr only)
	if kind == OVR:
		ovrUsrIterDI   = datItm(TYPE_ID__UNKNOWN, iDIName, False, None) #set unknown ID temporarily (we get that info in further steps)
		res.iterDatItm = datItm(iDIType, "D0", True, iInit) #manually gen 1st dcp var of FOR scope
	else:
		res.iterDatItm = datItm(iDIType, iDIName, True, iInit)

	#use iter datItm as val for calls
	iDIVal = val(iDIType, atm(ATM__DATITM, res.iterDatItm), False)
	ZCIDeepDbg(ZCI, "Added for statement iter datItm: " + res.iterDatItm.toStr())

	#iter condition
	ope = ZCI.zCtx.zCtx__findMatchingOperator(
		"clt",
		[iDIType,          iDIType         ],
		[iDITypeInst.name, iDITypeInst.name]
	)
	if ope is None:
		ZCIErr(ZCI, "Can't find a valid operator CLT to match between 2 types \"" + unpfxTypeName(ZCI.zCtx, iDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
	res.iterCond = atm(ATM__CALL, call(
		ope.name,
		[iDIVal, iLimit],
		ope.retType
	))
	ZCIDeepDbg(ZCI, "Added for statement iter cond: " + res.iterCond.toStr())

	#iter exe
	ope = ZCI.zCtx.zCtx__findMatchingOperator(
		"bad",
		[iDIType,          iDIType         ],
		[iDITypeInst.name, iDITypeInst.name]
	)
	if ope is None:
		ZCIErr(ZCI, "Can't find a valid operator BAD to match between 2 types \"" + unpfxTypeName(ZCI.zCtx, iDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
	res.iterExe = atm(ATM__ASG, asg(
		res.iterDatItm,
		val(
			iDIType,
			atm(ATM__CALL, call(
				ope.name,
				[iDIVal, iStep],
				ope.retType
			)),
			False
		)
	))
	ZCIDeepDbg(ZCI, "Added for statement iter exe: " + res.iterExe.toStr())



	#STEP 5: INNER SCOPE & OVR 1ST EXE

	#create inner sub-scope (lcl)
	subScp = newScp(parent=scope)

	#ovr: generated ZCI to be run as 1st exe in scope
	if kind == KIND__OVR:
		ope = ZCI.zCtx.zCtx__findMatchingOperator(
			"iin",
			[stcType,          iDIType         ],
			[stcTypeInst.name, iDITypeInst.name]
		)
		if ope is None:
			ZCIErr(ZCI, "Can't find a valid operator IIN to match between types \"" + unpfxTypeName(ZCI.zCtx, stcTypeInst.name)[0] + "\" and \"" + unpfxTypeName(ZCI.zCtx, iDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR).")

		#update usr iter datItm type
		ovrUsrIterDI.Type = ope.retType

		#don't forget to update dcpIdx of inner scp also, ovrUsrIterDI used the 1st one
		subScp.dcpIdx = 1

		#gen idxing exe
		ovrUsrIterDIVal = val(ovrUsrIterDI.Type, atm(ATM__DATITM, ovrUsrIterDI), False)
		ovr1stExe       = atm(ATM__ASG, asg(
			ovrUsrIterDI,
			val(
				ope.retType,
				atm(ATM__CALL, call(
					ope.name,
					[ovrUsrIterDIVal, iDIVal],
					ope.retType
				)),
				False
			)
		))

		#add it as 1st exe
		subScp.datItms.append(ovrUsrIterDI)
		subScp.exes.append(ovr1stExe)
		ZCIDeepDbg(ZCI, "Added for statement iter exe: " + res.iterExe.toStr())



	#STEP 6: INSIDE INNER SCOPE + END

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in for statement, in function " + tgtFct.name + " (STM_FOR).")

	#extract ZCIs from it
	ZCIDeepDbg(ZCI, "Extracting FOR statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction of FOR statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	readLclScp(scpZCIs, tgtFct, subScp)
	res.scope = subScp

	#add statement to lcl scp
	scope.exes.append( atm(ATM__FOR, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "for statement, in function " + tgtFct.name + " (STM_FOR).")
	ZCIDbg(ZCI, "Processed FOR STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()



#while
def processWhiStm(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing WHI STM in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#read condition
	res      = stm_whi()
	res.cond = readVal(ZCI, "condition in WHI statement (STM_WHI).", scope)
	ZCIDeepDbg(ZCI, "Added while statement condition: " + res.cond.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in while statement, in function " + tgtFct.name + " (STM_WHI).")

	#extract ZCIs from it
	ZCIDeepDbg(ZCI, "Extracting WHI statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction of WHI statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	subScp = newScp(parent=scope)
	readLclScp(scpZCIs, tgtFct, subScp)
	res.scope = subScp

	#add statement
	scope.exes.append( atm(ATM__WHI, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "whi statement, in function " + tgtFct.name + " (STM_WHI).")
	ZCIDbg(ZCI, "Processed WHI STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.deepDbgPause()






# -------- JUMPS --------

#return keyword
def processRetJmp(ZCI, scope, tgtFct):
	ZCIDbg(ZCI, "Processing RET JMP in function " + tgtFct.name, prtLine=False)
	jumpBlankZone(ZCI, None)

	#try read ret val if given
	retVal = None
	if not ZCI.reachedEnd():
		retVal = readVal(ZCI, "return value in function " + tgtFct.name + " (JMP_RET).", scope)

	#retVal must match with fct ret requirements (void/!void)
	if tgtFct.retType == TYPE_ID__UNKNOWN:
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
