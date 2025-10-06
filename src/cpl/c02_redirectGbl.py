#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#std
from std.string import *

#internal
from zctx import *
from pcpl.p3_ZCSAndImp import *






# -------- EXT_LNK --------

#external linking
def processLnk(ZCI):
	ZCIDbg(ZCI, "Processing SDL addition.", prtLine=False)
	jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

	#library linking path
	path = os.path.realpath( readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS_EXTENDED) )

	#check existence
	if not os.path.isfile(path):
		ZCIErr(ZCI, "Shared & Dynamically Linked (SDL) library " + path + " not found.")
	ZCIDbg(ZCI, "SDL file \"" + path + "\" found.", prtLine=False)

	#add link
	if path not in zCtx.cpl.lnkLibs:
		zCtx.cpl.lnkLibs.append(path)
		ZCIDbg(ZCI, "Added SDL \"" + path + "\" to linking list.")
	else:
		ZCIDbg(ZCI, "SDL \"" + path + "\" already in linking list => skipping it.")

	#end of ZCI expected
	endOfZCI(ZCI, "library linking ZCI (EXT_LNK).")
	ZCI.deepDbgPause()






# -------- DCL_TYP --------

#type declaration
def processTypeDcl(ZCI):
	ZCIDbg(ZCI, "Processing type declaration.", prtLine=False)
	jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", dblUnderscores=True)
	if len(ZCI.modPfx) == 0:
		fullName = "GU" + rawName
	else:
		fullName = ZCI.modPfx + 'U' + rawName

	#check already existing
	if ZCI.getTypeIDFromName(fullName) != TYPE_ID__UNKNOWN:
		modPfxTxt = ""
		if len(ZCI.modPfx) != 0:
			modPfxTxt = unpfxMod(ZCI.modPfx)
		ZCIErr(ZCI, "Type " + modPfxTxt + rawName.replace("__", '_') + " already exists, can't declare a new one with the same name (DCL_TYP).")
	ZCIDeepDbg(ZCI, "New type does not exist yet.", prtLine=False)

	#explicit declination degree if any
	dcnDeg = 0
	if ZCI.get() == '[':
		peerIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		ZCI.inc()

		#skip beginning blanks
		optionalBlanks(ZCI, "declination degree in type declaration ZCI (DCL_TYP)", blanks=BLANKS_EXTENDED)

		#strip ending blanks
		begIdx    = ZCI.ctx.icontent.idx
		dcnDegTxt = str_stripEnd( str_sub(ZCI.ctx.icontent.s, start=begIdx, stop=peerIdx-1), charset=BLANKS_EXTENDED)

		#non-integer dcnDeg
		if not str_isConvertible_int(dcnDegTxt):
			ZCIErr(ZCI, "Invalid explicit declination degree given (must be an integer).")

		#negative dcnDeg
		dcnDeg = int(dcnDegTxt)
		if dcnDeg < 0:
			ZCIErr(ZCI, "Invalid explicit declination degree given (must be positive).")

		#forward after includer
		ZCI.forward(peerIdx - begIdx + 1)
	ZCIDeepDbg(ZCI, "New type is declinable of degree " + str(dcnDeg), prtLine=False)

	#must be followed by blanks once more
	if ZCI.get() not in BLANKS:
		ZCIErr(ZCI, "Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
	jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

	#add generic type for the moment (it is incomplete: we don't know if it is a structure, if it has a parent...)
	newTypeID   = ZCI.zCtx.cpl.newTyp(fullName, dcnDeg)
	newTypeInst = ZCI.getTypeInstanceFromID(newTypeID)
	ZCIDbg(ZCI, "Explicitely added type " + newTypeInst.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		ZCIDbg(ZCI, "Type declaration is via structure syntax.", prtLine=False)
		newTypeInst.dcnCommon.size   = ZCI.zCtx.refSize
		newTypeInst.dcnCommon.nature = NATURE__STC

		#reading fields
		newTypeInst.dcnCommon.fields = readDatItmSeq(
			ZCI, "type declaration ZCI (DCL_TYP).",
			ZCI.zCtx.cpl.gblScp,
			cstValsOnly = True
		)
		if len(newTypeInst.dcnCommon.fields) == 0:
			ZCIErr(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDatItmSeq cannot return 0-length list)

		#update stcSize
		newTypeInst.computeStcSize(ZCI.zCtx.cpl.types)

		#set REF as parent
		newTypeInst.dcnCommon.parent = ZCI.zCtx.rootTypes[RT__REF]

	#process type content: type-copy syntax
	else:
		ZCIDbg(ZCI, "Type declaration is via type-copy syntax.", prtLine=False)
		parentID   = readType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		parentInst = ZCI.getTypeInstanceFromID(parentID)

		#copying itself, no matter the declination (error case seems obvious, though required)
		if parentInst.dcnCommon == newTypeInst.dcnCommon:
			ZCIErr(ZCI, "Type cannot be declared as a copy of itself or one of its declination.")

		#copy every important field from parent
		newTypeInst.dcnCommon.size   = parentInst.dcnCommon.size
		newTypeInst.dcnCommon.nature = parentInst.dcnCommon.nature
		newTypeInst.dcnCommon.fields = parentInst.dcnCommon.fields
		newTypeInst.dcnCommon.parent = parentID

	#end of ZCI expected
	endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	ZCIDbg(ZCI, "Type declaration " + newTypeInst.name + " processed.", prtLine=False)
	ZCI.deepDbgPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(ZCI, scope, tgtFct=None):

	#debug
	scpTxt = ""
	if tgtFct is None:
		scpTxt = "in global scope"
	else:
		scpTxt = "in function " + tgtFct.name
	ZCIDbg(ZCI, "Processing enumerate declaration.", prtLine=False)
	jumpBlankZone(ZCI, "Enumerate name in enumerate declaration " + scpTxt + " (DCL_ENM)")

	#get full enm name
	rawName  = readName(ZCI, "Enumerate name in enumerate declaration " + scpTxt + " (DCL_ENM).", dblUnderscores=True)
	fullName = getDatItmModPfxFromScope(ZCI, scope) + rawName

	#must be followed by braces includer
	optionalBlanks(ZCI, "fields inside braces includer in enumerate declaration " + scpTxt + " (DCL_ENM).", blanks=BLANKS_EXTENDED)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Missing fields inside braces includer in enumerate declaration " + scpTxt + " (DCL_ENM).")

	#read fields
	fields = readDatItmSeq(
		ZCI, "enumerate declaration ZCI (DCL_ENM).",
		scope,
		cstValsOnly          = True,
		allowUnsolvableTypes = True
	)
	for di in fields:
		if di.Type != TYPE_ID__UNKNOWN: #no type must be found (neither explicit type given or initial value)
			ZCIErr(ZCI, "No explicit type or value is allowed in enumerate declaration " + scpTxt + " (DCL_ENM).")

	#compute which type will be used
	ZCIDeepDbg(ZCI, "Enumerate length: " + str(len(fields)), prtLine=False)
	if len(fields) <= 0x1_00:
		ZCIDeepDbg(ZCI, "Enumerate length indexing can be contained in U8 => using that type for them.", prtLine=False)
		t = ZCI.zCtx.rootTypes[RT__U8]
	elif len(fields) <= 0x1_00_00:
		ZCIDeepDbg(ZCI, "Enumerate length indexing can be contained in U16 => using that type for them.", prtLine=False)
		t = ZCI.zCtx.rootTypes[RT__U16]
	elif len(fields) <= 0x1_00_00_00_00:
		ZCIDeepDbg(ZCI, "Enumerate length indexing can be contained in U32 => using that type for them.", prtLine=False)
		t = zCtx.rootTypes[RT__U32]
	else:
		ZCIErr(ZCI, "Too much fields in enumerate " + scpTxt + " (congrats for reaching that error, how did you managed to get it ?, DCL_ENM).")

	#fullfill fields
	for f in range(len(fields)):
		fields[f].Type  = t
		fields[f].value = val(t, atm(ATM__REF, f), Cst=True) #value stored as it was a ref to be cashted into type t

	#create enumerate
	enmDI = datItm(t, fullName, True, None, Cst=True, fields=fields)
	checkAlreadyDeclaredDataItemOrField(ZCI, enmDI, scope.datItms)
	scope.datItms.append(enmDI)

	#end of ZCI expected
	endOfZCI(ZCI, "enumerate declaration " + scpTxt + " (DCL_ENM).")
	ZCIDbg(ZCI, "Enumerate declaration processed.", prtLine=False)
	ZCI.deepDbgPause()






# -------- DCL_FWD - DCL_FCT --------

#common parsing
def processFctDcl_partial(ZCI, parsingFwd=False):

	#function name: maybe it is type related (method) => try reading a type
	methodType = readType(ZCI, "function name in function declaration/forwarding ZCI (DCL_FCT/DCL_FWD).", errIfNotExisting=False)

	#method name must be followed by a dot
	isMethod = (methodType != TYPE_ID__UNKNOWN)
	if isMethod:
		if ZCI.get() != '.':
			ZCIErr(ZCI, "Expected a dot '.' after type given in method name.")
		ZCI.inc()

	#read function name
	rawName = readName(ZCI, "function name in function declaration/forwarding ZCI (DCL_FCT/DCL_FWD).",
		parseModPfxes         = parsingFwd, #allow mod pfx notation in fwd to be able to fwd sthing from a mod to another (or gbl...)
		modPfxes_asHeaderOnly = parsingFwd, #but fct dcl must NOT have this feature: their SCOPE define their modPfx
		dblUnderscores        = True,
		whitelist             = FCT_NAME_CHARSET
	)

	#must be followed by parameters between parentheses includer
	if ZCI.get() != '(':
		ZCIErr(ZCI, "Expected parameters between parentheses includer right after function name.")

	#parameters
	params = readDatItmSeq(
		ZCI, "function declaration/forwarding ZCI (DCL_FCT/DCL_FWD)",
		ZCI.zCtx.cpl.gblScp,
		cstValsOnly = True,
		allowEmpty  = True
	)
	for p in params: #add "lcl" module prefix
		p.name = 'L' + p.name

	#go to the next interesting thing (if any)
	optionalBlanks(ZCI, None)

	#targetting operator
	isOpe = (rawName in OPERATOR_FCTNAME2SYMBOL.keys())

	#case 1: regular function
	if not isOpe:

		#additionnal check: name availability !HERE, WE WANT TO GUARANTEE NO CONFUSION BETWEEN GBL DI NAMES & FCT NAMES. USER CODE CAN HAVE AMBIGUITY, BUT Z NOTATION CAN'T: THIS IS WHY WE USE A "TMP PREFIXED NOTATION" TO CHECK THEM TEMPORARILY.
		if not isMethod:
			equivalentDIName = getDatItmModPfxFromScope(ZCI, ZCI.zCtx.cpl.gblScp)
			for gdi in ZCI.zCtx.cpl.gblScp.datItms:
				if gdi.name == equivalentDIName:
					ZCIErr(ZCI, "Unable to declare/forward function \"" + ZCI.modPfx + rawName + "\" because a global data item with the same name already exist (avoiding confusion).")

		#build full fct name
		baseName = rawName #modPfx already included while reading (DCL_FWD)
		if not parsingFwd:
			baseName = ZCI.modPfx + rawName #use modPfx from current SCOPE (DCL_FCT)
		fullName = getFctNameFromPfxName(ZCI, baseName, methodOf=methodType)

	#case 2: operator
	else:
		if isMethod:
			ZCIErr(ZCI, "Operator functions cannot be used as methods for a given type (type " + ZCI.getTypeNameFromID(methodType) + " targetted for operator " + OPERATOR_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]] + ").")

		#build full function name
		fullName = 'O' + OPERATOR_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]]
		for p in params:
			fullName += '_' + ZCI.getTypeNameFromID(p.Type)

	#check if function/method/operator already exists
	if getFctFromName(ZCI, fullName) is not None:
		ZCIErr(ZCI, "Already have a function/method/operator with name " + fullName)

	#create fct instance (set VOID retType for the moment)
	f        = newFct(fullName, TYPE_ID__UNKNOWN, params, ZCI.zCtx.cpl.gblScp)
	f.method = isMethod
	ZCI.zCtx.cpl.fcts.append(f)

	#add params as available data items in fct scope
	for p in params:
		f.scope.datItms.append(p)

	#return raw name (useful for fwd only actually)
	return rawName




