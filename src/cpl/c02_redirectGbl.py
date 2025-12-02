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
	ZCIDbg0(ZCI, "Processing SDL addition.", prtLine=False)
	jumpBlankZone(ZCI, "File path in library linking ZCI (EXT_LNK)")

	#library linking path
	path = readName(ZCI, "File path in library linking ZCI (EXT_LNK).", blacklist=BLANKS_EXTENDED)[1]
	if not path.startswith('/'):
		path = os.path.normpath(ZCI.ctx.dirname + '/' + path)

	#check existence
	if not os.path.isfile(path):
		ZCIErr(ZCI, "Shared & Dynamically Linked (SDL) library " + path + " not found.")
	ZCIDbg0(ZCI, "SDL file \"" + path + "\" found.", prtLine=False)

	#add link
	if path not in ZCI.zCtx.cpl.lnkLibs:
		ZCI.zCtx.cpl.lnkLibs.append(path)
		ZCIDbg0(ZCI, "Added SDL \"" + path + "\" to linking list.")
	else:
		ZCIDbg0(ZCI, "SDL \"" + path + "\" already in linking list => skipping it.")

	#load it
	ZCI.zCtx.loadExtFP(path)

	#end of ZCI expected
	endOfZCI(ZCI, "library linking ZCI (EXT_LNK).")
	ZCI.dbgPause()






# -------- DCL_TYP --------

