#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *
from cpl.c02_redirectGbl import *






# -------- CONDITIONAL STATEMENTS --------

#if - elf - els
def processIfStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing IF STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#read condition
	res      = stm_if()
	res.cond = readVal(ZCI, "condition in IF statement (STM_IF_).", scope)
	ZCIDbg1(ZCI, "Added IF statement condition: " + res.cond.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in IF statement, in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDbg1(ZCI, "Extracting IF statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction of IF statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	res.ifScope = newScp(parent=scope)
	readLclScp(subScpZCIs, res.ifScope, tgtFct)

	#add statement
	scope.exes.append( atm(ATM__STM_IF, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "IF statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg0(ZCI, "Processed IF STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.dbgPause()

def processElfStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing ELF STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#must follow if/elf statement
	lastExe   = None
	lastExeID = -1
	if len(scope.exes) != 0:
		lastExe   = lst_last(scope.exes)
		lastExeID = lastExe.id
	if lastExeID != ATM__STM_IF:
		ZCIErr(ZCI, "Found lonely \"elf\" keyword, it must be following an IF/ELF statement, in function" + tgtFct.name + " (STM_IF_).")

	#find the deepest elf processed before
	deepestPrevIf      = lastExe.dat
	deepestPrevIfScope = scope
	while True:

		#no els processed at all => can add elf
		if deepestPrevIf.elsScope is None:
			break

		#followed by an elf => let's see deeper
		if len(deepestPrevIf.elScope.exes) == 1 and deepestPrevIf.elsScope.exes[0].id == ATM__STM_IF: #each elf processing results into 1 exe in elsScope => more or less means "els" has been processed instead
			deepestPrevIf      = deepestPrevIf.elsScope.exes[0].dat
			deepestPrevIfScope = deepestPrevIf.elsScope

		#els keyword already detected
		else:
			ZCIErr(ZCI, "Found \"elf\" keyword after \"els\", makes no sens in IF/ELF/ELS statement, in function" + tgtFct.name + " (STM_IF_).")

	#read condition
	i      = stm_if()
	i.cond = readVal(ZCI, "condition in ELF statement (STM_IF_).", deepestPrevIfScope)
	ZCIDbg1(ZCI, "Added ELF statement condition: " + i.cond.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in ELF statement, in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDbg1(ZCI, "Extracting ELF statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction of ELF statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	i.ifScope = newScp(parent=deepestPrevIfScope)
	readLclScp(subScpZCIs, i.ifScope, tgtFct)

	#add elf as regular IF, inside the deepestPrevIf elsScope
	deepestPrevIf.elsScope = newScp(parent=deepestPrevIfScope)
	deepestPrevIf.elsScope.exes.append(i)

	#end of ZCI expected
	endOfZCI(ZCI, "ELF statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg0(ZCI, "Processed ELF STM in function " + tgtFct.name + ": " + i.toStr())
	ZCI.dbgPause()

def processElsStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing ELS STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#must follow if/elf statement
	lastExe   = None
	lastExeID = -1
	if len(scope.exes) != 0:
		lastExe   = lst_last(scope.exes)
		lastExeID = lastExe.id
	if lastExeID != ATM__STM_IF:
		ZCIErr(ZCI, "Found lonely \"els\" keyword, it must be following an IF/ELF statement, in function" + tgtFct.name + " (STM_IF_).")

	#find the deepest elf processed before
	deepestPrevIf      = lastExe.dat
	deepestPrevIfScope = scope
	while True:

		#no els processed at all => can add one
		if deepestPrevIf.elsScope is None:
			break

		#followed by an elf => let's see deeper
		if len(deepestPrevIf.elScope.exes) == 1 and deepestPrevIf.elsScope.exes[0].id == ATM__STM_IF: #each elf processing results into 1 exe in elsScope => more or less means "els" has been processed instead
			deepestPrevIf      = deepestPrevIf.elsScope.exes[0].dat
			deepestPrevIfScope = deepestPrevIf.elsScope

		#els keyword already detected
		else:
			ZCIErr(ZCI, "Found \"els\" keyword after another \"els\", makes no sens in IF/ELF/ELS statement, in function" + tgtFct.name + " (STM_IF_).")

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after keyword in ELS statement, in function " + tgtFct.name + " (STM_IF_).")

	#extract ZCIs from it
	ZCIDbg1(ZCI, "Extracting ELS statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction of ELS statement sub-scope.")

	#parse them directly in the deepest els scope (lcl)
	deepestPrevIf.elsScope = newScp(parent=deepestPrevIfScope)
	readLclScp(subScpZCIs, deepestPrevIf.elsScope, tgtFct)

	#end of ZCI expected
	endOfZCI(ZCI, "ELS statement, in function " + tgtFct.name + " (STM_IF_).")
	ZCIDbg0(ZCI, "Processed ELS STM in function " + tgtFct.name + ": " + deepestPrevIf.elsScope.toStr())
	ZCI.dbgPause()



#switch cases
def processSwiStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing SWI STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#read tgt
	res     = stm_swi()
	res.tgt = readVal(ZCI, "target in SWI statement (STM_SWI).", scope)
	ZCIDbg1(ZCI, "Added switch statement target: " + res.tgt.toStr())

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
		ZCIDbg1(ZCI, "Added switch statement case value: " + v.toStr())
		res.cases.append(v)

		#extract ZCIs from it
		ZCIDbg1(ZCI, "Extracting SWI statement case sub-scope.")
		subScpZCIs = extractZCIsFromCtx(
			ZCI.zCtx,
			ZCI.ctx, subCtxs=ZCI.subCtxs,
			gbl     = False,
			modPfx  = ZCI.modPfx,
			wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		)
		ZCIDbg1(ZCI, "End of extraction of SWI statement case sub-scope.")

		#parse them as inner sub-scp (lcl)
		subScp = newScp(parent=scope)
		readLclScp(subScpZCIs, subScp, tgtFct)
		res.scopes.append(subScp)

	#add statement
	scope.exes.append( atm(ATM__STM_SWI, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "SWI statement, in function " + tgtFct.name + " (STM_SWI).")
	ZCIDbg0(ZCI, "Processed SWI STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.dbgPause()






# -------- LOOP STATEMENTS --------

#for
def processForStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing FOR STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#will be stored as WHI
	res = stm_whi()



	#STEP 1: ITER DATITM NAME + KIND DETECTION

	#read iter datItm name
	iterDIName = 'L' + readName(ZCI, "iteration data item name in FOR statement, in function " + tgtFct.name + " (STM_FOR).", dblUnderscores=True)[1]

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
	kw      = readName(tmpCopy, None)[1]
	kind    = 0
	if kw == "on":
		kind = KIND__ON
		ZCIDbg1(tmpCopy, "For statement of \"ON\" kind.")
	elif kw == "in":
		kind = KIND__IN
		ZCIDbg1(tmpCopy, "For statement of \"IN\" kind.")
	elif kw == "ovr":
		kind = KIND__OVR
		ZCIDbg1(tmpCopy, "For statement of \"OVR\" kind.")
	else:
		kind = KIND__RANGE
		ZCIDbg1(tmpCopy, "For statement of \"RANGE\" kind.")

	#forward after kw
	if kind != KIND__RANGE:
		ZCI.forwardAlike(tmpCopy)

		#another blank required
		if ZCI.get() not in BLANKS:
			ZCIErr(ZCI, "Blank required after \"" + kw + "\" keyword in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		jumpBlankZone(ZCI, None)



	#STEP 2: ITER INIT, ITER LIMIT, ITER STEP

	#read first val given
	v1         = readVal(ZCI, "value given in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
	v1TypeInst = ZCI.getTypeInstanceFromID(v1.Type)

	#init & limit to be determined specifically
	iterInit  = None #val
	iterLimit = None #val
	iterStep  = val(TYPE_ID__UNKNOWN, atm(ATM__S32, 1), True) #step defaulted to 1 (type to be defined later)

	#these 3 will help to determine iterDI type
	iterDIType = None

	#case 1: ON
	if kind == KIND__ON:
		iterInit  = ZCI.zCtx.smaxZero #start at 0
		iterLimit = v1                #v1 given is our limit to reach

		#it also determines the type of our iterDI
		iterDIType    = v1.Type

	#case 2: RANGE
	elif kind == KIND__RANGE:
		iterInit = v1 #v1 in our init

		#it also determines the type of our iterDI
		iterDIType    = v1.Type

		#expecting a colon separator
		if ZCI.get() != ':':
			ZCIErr(ZCI, "Expected a colon ':' separator after first range value in FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		ZCI.inc()

		#limit given as 2nd value
		iterLimit = readVal(ZCI, "range limit value in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
		if iterLimit.Type != iterInit.Type:
			ZCIWrn(ZCI, "Limit value doesn't have the same type as the initial one in range FOR statement, in function " + tgtFct.name + " (STM_FOR).")
		if ZCI.getTypeInstanceFromID(iterLimit.Type).dcnCommon.nature != NATURE__PRM:
			ZCIErr(ZCI, "Range limit value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")

		#optional 3rd have colon separator
		if ZCI.get() != ':':
			ZCI.inc()

			#step given as 3rd value (overwrite)
			iterStep = readVal(ZCI, "range step value in FOR statement, in function " + tgtFct.name + " (STM_FOR).", scope)
			if ZCI.getTypeInstanceFromID(iterStep).dcnCommon.nature != NATURE__PRM:
				ZCIErr(ZCI, "Step value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")

	#case 3: IN/OVR => extend to ".len"
	else:
		iterInit = ZCI.zCtx.smaxZero #start at 0

		#val given must be a stc
		if v1TypeInst.dcnCommon.nature != NATURE__STC:
			ZCIErr(ZCI, "Value given in FOR statement must have structure type, in function " + tgtFct.name + " (STM_FOR).")

		#get field "len" from it
		offset     = 0
		iterDIType = TYPE_ID__UNKNOWN
		for di in v1TypeInst.dcnCommon.fields:
			if di.name == "len":
				iterDIType = di.Type
				break
			offset += ZCI.zCtx.getTypeInstanceFromID(di.Type).dcnCommon.size

		#no "len" field found
		if iterDIType == TYPE_ID__UNKNOWN:
			ZCIErr(ZCI, "Value given as limit has no \"len\" field in FOR statement, in function " + tgtFct.name + " (STM_FOR).")

		#use appropriate "ffa" call, keep the info that this "ffa_get_<fieldTypeID>" must be generated later
		if iterDIType not in ZCI.zCtx.cpl.ffa_fieldTypeIDs:
			ZCI.zCtx.cpl.ffa_fieldTypeIDs.append(iterDIType)

		#"ffa_get" call on v1 and computed offset => this is our iter limit !
		iterLimitRef = val(ZCI.zCtx.refType, atm(
			ATM__CALL,
			call("frf", [v1], ZCI.zCtx.refType)
		), False)
		iterLimit = val(
			iterDIType,
			atm(ATM__CALL, call(
				"ffa_get_" + str(iterDIType), [
					iterLimitRef,
					val(ZCI.zCtx.smaxType, atm(ATM__U32, offset), True),
				], iterDIType
			)),
			v1.Cst
		)
		ZCIDbg1(ZCI, "Got \"len\" field from given value, in FOR IN/OVR statement:" + v1.toStr(), prtLine=False)

	#now that we have iterDI type, update iter step
	iterStep.Type = iterDIType

	#limit must be prm
	iterDITypeInst = ZCI.getTypeInstanceFromID(iterDIType)
	if iterDITypeInst.dcnCommon.nature != NATURE__PRM:
		ZCIErr(ZCI, "Value given in FOR statement must have primitive type, in function " + tgtFct.name + " (STM_FOR).")



	#STEP 3: ITER DATITM, EXTERNAL & INTERNAL

	#the datItm the USER is going to use is INTERNAL (in inner scope)
	intIterDI = datItm(iterDIType, iterDIName, False, None)

	#however, the real iter exe & condition will be made using an EXTERNAL datItm (in cur scope)
	extIterDI = scope.nxtDcpDatItm(iterDIType)
	ZCIDbg1(ZCI, "Added FOR statement extIterDI: " + extIterDI.toStr())



	#STEP 4: BUILD ITER COND & ITER EXE

	#use extIterDI as val for calls
	extIterDIVal = val(iterDIType, atm(ATM__DATITM, extIterDI), False)

	#iter condition
	ope = zCtx__findMatchingOperator(ZCI.zCtx,
		"Oclt",
		[iterDIType,          iterDIType         ],
		[iterDITypeInst.name, iterDITypeInst.name]
	)
	if ope is None:
		ZCIErr(ZCI,
			"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(ZCI.zCtx, "Oclt") + \
			"\nCan't find a valid operator CLT to match between 2 types \"" + unpfxTypeName(ZCI.zCtx, iterDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR)."
		)
	res.iterCond = val(
		ope.retType,
		atm(ATM__CALL, call(
			ope.name,
			[extIterDIVal, iterLimit],
			ope.retType
		)),
		False
	)
	ZCIDbg1(ZCI, "Added FOR statement iter cond: " + res.iterCond.toStr())

	#iter exe
	ope = zCtx__findMatchingOperator(ZCI.zCtx,
		"Obad",
		[iterDIType,          iterDIType         ],
		[iterDITypeInst.name, iterDITypeInst.name]
	)
	if ope is None:
		ZCIErr(ZCI,
			"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(ZCI.zCtx, "Obad") + \
			"\nCan't find a valid operator BAD to match between 2 types \"" + unpfxTypeName(ZCI.zCtx, iterDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR)."
		)
	iterExe = atm(ATM__ASG, asg(
		extIterDIVal,
		val(
			iterDIType,
			atm(ATM__CALL, call(
				ope.name,
				[extIterDIVal, iterStep],
				ope.retType
			)),
			False
		)
	))
	ZCIDbg1(ZCI, "Added FOR statement iter exe: " + iterExe.toStr())



	#STEP 5: INNER SCOPE, INTERNAL 1ST EXE

	#create inner sub-scope (lcl)
	res.scope = newScp(parent=scope)

	#add internal iterDI
	res.scope.datItms.append(intIterDI)
	intIterDIVal = val(iterDIType, atm(ATM__DATITM, intIterDI), False)

	#build 1st inner scope exe: ON/IN => "intIterDI = extIterDI"
	if kind != KIND__OVR:
		int1stExe = atm(ATM__ASG, asg(intIterDIVal, extIterDIVal))

	#build 1st inner scope exe: OVR => "intIterDI = v1[extIterDI]"
	else:
		ope = zCtx__findMatchingOperator(ZCI.zCtx,
			"Oiin",
			[v1.Type,         iterDIType         ],
			[v1TypeInst.name, iterDITypeInst.name]
		)
		if ope is None:
			ZCIErr(ZCI,
				"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(ZCI.zCtx, "Oiin") + \
				"\nCan't find a valid operator IIN to match between types \"" + unpfxTypeName(ZCI.zCtx, v1TypeInst.name)[0] + "\" and \"" + unpfxTypeName(ZCI.zCtx, iDITypeInst.name)[0] + "\" in FOR statement, in function " + tgtFct.name + " (STM_FOR)."
			)

		#update INTERNAL iterDI type
		intIterDI.Type    = ope.retType
		intIterDIVal.Type = ope.retType

		#1st exe
		int1stExe = atm(ATM__ASG, asg(
			intIterDIVal,
			val(
				ope.retType,
				atm(ATM__CALL, call( # corresponds to call "v1[extIterDI]"
					ope.name,
					[v1, extIterDIVal],
					ope.retType
				)),
				False
			)
		))

	#add internal 1st exe
	res.scope.exes.append(int1stExe)
	ZCIDbg1(ZCI, "Added FOR statement inner 1st exe: " + int1stExe.toStr())



	#STEP 6: REST OF INNER SCOPE, INTERNAL LAST EXE, END

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in for statement, in function " + tgtFct.name + " (STM_FOR).")

	#extract ZCIs from it
	ZCIDbg1(ZCI, "Extracting FOR statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction of FOR statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	readLclScp(subScpZCIs, res.scope, tgtFct)

	#add iter exe as the last one in inner scope
	res.scope.exes.append(iterExe)

	#add statement to lcl scp
	scope.exes.append( atm(ATM__STM_WHI, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "FOR statement, in function " + tgtFct.name + " (STM_FOR).")
	ZCIDbg0(ZCI, "Processed FOR STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.dbgPause()



#while
def processWhiStm(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing WHI STM in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

	#read condition
	res          = stm_whi()
	res.iterCond = readVal(ZCI, "condition in WHI statement (STM_WHI).", scope)
	ZCIDbg1(ZCI, "Added while statement condition: " + res.iterCond.toStr())

	#read following includer
	optionalBlanks(ZCI, None)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Expected braces includer after condition in while statement, in function " + tgtFct.name + " (STM_WHI).")

	#extract ZCIs from it
	ZCIDbg1(ZCI, "Extracting WHI statement sub-scope.")
	subScpZCIs = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction of WHI statement sub-scope.")

	#parse them as inner sub-scp (lcl)
	subScp = newScp(parent=scope)
	readLclScp(subScpZCIs, subScp, tgtFct)
	res.scope = subScp

	#add statement
	scope.exes.append( atm(ATM__STM_WHI, res) )

	#end of ZCI expected
	endOfZCI(ZCI, "WHI statement, in function " + tgtFct.name + " (STM_WHI).")
	ZCIDbg0(ZCI, "Processed WHI STM in function " + tgtFct.name + ": " + res.toStr())
	ZCI.dbgPause()






# -------- JUMPS --------

#return keyword
def processRetJmp(ZCI, scope, tgtFct):
	ZCIDbg0(ZCI, "Processing RET JMP in function " + tgtFct.name, prtLine=False)
	optionalBlanks(ZCI, None)

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
	ZCIDbg0(ZCI, "Processed RET JMP in function " + tgtFct.name + " with given value " + retValTxt)
	ZCI.dbgPause()






# -------- EXECUTION --------

#read given ZCIs => add them to given scope
def readLclScp(ZCIs, scope, tgtFct): #tgtFct is for debug
	for ZCI in ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDbg1(ZCI, "Treating local ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=True)

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
				scope.exes.append( atm(ATM__JMP, jmp(JMP__BRK)) )
				endOfZCI(ZCI, "break jump ZCI (JMP_BRK).")
				continue
			if str_cmp("ctn", firstWord):
				scope.exes.append( atm(ATM__JMP, jmp(JMP__CTN)) )
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
			if str_cmp("whi", firstWord):
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
	zCtx.updateLogLvl(STEP.C03)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C03 PROCESS LCLs : beginning =========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#main fct existence
	mainFct = zCtx__getFctFromName(zCtx, "GFmain")
	if zCtx.cpl.mode == CPL__MODE_EXE and mainFct is None:
		zCtx.err("Missing \"main\" function to compile as executable.", prtSubCtxs=False, prtLine=False)
	elif zCtx.cpl.mode == CPL__MODE_SDL and mainFct is not None:
		zCtx.err("Got a \"main\" function to compile as SDL.", prtSubCtxs=False, prtLine=False)

	#process every fct
	for f in zCtx.cpl.fcts:
		if f.ext or f.content is None: #ext or already processed
			continue

		#can't process dcn-dep fcts
		if f.dcnDep:
			zCtx.dbg0("Method \"" + f.name + "\" is public but also dcn-dependant => not processing it directly.")
			continue

		#process fct scope & remove its content ZCIs
		readLclScp(f.content, f.scope, f)
		f.content = None

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C03 PROCESS LCLs : end =========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#gather gbl scp + fcts
		output = zCtx.cpl.gblScp.toStr()
		for f in zCtx.cpl.fcts:
			if not f.ext:
				output += f.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c03.dl", output)