#function declaration
def processFctDcl(ZCI):
	ZCIDbg(ZCI, "Processing function declaration.", prtSubCtxs=True)

	#parse until after params
	processFctDcl_partial(ZCI)
	f = ZCI.zCtx.cpl.fcts[-1]

	#return type explicitly given => non-VOID
	retType = TYPE_ID__UNKNOWN
	if ZCI.get() != '{':
		retType = readType(ZCI, "return type in function declaration/forwarding ZCI (DCL_FCT)")

		#move to function content
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
		if ZCI.get() != '{':
			ZCIErr(ZCI, "Expected to have function content after return type given (braces includer).")
	ZCIDeepDbg(ZCI, "Return type detected \"" + ZCI.getTypeNameFromID(retType) + "\".")

	#content
	ZCIDeepDbg(ZCI, "Extracting function \"" + f.name + "\"'s content.")
	content = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDeepDbg(ZCI, "End of extraction for function \"" + f.name + "\".")

	#complete fct info
	f.retType = retType
	f.content = content
	ZCIDeepDbg(ZCI, "Added to cpl data as: " + f.toStr(), prtSubCtxs=False, prtLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "function declaration ZCI (DCL_FCT).")
	ZCIDbg(ZCI, "Function declaration processed.", prtLine=False)
	ZCI.deepDbgPause()