#type declaration
def processTypeDcl(ZCI, isPub):
	ZCIDbg0(ZCI, "Processing type declaration.", prtLine=False)
	jumpBlankZone(ZCI, "Type name in type declaration ZCI (DCL_TYP)")

	#get full type name considered as "undeclinated"
	rawName = readName(ZCI, "Type name in type declaration ZCI (DCL_TYP).", dblUnderscores=True)[1]
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
	ZCIDbg1(ZCI, "New type does not exist yet.", prtLine=False)

	#special case: don't overlap "raw" types
	if fullName.startswith("GUraw"):
		overlap = False
		for i in fullName[5:]:
			if i not in string.digit:
				break
			overlap = True
		if overlap:
			ZCIErr(ZCI, "Type \"" + fullName[2:] + "\" overlap with \"raw\" types => forbidden, in type declaration ZCI (DCL_TYP).")

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
			ZCIErr(ZCI, "Invalid explicit declination degree given (must be an integer, DCL_TYP).")

		#negative dcnDeg
		dcnDeg = int(dcnDegTxt)
		if dcnDeg < 0:
			ZCIErr(ZCI, "Invalid explicit declination degree given (must be positive, DCL_TYP).")

		#too big dcnDeg
		if dcnDeg > ZCI.zCtx.dcnDegMax:
			ZCIErr(ZCI, "Invalid explicit declination degree given (maximum " + str(ZCI.zCtx.dcnDegMax) + ", " + str(dcnDeg) + " given, DCL_TYP)")

		#forward after includer
		ZCI.forward(peerIdx - begIdx + 1)
	ZCIDbg1(ZCI, "New type is declinable of degree " + str(dcnDeg), prtLine=False)

	#must be followed by blanks once more
	if ZCI.get() not in BLANKS:
		ZCIErr(ZCI, "Expected blank zone after type name in type declaration ZCI (DCL_TYP).")
	jumpBlankZone(ZCI, "Type content definition in type declaration ZCI (DCL_TYP).")

	#add generic info of type, but it is incomplete for the moment: we don't know if it is a structure, if it has a parent...
	newTypeID   = ZCI.zCtx.cpl.newTyp(fullName, dcnDeg, isPub=isPub)
	newTypeInst = ZCI.getTypeInstanceFromID(newTypeID)
	ZCIDbg0(ZCI, "Explicitely added type " + newTypeInst.name + " but there are still missing information about it (incomplete for the moment).")

	#process type content: structure syntax
	if ZCI.get() == '{':
		ZCIDbg0(ZCI, "Type declaration is via structure syntax.", prtLine=False)
		newTypeInst.dcnCommon.nature = NATURE__STC

		#reading fields
		newTypeInst.dcnCommon.fields = readDatItmSeq(
			ZCI, "type declaration ZCI (DCL_TYP).",
			ZCI.zCtx.cpl.gblScp,
			cstValsOnly           = True,
			forbidDcnKwInTypeDcns = False
		)
		if len(newTypeInst.dcnCommon.fields) == 0:
			ZCIInt(ZCI, "Must have at least 1 field in structure type.") #should never occur, right ? (readDatItmSeq cannot return 0-length list)

		#special case: no "raw" type allowed
		for di in newTypeInst.dcnCommon.fields:
			if di.Type == ZCI.zCtx.rawType:
				ZCIErr(ZCI, "Structure type \"" + unpfxTypeName(ZCI.zCtx, fullName)[0] + "\" contains a field of type \"raw\" => forbidden, in type declaration ZCI (DCL_TYP).")

		#compute size
		newTypeInst.computeStcSize(ZCI.zCtx.cpl)

	#process type content: type-copy syntax
	else:
		ZCIDbg0(ZCI, "Type declaration is via type-copy syntax.", prtLine=False)
		parentID   = readType(ZCI, "type declaration ZCI (DCL_TYP).") #read type given as 2nd argument
		parentInst = ZCI.getTypeInstanceFromID(parentID)

		#special case: no "raw" type allowed
		if parentID == ZCI.zCtx.rawType:
			ZCIErr(ZCI, "Type \"" + unpfxTypeName(ZCI.zCtx, fullName)[0] + "\" is being copied from \"raw\" type => forbidden, in type declaration ZCI (DCL_TYP).")

		#copying itself, no matter the declination (error case seems obvious, though required)
		if parentInst.dcnCommon == newTypeInst.dcnCommon:
			ZCIErr(ZCI, "Type cannot be declared as a copy of itself or one of its declination (DCL_TYP).")

		#copy every important field from parent
		newTypeInst.dcnCommon.size   = parentInst.dcnCommon.size
		newTypeInst.dcnCommon.nature = parentInst.dcnCommon.nature
		newTypeInst.dcnCommon.fields = parentInst.dcnCommon.fields
		newTypeInst.dcnCommon.parent = parentID

	#atm related gen
	if ZCI.zCtx.cpl.mode == CPL__MODE_Z and ZCI.zCtx.cpl.opts['ATM_GENERATED_CONTENT'] == "ON":
		ZCIDbg0(ZCI, "Generating ATM related content.", prtLine=False)

		#create ATM ID cst
		atmID_val = val(ZCI.zCtx.smaxType, atm(ATM__S64, newTypeID), True)
		atmID_DI  = datItm(
			ZCI.zCtx.smaxType,
			"MAtm_" + ZCI.modPfx + "E" + rawName,
			True,
			atmID_val
		)
		atmID_DI.isPub = True
		ZCI.zCtx.cpl.gblScp.datItms.append(atmID_DI)

		#create a param "e" for toAtm method
		paramE     = datItm(newTypeID, "Le", False, None)
		paramE_val = val(newTypeID, atm(ATM__DATITM, paramE), False)

		#create toAtm method
		toAtm_fct = newFct(
			"GT" + fullName + "_FtoAtm",
			newTypeID,
			[paramE],
			ZCI.zCtx.cpl.gblScp,
			methodOf=newTypeID
		)
		ZCI.zCtx.cpl.fcts.append(toAtm_fct)
		toAtm_fct.scope.datItms.append(paramE) #also add param as 1st datItm in fct scope

		#fct content is: "ret atm{ id=^Atm.type, dat=@e }"
		# => dcp into:
		#     smax D0 = ^Atm.type
		#     ref  D1 = @e
		#     atm  D2
		#     D2.id  = D0
		#     D2.dat = D1
		#     ret D2

		#"smax D0 = ^Atm.type"
		dcpDI_id         = toAtm_fct.scope.nxtDcpDatItm(ZCI.zCtx.smaxType)
		dcpDI_id.inited  = True
		dcpDI_id.initVal = atmID_val

		#"ref DI = @e"
		dcpDI_dat         = toAtm_fct.scope.nxtDcpDatItm(ZCI.zCtx.refType)
		dcpDI_dat.inited  = True
		dcpDI_dat.initVal = val(
			ZCI.zCtx.refType,
			atm(ATM__CALL, call("frf", [paramE_val], ZCI.zCtx.refType)),
			False
		)

		#"atm D2"
		dcpDI_mainStc     = toAtm_fct.scope.nxtDcpDatItm(ZCI.zCtx.atmType)
		dcpDI_mainStcVal  = val(ZCI.zCtx.atmType, atm(ATM__DATITM, dcpDI_mainStc), True)

		#"D2.id = D0"
		toAtm.fct.scope.exes.append(atm(
			ATM__ASG,
			asg(
				val(ZCI.zCtx.smaxType, atm(
					ATM__FFA,
					ffa(dcpDI_mainStcVal, 0)
				), False),
				val(ZCI.zCtx.smaxType, atm(
					ATM__DATITM,
					dcpDI_id
				), False)
			)
		))

		#"D2.dat = D1"
		toAtm.fct.scope.exes.append(atm(
			ATM__ASG,
			asg(
				val(ZCI.zCtx.refType, atm(
					ATM__FFA,
					ffa(dcpDI_mainStcVal, ZCI.zCtx.smaxSize) #no need to apply any padding, #smax must be arch type
				), False),
				val(ZCI.zCtx.refType, atm(
					ATM__DATITM,
					dcpDI_dat
				), False)
			)
		))

		#"ret D2"
		toAtm_fct.scope.exes.append(atm(
			ATM__JMP,
			jmp(JMP__RET, retVal=val(
				ZCI.zCtx.atmType,
				atm(ATM__DATITM, dcpDI_mainStc),
				False
			))
		))
		ZCIDbg0(ZCI, "Generated ATM related content.", prtLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "type declaration ZCI (DCL_TYP).")
	ZCIDbg0(ZCI, "Type declaration " + newTypeInst.name + " processed.", prtLine=False)
	ZCI.dbgPause()