#function forwarding declaration
def processFwdDcl(ZCI):
	ZCIDbg(ZCI, "Processing function forwarding declaration.", prtSubCtxs=True)

	#get type to forward
	fwdType = readType(ZCI, "type to forward into, in function forwarding ZCI (DCL_FWD).")
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

	#parse until after params
	pfxName = processFctDcl_partial(ZCI, parsingFwd=True) #rawName returned is actually a pfxName because of Fwd specific option
	dstF    = ZCI.zCtx.cpl.fcts[-1]

	#return type explicitly given => non-VOID
	retType = TYPE_ID__UNKNOWN
	if not ZCI.reachedEnd():
		retType = readType(ZCI, "return type in function forwarding ZCI (DCL_FWD)")

		#move to the very end
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
	ZCIDeepDbg(ZCI, "Return type detected \"" + ZCI.getTypeNameFromID(retType) + "\".")

	#look for src fct
	srcFullName = getFctNameFromPfxName(ZCI, pfxName, methodOf=fwdType)
	srcF        = getFctFromName(ZCI, srcFullName)
	if srcF is None:
		ZCIErr(ZCI, "Unable to find source function \"" + srcFullName + "\" to forward from (DCL_FWD).")

	#requirement 1: must be a method
	if not dstF.method:
		ZCIErr(ZCI, "Can only forward METHOD functions (DCL_FWD).")

	#requirement 2: must have the same exact parameters, except the 1st one (number, names, types)
	paramVals = []
	if len(dstF.params) != len(srcF.params):
		ZCIErr(ZCI, "Can only forward functions with exact same number of parameters (expected " + str(len(srcF.params)) + ", got " + str(len(dstF.params)) + ", in DCL_FWD).")
	for p in range(len(srcF.params)):
		if p != 0:
			if dstF.params[p].name != srcF.params[p].name:
				ZCIErr(ZCI, "Can only forward functions with exact same parameters (expected name \"" + srcF.params[p].name + "\" as parameter " + str(p+1) + ", got \"" + dstF.params[p].name + "\", in DCL_FWD).")
			if dstF.params[p].Type != srcF.params[p].Type:
				ZCIErr(ZCI, "Can only forward functions with exact same parameters (expected type \"" + ZCI.getTypeNameFromID(srcF.params[p].Type) + "\" as parameter " + str(p+1) + ", got \"" + ZCI.getTypeNameFromID(dstF.params[p].Type) + "\", in DCL_FWD).")

		#add param values
		paramVals.append(
			val(dstF.retType, atm(ATM__DATITM, dstF.params[p]), dstF.params[p].Cst)
		)

	#requirement 3: must ret void if src ret void
	if retType != TYPE_ID__UNKNOWN and srcF.retType == TYPE_ID__UNKNOWN:
		ZCIErr(ZCI, "Cannot forward as non-void because source function is void (DCL_FWD).")

	#calling src fct with dst params (which should be the same btw)
	generatedCallAtm = atm(ATM__CALL, call(srcF.name, paramVals, srcF.retType))

	#set exec as VFC or JMP_RET
	if retType == TYPE_ID__UNKNOWN:
		dstExe = generatedCallAtm
	else:
		retVal = val(srcF.retType, generatedCallAtm, False) #retType here does not really matter, it will be cashted in the retType of dstF in all cases
		dstExe = atm(ATM__JMP, jmp(JMP__RET, retVal))

	#complete new fct info
	dstF.retType = retType
	dstF.scope.exes.append(dstExe) #add to fct scope as already processed content
	ZCIDeepDbg(ZCI, "Added to cpl data as: " + dstF.toStr(), prtSubCtxs=False, prtLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "function forwarding ZCI (DCL_FWD).")
	ZCIDbg(ZCI, "Function forwarding processed.", prtLine=False)
	ZCI.deepDbgPause()