# -------- DCL_ENM --------

#enumerate declaration
def processEnmDcl(ZCI, scope, tgtFct=None, isPub=False):

	#debug
	scpTxt = ""
	if tgtFct is None:
		scpTxt = ", in global scope"
	else:
		scpTxt = ", in function " + unpfxFctName(ZCI.zCtx, tgtFct)
	ZCIDbg0(ZCI, "Processing enumerate declaration.", prtLine=False)
	jumpBlankZone(ZCI, "Enumerate name in enumerate declaration" + scpTxt + " (DCL_ENM)")

	#get full enm name
	rawName  = readName(ZCI, "Enumerate name in enumerate declaration" + scpTxt + " (DCL_ENM).", dblUnderscores=True)[1]
	fullName = getDatItmModPfxFromScope(ZCI, scope) + rawName

	#must be followed by braces includer
	optionalBlanks(ZCI, "fields inside braces includer in enumerate declaration" + scpTxt + " (DCL_ENM).", blanks=BLANKS_EXTENDED)
	if ZCI.get() != '{':
		ZCIErr(ZCI, "Missing fields inside braces includer in enumerate declaration" + scpTxt + " (DCL_ENM).")

	#read fields
	fields = readDatItmSeq(
		ZCI, "enumerate declaration ZCI" + scpTxt + " (DCL_ENM).",
		scope,
		cstValsOnly          = True,
		allowUnsolvableTypes = True
	)
	for di in fields:
		if di.Type != TYPE_ID__UNKNOWN: #no type must be found (neither explicit type given or initial value)
			ZCIErr(ZCI, "No explicit type or value is allowed in enumerate declaration" + scpTxt + " (DCL_ENM).")

	#set fields
	itmType = setEnmFieldsType(ZCI.zCtx, fields)

	#create custom enm type
	modPfx = ZCI.modPfx
	if len(modPfx) == 0:
		modPfx += 'G'
	mainType_fullName = modPfx + 'N' + rawName
	mainType          = ZCI.zCtx.cpl.newTyp(mainType_fullName, isPub=isPub)
	ZCIDbg0(ZCI, "Creating specific enm type \"" + mainType_fullName + "\".", prtLine=False)

	#copy some info from itm type to the newly created one
	itmTypeInst                   = ZCI.getTypeInstanceFromID(itmType)
	mainTypeInst                  = ZCI.getTypeInstanceFromID(mainType)
	mainTypeInst.dcnCommon.size   = itmTypeInst.dcnCommon.size
	mainTypeInst.dcnCommon.nature = NATURE__ENM
	mainTypeInst.dcnCommon.fields = fields #same fields for the datItm instance & enm type
	mainTypeInst.dcnCommon.parent = itmType

	#create enm <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NO NEED
	#enmDI = datItm(mainType, fullName, True, None, Cst=True, fields=fields, isPub=isPub)
	#checkAlreadyDclDatItmOrField(ZCI, enmDI, scope.datItms)
	#scope.datItms.append(enmDI)

	#end of ZCI expected
	endOfZCI(ZCI, "enumerate declaration" + scpTxt + " (DCL_ENM).")
	ZCIDbg0(ZCI, "Enumerate declaration processed.", prtLine=False)
	ZCI.dbgPause()






# -------- DCL_FWD - DCL_FCT --------