# -------- REMAINING ZCIs: VFC_VFC, ASG_ASG, DCL_DAT --------

#data item assignment only (assigning to existing destination) WARNING: ZCI must be RIGHT BEFORE SRC VALUE !
def processAsg(ZCI, scope, tgtFct, dstDI):

	#debug
	scpTxt  = ""
	cstOnly = False
	if tgtFct is None:
		scpTxt  = "in global scope"
		cstOnly = True
	else:
		scpTxt = "in function " + tgtFct.name
	ZCIDbg(ZCI, "Processing data item assignment " + scpTxt + " (ASG_ASG).", prtLine=False)

	#read src value to be assigned
	srcVal = readVal(ZCI, "source value in assignment " + scpTxt + " (ASG_ASG).", scope, cstOnly=cstOnly)

	#add execution to concerned scope
	scope.exes.append( atm(ATM__ASG, asg(dstDI, srcVal)) )

	#end of ZCI expected
	endOfZCI(ZCI, "data item assignment " + scpTxt + " (ASG_ASG).")
	ZCIDbg(ZCI, "Data item assignment processed.", prtLine=False)
	ZCI.deepDbgPause()



#data item declaration (including assignment with initial value)
def processDclDat(ZCI, scope, tgtFct, isCst):

	#debug
	scpTxt         = ""
	cstInitValOnly = False
	if tgtFct is None:
		scpTxt         = "in global scope"
		cstInitValOnly = True
	else:
		scpTxt = "in function " + tgtFct.name
	ZCIDbg(ZCI, "Processing data item declaration " + scpTxt + " (DCL_DAT).", prtLine=False)

	#read the whole ZCI from the start
	di = readDatItm(ZCI, "Data item declaration " + scpTxt + " (DCL_DAT).", scope, cstInitValOnly=cstInitValOnly)

	#don't allow the use of module notation in name when declaring !
	givenModPfx = extractModPfx(di.name)
	if len(givenModPfx) != 0:
		ZCIErr(ZCI, "Cannot use module notation in name when declaring a data item " + scpTxt + " (DCL_DAT detected, you should declare inside a module instead).")

	#set some important info to the NEWLY CREATED data item
	di.name = getDatItmModPfxFromScope(ZCI, scope) + di.name
	di.Cst  = isCst

	#add declaration to scope
	checkAlreadyDeclaredDatItmOrField(ZCI, di, scope.datItms) #check already existing
	scope.datItms.append(di)

	#end of ZCI expected
	endOfZCI(ZCI, "data item declaration " + scpTxt + " (DCL_DAT).")
	ZCIDbg(ZCI, "Data item declaration processed.", prtLine=False)
	ZCI.deepDbgPause()