#common parsing
def processFctDcl_partial(ZCI, isPub, fwdTypeName=None):
	parsingFctDcl      = (fwdTypeName is None)
	fwd_srcFctFullName = "" #ret val used only in DCL_FWD



	#STEP 1: METHOD-RELATED STUFF

	#function name: maybe it is type related (method) => try reading a type
	methodType = readType(ZCI, "function name in function declaration/forwarding ZCI (DCL_FCT/DCL_FWD).", errIfNotExisting=False, forbidDcnKwInDcns=False)

	#get method type name
	dcnDep         = False
	dcnKwLst       = None
	methodTypeName = ""
	isMethod       = (methodType != TYPE_ID__UNKNOWN)
	if isMethod:
		methodTypeInst = ZCI.getTypeInstanceFromID(methodType)
		methodTypeName = methodTypeInst.name

		#also, look whether it is dcn-dependant
		for d in methodTypeInst.dcns:
			if d == ZCI.zCtx.gncDcnType:
				dcnDep   = True
				dcnKwLst = ZCI.zCtx.spcDcnTypes #fake operations incomming: do not replace for the moment, but allow the use of "dcn#" in params
				break

		#must be followed by a dot
		if ZCI.get() != '.':
			ZCIErr(ZCI, "Expected a dot '.' after type given in method name.")
		ZCI.inc()

	#forward only methods
	elif not parsingFctDcl:
		ZCIErr(ZCI, "Can only forward methods (DCL_FWD).")



	#STEP 2: MOD PFX, NAME, IS OPERATOR

	#read function name
	modPfx, rawName = readName(ZCI, "function name in function declaration/forwarding ZCI (DCL_FCT/DCL_FWD).",
		parseModPfxes = True,
		whitelist     = FCT_NAME_CHARSET
	)

	#out-of-mod
	if modPfx == "G":
		isOpe = (rawName in OPERATOR_FCTNAME2SYMBOL.keys()) #out-of-mod => can be an operator

	#in mod
	else:
		if parsingFctDcl:
			ZCIErr(ZCI, "Function declaration name does not allow module prefixes (DCL_FCT).")
		isOpe  = False #out-of-mod => can't be an operator



	#STEP 3: PARAMS

	#must be followed by parameters between parentheses includer
	if ZCI.get() != '(':
		ZCIErr(ZCI, "Expected parameters between parentheses includer right after function name (DCL_FCT/DCL_FWD).")

	#parameters
	params = readDatItmSeq(
		ZCI, "function declaration/forwarding ZCI (DCL_FCT/DCL_FWD)",
		ZCI.zCtx.cpl.gblScp,
		cstValsOnly              = True,
		allowEmpty               = True,
		dcnKwLstToReplaceInTypes = dcnKwLst #only effective if fct is dcn-dependent, and btw, it doesn't replace anything for the moment but only ALLOW 'dcn#' notations
	)
	for p in params: #add "lcl" module prefix
		if isMethod and p.name == "sbj":
			ZCIErr(ZCI, "Can't use name \"sbj\" as parameter in method, already in use for targetting current instance (DCL_FCT/DCL_FWD).")
		p.name = 'L' + p.name

	#method instance as 1st param: "sbj"
	if isMethod:
		params = [datItm(methodType, "Lsbj", False, None)] + params

	#go to the next interesting thing (if any)
	optionalBlanks(ZCI, None)



	#STEP 4: CHECK & BUILD FCT EXACT NAME

	#case 1: operator
	if isOpe:
		if isMethod:
			ZCIErr(ZCI, "Operator functions cannot be used as methods for a given type (type " + methodTypeName + " targetted for operator " + OPE_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]] + ", DCL_FCT/DCL_FWD).")

		#build full fct name
		fullName = 'O' + OPE_NAMES[OPERATOR_FCTNAME2SYMBOL[rawName]]
		for p in params:
			fullName += '_' + ZCI.getTypeNameFromID(p.Type)

	#case 2: regular fct/method
	else:
		for c in rawName:
			if c not in DEFAULT_NAME_CHARSET: #regular charset as for any datItm (must be callable the same way)
				ZCIErr(ZCI, "Invalid character \'" + c + "\' in function name (DCL_FCT/DCL_FWD).")

		#method only
		methodHeader = "F"
		if isMethod:
			if parsingFctDcl:
				methodHeader       = 'T' + methodTypeName + "_F"
			else:
				methodHeader       = 'T' + fwdTypeName + "_F"
				fwd_srcFctFullName = modPfx + 'T' + methodTypeName + "_F" + rawName #also build fwd src fct name (DCL_FWD only)

				#additionnal check for fwd fct: forward with same type
				if methodTypeName == fwdTypeName:
					ZCIErr(ZCI, "Can't forward using the same type for both source and destination (" + methodTypeName + ", DCL_FWD).")

		#additionnal check for gbl fct: GUARANTEE NO CONFUSION BETWEEN GBL DI NAMES & FCT NAMES
		else:
			equivalentGDIName = ZCI.modPfx + 'E' + rawName
			for gdi in ZCI.zCtx.cpl.gblScp.datItms:
				if gdi.name == equivalentGDIName:
					ZCIErr(ZCI, "Unable to declare function \"" + unpfxMod(ZCI.modPfx) + rawName + "\" because a global data item with the same name already exist (avoid confusion, DCL_FCT).")

		#build full fct name
		if len(ZCI.modPfx) == 0:
			ZCI.modPfx = 'G' #overwrite ZCI info, doesn't matter here, this ZCI will no longer be parsed
		fullName = ZCI.modPfx + methodHeader + rawName



	#STEP 6: CREATE INSTANCE

	#check if function/method/operator already exists
	if getFctFromName(ZCI, fullName) is not None:
		ZCIErr(ZCI,
			"Available functions/methods/operators declared since now " + listAllExistingFct(ZCI.zCtx) + \
			"\nAlready have a function/method/operator with name " + fullName
		)

	#create fct instance (set VOID retType for the moment)
	f        = newFct(fullName, TYPE_ID__UNKNOWN, params, ZCI.zCtx.cpl.gblScp, methodOf=methodType)
	f.isPub  = isPub
	f.dcnDep = dcnDep
	ZCI.zCtx.cpl.fcts.append(f)

	#add params as available data items in fct scope
	for p in params:
		f.scope.datItms.append(p)

	#return src fct full name (makes sens only in DCL_FWD)
	return fwd_srcFctFullName