#concerns more step 3 actually
def processVFC(ZCI, scope, tgtFct):

	#debug
	scpTxt = ""
	if tgtFct is None:
		scpTxt = "in global scope"
	else:
		scpTxt = "in function " + tgtFct.name
	ZCIDbg(ZCI, "Processing void returning function call " + scpTxt + " (VFC_VFC).", prtLine=False)

	#local scope only
	if tgtFct is None:
		ZCIErr(ZCI, "Detected void returning function call in global scope but this is only allowed in local scope (VFC_VFC).")

	#read ZCI content as reading a value: it MUST be a call (either operator, !VFC or VFC)
	v = readVal(ZCI, "void returning function call " + scpTxt + " (VFC_VFC).", scope)
	if v.vdat.id != ATM__CALL:
		ZCIErr(ZCI, "Invalid ZCS, unknown ZCI given " + scpTxt + " (Expected a void returning function call, VFC_VFC).")

	#store call in scope exe <---- Note that we don't care about the return type for the moment, it can be anything
	scope.exes.append(v.vdat)

	#end of ZCI expected
	endOfZCI(ZCI, "void returning function call (VFC_VFC).")
	ZCIDbg(ZCI, "Void returning function call processed.", prtLine=False)
	ZCI.deepDbgPause()



#remaining ZCIs can be DCL_DAT, ASG_ASG or VFC_VFC (the last one only allowed in local scope)
def processRemainingZCI(ZCI, scope, tgtFct=None):
	ZCIDeepDbg(ZCI, ">>>>>>>>>>>>>>>>>>>>>>>>> ZCI:\n  " + ZCI.toStr() + "\n\"" + ZCI.txt + "\"\n\"" + ZCI.ctx.icontent.s[ZCI.startIdx-200:ZCI.ctx.icontent.idx+1] + "§" + ZCI.ctx.icontent.s[ZCI.ctx.icontent.idx] + "§" + ZCI.ctx.icontent.s[ZCI.ctx.icontent.idx+1:ZCI.stopIdx+201] + "\"")

	#try reading a type (in a separated copy, in all cases we will have to read from the start)
	tmpCopy = ZCI.copy()
	tID     = readType(tmpCopy, None, errIfNotExisting=False)

	#starting with a type name => DCL_DAT, else => can be anything
	if tID == TYPE_ID__UNKNOWN:

		#try getting a name
		name = readName(tmpCopy, None, parseModPfxes=True, modPfxes_asHeaderOnly=True)

		#no name => can only be a VFC_VFC
		if len(name) == 0:
			processVFC(ZCI, scope, tgtFct)
			return

		#got a name, well OK, but it can still be a VFC_VFC... unless we don't have asg symbol !
		optionalBlanks(tmpCopy, None)
		if readSym(tmpCopy) != SYM__ASG:
			processVFC(ZCI, scope, tgtFct)
			return

		#already have a data item with that name => ASG_ASG then
		di = getDatItmFromPfxName(name, scope)
		if di is not None:

			#forward right before value
			tmpCopy.forward(SYM_LENGTHS[SYM__ASG])
			optionalBlanks(tmpCopy, None)

			#process ASG_ASG
			ZCI.forwardAlike(tmpCopy)
			processAsg(ZCI, scope, tgtFct, di)
			return

	#in every other cases => DCL_DAT
	processDclDat(ZCI, scope, tgtFct, False)