#function declaration
def processFctDcl(ZCI, isPub):
	ZCIDbg0(ZCI, "Processing function declaration.", prtSubCtxs=True)

	#parse until after params
	processFctDcl_partial(ZCI, isPub)
	f = ZCI.zCtx.cpl.fcts[-1]

	#return type explicitly given => non-VOID
	retType = TYPE_ID__UNKNOWN
	if ZCI.get() != '{':
		dcnKwLst = None
		if f.dcnDep:
			dcnKwLst = ZCI.zCtx.spcDcnTypes #fake operation: do not replace for the moment, but allow the use of "dcn#" in retType
		retType = readType(ZCI, "return type in function declaration ZCI (DCL_FCT)", dcnKwLstToReplace=dcnKwLst)

		#move to function content
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
		if ZCI.get() != '{':
			ZCIErr(ZCI, "Expected to have function content after return type given (braces includer).")
	ZCIDbg1(ZCI, "Return type detected \"" + ZCI.getTypeNameFromID(retType) + "\".")

	#content
	ZCIDbg1(ZCI, "Extracting function \"" + f.name + "\"'s content.")
	content = extractZCIsFromCtx(
		ZCI.zCtx,
		ZCI.ctx, subCtxs=ZCI.subCtxs,
		gbl     = False,
		modPfx  = ZCI.modPfx,
		wallIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
	)
	ZCIDbg1(ZCI, "End of extraction for function \"" + f.name + "\".")

	#complete fct info
	f.retType = retType
	f.content = content
	ZCIDbg1(ZCI, "Added to cpl data as: " + f.toStr(), prtSubCtxs=False, prtLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "function declaration ZCI (DCL_FCT).")
	ZCIDbg0(ZCI, "Function declaration processed.", prtLine=False)
	ZCI.dbgPause()



#function forwarding declaration
def processFwdDcl(ZCI, isPub):
	ZCIDbg0(ZCI, "Processing function forwarding declaration.", prtSubCtxs=True)

	#get type to forward
	fwdType     = readType(ZCI, "type to forward into, in function forwarding ZCI (DCL_FWD).", forbidDcnKwInDcns=False)
	fwdTypeName = ZCI.getTypeNameFromID(fwdType)
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

	#parse until after params
	srcFctFullName = processFctDcl_partial(ZCI, isPub, fwdType=fwdTypeName)
	dstF           = ZCI.zCtx.cpl.fcts[-1]

	#look for src fct
	srcF = getFctFromName(ZCI, srcFctFullName)
	if srcF is None:
		ZCIErr(ZCI, "Unable to find source function \"" + srcFctFullName + "\" to forward from (DCL_FWD).")

	#return type explicitly given => non-VOID
	retType = TYPE_ID__UNKNOWN
	if not ZCI.reachedEnd():
		dcnKwLst = None
		if f.dcnDep:
			dcnKwLst = ZCI.zCtx.spcDcnTypes #fake operation: do not replace for the moment, but allow the use of "dcn#" in retType
		retType = readType(ZCI, "return type in function forwarding ZCI (DCL_FWD)", dcnKwLstToReplace=dcnKwLst)

		#move to the very end
		optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
	ZCIDbg1(ZCI, "Return type detected \"" + ZCI.getTypeNameFromID(retType) + "\".")

	#requirement 1: must have the same exact parameters, except the 1st one (number, names, types)
	paramVals = []
	if len(dstF.params) != len(srcF.params):
		ZCIErr(ZCI, "Can only forward functions with exact same number of parameters (expected " + str(len(srcF.params)) + ", got " + str(len(dstF.params)) + ", in DCL_FWD).")
	for p in range(len(srcF.params)):
		if p != 0:

			#error cases
			if dstF.params[p].name != srcF.params[p].name:
				ZCIErr(ZCI, "Can only forward functions with same parameters names (expected \"" + srcF.params[p].name + "\" as parameter " + str(p+1) + ", got \"" + dstF.params[p].name + "\", in DCL_FWD).")
				typeSizesMustMatch(ZCI, ", in function forwarding (DCL_FWD).", dstF.params[p].Type, srcF.params[p].Type)

		#add param values
		paramVals.append(
			val(dstF.retType, atm(ATM__DATITM, dstF.params[p]), dstF.params[p].Cst)
		)

	#requirement 2: must ret void if src ret void
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
	ZCIDbg1(ZCI, "Added to cpl data as: " + dstF.toStr(), prtSubCtxs=False, prtLine=False)

	#end of ZCI expected
	endOfZCI(ZCI, "function forwarding ZCI (DCL_FWD).")
	ZCIDbg0(ZCI, "Function forwarding processed.", prtLine=False)
	ZCI.dbgPause()






# -------- REMAINING ZCIs: VFC_VFC, ASG_ASG, DCL_DAT --------

#data item assignment only (assigning to existing destination) WARNING: ZCI must be RIGHT BEFORE SRC VALUE !
def processAsg(ZCI, scope, tgtFct, dstVal):

	#debug
	scpTxt  = ""
	cstOnly = False
	if tgtFct is None:
		scpTxt  = ", in global scope"
		cstOnly = True
	else:
		scpTxt = ", in function " + unpfxFctName(ZCI.zCtx, tgtFct)
	ZCIDbg0(ZCI, "Processing data item assignment" + scpTxt + " (ASG_ASG).", prtLine=False)

	#read src value to be assigned
	srcVal = readVal(ZCI, "source value in assignment" + scpTxt + " (ASG_ASG).", scope, cstOnly=cstOnly)

	#datItm does not exist yet => also dcl it
	if dstVal.vdat.id == ATM__DATITM:
		if not alreadyDclDatItmOrField(dstVal.vdat.dat, scope.datItms):
			ZCIDbg0(ZCI, "Also dcl dat itm \"" + dstVal.vdat.dat.name + "\", it did not exist in cur scope yet (ASG_ASG).", prtLine=False)
			scope.datItms.append(dstVal.vdat.dat)

	#something else than datItm val
	else:

		#ffa chain can be accepted if targettable
		deepestVal = None
		if dstVal.vdat.id == ATM__FFA:
			deepestVal = dstVal.vdat.dat.value
			while deepestVal.vdat.id == ATM__FFA:
				deepestVal = deepestVal.vdat.dat

		#accessing a field from a non-datItm => can't write into it
		if deepestVal is None:
			ZCIErr(ZCI, "Invalid destination " + dstVal.toStr() + "\nto assign value " + scpTxt + " (Expected a data item based value, ASG_ASG).")

	#add execution to concerned scope
	scope.exes.append( atm(ATM__ASG, asg(dstVal, srcVal)) )

	#end of ZCI expected
	endOfZCI(ZCI, "data item assignment" + scpTxt + " (ASG_ASG).")
	ZCIDbg0(ZCI, "Data item assignment processed.", prtLine=False)
	ZCI.dbgPause()