# -------- EXECUTION --------

#compilation
def c02_redirectGbl(zCtx):
	zCtx.step = STEP.C02
	zCtx.dbgSepLine()
	zCtx.dbg("=================================================================================")
	zCtx.dbg("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.dbg("=================================================================================")
	zCtx.deepDbgPause()

	#analyse every global ZCI
	for ZCI in zCtx.ZCIs:
		initialCtx = ZCI.ctx.copy()
		ZCIDeepDbg(ZCI, "Treating global ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=True)

		#read 1st ZCI word
		firstWord = readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)



		#CASE 1 - BEGINNING WITH KEYWORD AND FORBIDDEN

		#bigrams
		if len(firstWord) == 2:
			if str_cmp("if", firstWord):
				ZCIErr(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")

		#trigrams
		elif len(firstWord) == 3:

			#1.1 - jumps
			if str_cmp("brk", firstWord):
				ZCIErr(ZCI, "BREAK jumps are not allowed in global scope (JMP_BRK detected).")
			if str_cmp("ctn", firstWord):
				ZCIErr(ZCI, "CONTINUE jumps are not allowed in global scope (JMP_CTN detected).")
			if str_cmp("ret", firstWord):
				ZCIErr(ZCI, "RETURN jumps are not allowed in global scope (JMP_RET detected).")

			#1.2 - statements
			if str_cmp("elf", firstWord) or str_cmp("els", firstWord):
				ZCIErr(ZCI, "IF/ELIF/ELSE statements are not allowed in global scope (STM_IF_ detected).")
			if str_cmp("for", firstWord):
				ZCIErr(ZCI, "FOR statements are not allowed in global scope (STM_FOR detected).")
			if str_cmp("while", firstWord):
				ZCIErr(ZCI, "WHILE statements are not allowed in global scope (STM_WHI detected).")
			if str_cmp("swi", firstWord):
				ZCIErr(ZCI, "SWITCH statements are not allowed in global scope (STM_SWI detected).")

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
					processFctDcl(ZCI)
					continue

				#2.5 - Function forwarding
				if str_cmp("fwd", firstWord):
					jumpBlankZone(ZCI, "Type to forward into, in function forwarding ZCI (DCL_FWD).") #forward to function name directly
					processFwdDcl(ZCI)
					continue

				#2.6 - Constant data item declaration
				if str_cmp("cst", firstWord):
					jumpBlankZone(ZCI, "Constant keyword in data item declaration ZCI (DCL_DAT).")
					processDclDat(ZCI, zCtx.cpl.gblScp, None, True)
					continue



		#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

		#reset ZCI at initial state & try parsing it, no other possibility for a global ZCI
		ZCI.resetCtx(initialCtx)
		processRemainingZCI(ZCI, zCtx.cpl.gblScp)

	#debug
	zCtx.dbg("===========================================================================")
	zCtx.dbg("======================== C02 REDIRECT GLOBAL : end ========================")
	zCtx.dbg("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.deepDbgPause()

	#debug output file
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		dumpZCIs(zCtx.ZCIs, "dbg/" + path_name(zCtx.initialCtx.filename) + ".c01.dl", oneLine=False)