#data item declaration (including assignment with initial value)
def processDclDat(ZCI, scope, tgtFct, isCst, isPub=False):

	#debug
	scpTxt         = ""
	cstInitValOnly = False
	if tgtFct is None:
		scpTxt         = ", in global scope"
		cstInitValOnly = True
	else:
		scpTxt = ", in function " + unpfxFctName(ZCI.zCtx, tgtFct)
	ZCIDbg0(ZCI, "Processing data item declaration" + scpTxt + " (DCL_DAT).", prtLine=False)

	#read the whole ZCI from the start
	di = readDatItm(ZCI, "data item declaration" + scpTxt + " (DCL_DAT).", scope, cstInitValOnly=cstInitValOnly, allowModPfxInName=False)

	#set some important info to the NEWLY CREATED data item
	di.name  = getDatItmModPfxFromScope(ZCI, scope) + di.name
	di.Cst   = isCst
	di.isPub = isPub

	#add declaration to scope
	checkAlreadyDclDatItmOrField(ZCI, di, scope.datItms) #check already existing
	scope.datItms.append(di)

	#init val given => remove it and create asg at current position instead, VERY IMPORTANT !!!
	if di.inited:
		di.inited = False
		scope.exes.append(
			atm(ATM__ASG, asg(
				val(di.Type, atm(ATM__DATITM, di), False),
				di.initVal
			))
		)
		di.initVal = None

	#end of ZCI expected
	endOfZCI(ZCI, "data item declaration" + scpTxt + " (DCL_DAT).")
	ZCIDbg0(ZCI, "Data item declaration processed.", prtLine=False)
	ZCI.dbgPause()



#concerns more step 3 actually
def processVFC(ZCI, scope, tgtFct, v):

	#debug
	scpTxt = ""
	if tgtFct is None:
		scpTxt = ", in global scope"
	else:
		scpTxt = ", in function " + unpfxFctName(ZCI.zCtx, tgtFct)
	ZCIDbg0(ZCI, "Processing void returning function call" + scpTxt + " (VFC_VFC).", prtLine=False)

	#local scope only
	if tgtFct is None:
		ZCIErr(ZCI, "Detected void returning function call in global scope but this is only allowed in local scope (VFC_VFC).")

	#call => OK, add it to scope
	if v.vdat.id == ATM__CALL:
		# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< DISABLED FFA CALLS, RELY ON C COMPILER
		#if v.vdat.dat.name.startswith("ffa_get_") or v.vdat.dat.name.startswith("frf"): #these are not real fcts, makes no sens to call them as VFC
		#	ZCIErr(ZCI, "Invalid ZCS, unknown ZCI given" + scpTxt + " (Expected function call, VFC_VFC).")
		scope.exes.append(v.vdat)

	#other => unknown ZCI
	else:
		ZCIErr(ZCI, "Invalid ZCS, unknown ZCI given" + scpTxt + " (Expected function call, VFC_VFC).")

	#end of ZCI expected
	endOfZCI(ZCI, "void returning function call" + scpTxt + " (VFC_VFC).")
	ZCIDbg0(ZCI, "Void returning function call processed.", prtLine=False)
	ZCI.dbgPause()



#remaining ZCIs can be DCL_DAT, ASG_ASG or VFC_VFC (the last one only allowed in local scope)
def processRemainingZCI(ZCI, scope, tgtFct=None, isPub=False):

	#debug
	scpTxt = ""
	if tgtFct is None:
		scpTxt = ", in global scope"
	else:
		scpTxt = ", in function " + unpfxFctName(ZCI.zCtx, tgtFct)
	ZCIDbg0(ZCI, "Processing remaining ZCI, can be VFC_VFC / ASG_ASG / DCL_DAT.", prtLine=True)

	#read beginning of ZCI as a value
	dcnKwLstToReplace = None
	if tgtFct is not None:
		dcnKwLstToReplace = tgtFct.dcnKwLstToReplace
	v = readVal(ZCI, None, scope, allowVFC=True, dcnKwLstToReplace=dcnKwLstToReplace)

	#does not start with a value-like pattern => can only be a DCL_DAT with explicit type given
	if v is None:
		processDclDat(ZCI, scope, tgtFct, False, isPub=isPub)
		return

	#no asg symbol following => VFC
	optionalBlanks(ZCI, None)
	if readSym(ZCI) != SYM__ASG:
		processVFC(ZCI, scope, tgtFct, v)
		return

	#else, ASG_ASG, forward after symbol & parse the rest
	ZCI.forward(SYM_LENGTHS[SYM__ASG])
	optionalBlanks(ZCI, None)
	processAsg(ZCI, scope, tgtFct, v)






# -------- EXECUTION --------

#compilation
def c02_redirectGbl(zCtx):
	zCtx.updateLogLvl(STEP.C02)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("======================== C02 REDIRECT GLOBAL : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#before loading any gbl ZCI, load lit str saved at step P1
	for i in range(zCtx.pcpl.litStrIdx+1):
		hs = zCtx.pcpl.litStr[i] #hex str (2 hex chr per chr)

		#transform lit str as raw val
		seq = [] #lst[val]
		for c in range(int(len(hs)/2)):
			seq.append(val(
				zCtx.rootTypes[RT__S8],
				atm(ATM__S8, hex_toS8(hs[2*c], hs[2*c+1]) ),
				True
			))

		#add datItm dcl
		di = datItm(zCtx.rawType, "GE__" + str(i), True, val(
			zCtx.rawType,
			atm(ATM__LST_VAL, seq),
			True
		))
		zCtx.cpl.gblScp.datItms.append(di)

	#manually set resource access
	manualAccess_set   = False
	manualAccess_isPub = False

	#analyse every global ZCI
	z = -1
	while z < len(zCtx.ZCIs)-1:
		z         += 1
		ZCI        = zCtx.ZCIs[z]
		initialCtx = ZCI.ctx.copy()
		ZCIDbg1(ZCI, "Treating global ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=True)

		#reset cur access state for each ZCI
		isPub = zCtx.pubByDefault

		#read 1st ZCI word
		firstWord = readName(ZCI, "Invalid ZCS: Unknown ZCI.", blacklist=ZCI_FIRSTWORD_DETECTION_BLACKLIST)[1]



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
				ZCIInt(ZCI, "Must not have any importation remaining at that step.")



			#CASE 2 - BEGINNING WITH KEYWORD AND ALLOWED

			#trigrams requiring a following blank
			if ZCI.txt[3] in BLANKS:

				#public kw (combinable behavior)
				if str_cmp("pub", firstWord):
					if manualAccess_set:
						ZCIErr(ZCI, "Already have an access modifier set for this ZCI.")

					#manual access modifier
					optionalBlanks(ZCI, "Missing something after \"pub\" keyword (empty ZCI instead).")
					manualAccess_set   = True
					manualAccess_isPub = True
					z -= 1
					continue

				#private kw (combinable behavior)
				if str_cmp("prv", firstWord):
					if manualAccess_set:
						ZCIErr(ZCI, "Already have an access modifier set for this ZCI.")

					#manual access modifier
					optionalBlanks(ZCI, "Missing something after \"prv\" keyword (empty ZCI instead).")
					manualAccess_set   = True
					manualAccess_isPub = False
					z -= 1
					continue

				#2.1 - library linking
				if str_cmp("lnk", firstWord):
					if manualAccess_set:
						ZCIErr(ZCI, "Doesn't make sens to set public/private access to library link.")
					processLnk(ZCI)
					continue

				#2.2 - type declaration DCL_TYP
				if str_cmp("typ", firstWord):
					if manualAccess_set:
						isPub            = manualAccess_isPub
						manualAccess_set = False
					processTypeDcl(ZCI, isPub)
					continue

				#2.3 - Enumerate declaration DCL_ENM
				if str_cmp("enm", firstWord):
					if manualAccess_set:
						isPub            = manualAccess_isPub
						manualAccess_set = False
					processEnmDcl(ZCI, ZCI.zCtx.cpl.gblScp, isPub=isPub)
					continue

				#2.4 - Function declaration
				if str_cmp("fct", firstWord):
					jumpBlankZone(ZCI, "Function name in function declaration ZCI (DCL_FCT).") #forward to function name directly
					if manualAccess_set:
						isPub            = manualAccess_isPub
						manualAccess_set = False
					processFctDcl(ZCI, isPub)
					continue

				#2.5 - Function forwarding
				if str_cmp("fwd", firstWord):
					jumpBlankZone(ZCI, "Type to forward into, in function forwarding ZCI (DCL_FWD).") #forward to function name directly
					if manualAccess_set:
						isPub            = manualAccess_isPub
						manualAccess_set = False
					processFwdDcl(ZCI, isPub)
					continue

				#2.6 - Constant data item declaration
				if str_cmp("cst", firstWord):
					jumpBlankZone(ZCI, "Constant keyword in data item declaration ZCI (DCL_DAT).")
					if manualAccess_set:
						isPub            = manualAccess_isPub
						manualAccess_set = False
					processDclDat(ZCI, zCtx.cpl.gblScp, None, True, isPub=isPub)
					continue



		#CASE 4 - ANYTHING ELSE (can be only global DCL_DAT or global ASG_ASG)

		#reset ZCI at initial state & try parsing it, no other possibility for a global ZCI
		ZCI.resetCtx(initialCtx)
		if manualAccess_set:
			isPub            = manualAccess_isPub
			manualAccess_set = False
		processRemainingZCI(ZCI, zCtx.cpl.gblScp, isPub=isPub)

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================== C02 REDIRECT GLOBAL : end ========================")
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
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c02.dl", output)
