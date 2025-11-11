# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/fct.py

# -------- FUNCTIONS & METHODS RELATED TOOLS --------

#get fct name
def zCtx__getFctFromName(zCtx, exactName):
	for f in zCtx.cpl.fcts:
		if exactName == f.name:
			return f
	return None

def getFctFromName(ZCI, exactName):
	return zCtx__getFctFromName(ZCI.zCtx, exactName)

def zCtx__listAllDcnsNameCombinations(sbj, typ_inst):

	#get type name without dcns (don't care about typ_modPfx, we keep it at the beginning of that "rawName")
	typ_rawName = cutDcnFromTypeName(typ_inst.name)

	#get alternatives for each dcn individually
	dcnIndividualAlternatives = []
	for d in typ_inst.dcns:
		alts = sbj.getTypeAlternativeNames(d)
		alts.append(sbj.gncDcnType)
		dcnIndividualAlternatives.append(alts)

	#get every combination together
	dcnCollectiveCombinations = Combinations__makeAll(dcnIndividualAlternatives)

	#constitue possible names
	dcnsNames = []
	for combination in dcnCollectiveCombinations:
		sfx = ""
		for d in range(len(typ_inst.dcns)):
			sfx += '_' + combination[d]

		#add complete name (look like ["_GUbyt_GUflt_GUint", "_GUs8_GUflt_GUint", "_GUs8_GUf32_GUint"...])
		dcnsNames.append(sfx)
	return dcnsNames

#reaaaaaaaaaaaally useful too !!! Does 3 things together !
def checkAll_thenReadParams_thenCreateCall(ZCI,
	allowVFC,  ZCIKindIfErr,
	fctModPfx, fctRawName,
	scope,     cstOnly,
	dcnKwLstToReplace,
	methodCaller = None #val
):
	#check scope: calls are only allowed in non-global scope
	if scope == ZCI.zCtx.cpl.gblScp:
		ZCIErr(ZCI, "Calls are not allowed in global scope in " + ZCIKindIfErr)

	#sub-err indication
	ZCIKindIfErr_ending = "."
	if ZCIKindIfErr is not None:
		ZCIKindIfErr_ending = ", in " + ZCIKindIfErr

	#method related
	isMethod       = (methodCaller is not None)
	methodTypeInst = None
	methodHeader   = "F"
	if isMethod:
		methodTypeInst = ZCI.getTypeInstanceFromID(methodCaller.Type)
		methodHeader   = 'T' + methodTypeInst.name + "_F"

	#try get function matching exact name
	fctExactName = fctModPfx + methodHeader + fctRawName
	tgtFct       = getFctFromName(ZCI, fctExactName)
	ZCIDeepDbg(ZCI, "Trying to find matching fct call with exact name \"" + fctExactName + "\".")

	#no exact match
	if tgtFct is None:
		for f in ZCI.zCtx.cpl.fcts:
			print("["+f.name+"]")

		#not a method => no other alternative
		if not isMethod:
			ZCIWrn(ZCI, "You may wanted to target one of the following functions declared: " + listAllExistingFct(ZCI.zCtx), prtSubCtxs=False, prtLine=False)
			ZCIErr(ZCI, "No matching function \"" + unpfxMod(fctModPfx) + fctRawName + "\" found (parsing call)" + ZCIKindIfErr_ending)
		ZCIDeepDbg(ZCI, "No matching function with that exact name but this is a method call => trying alternatives.", prtLine=False)

		#get some info about tgt method type
		methodTypeName_alternatives = ZCI.zCtx.getTypeAlternativeNames(methodCaller.Type)
		fctExactName_alternatives   = []

		#at least one dcn in type => gather every combination, including with "dcn" kw (dcn-dep methods)
		dcnsCombinations = []
		if len(methodTypeInst.dcns) != 0:
			dcnsCombinations += zCtx__listAllDcnsNameCombinations(ZCI.zCtx, methodTypeInst)

		#look in parents for a match
		for parentAltName in methodTypeName_alternatives:

			#declinated parent can match
			for dc in dcnsCombinations:
				fctExactName_alternatives.append(fctModPfx + 'T' + parentAltName + dc + "_F" + fctRawName)

			#undcn parent can also match
			fctExactName_alternatives.append(fctModPfx + 'T' + parentAltName + "_F" + fctRawName)

		#check each alternative for tgtFct
		ZCIDeepDbg(ZCI, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ALTERNATIVES " + strLst_toDsp(fctExactName_alternatives), prtLine=False)
		for altExactName in fctExactName_alternatives:
			ZCIDeepDbg(ZCI, "Trying with \"" + altExactName + "\".", prtLine=False)

			#retry with this one
			tgtFct = getFctFromName(ZCI, altExactName)
			if tgtFct is not None:
				fctExactName = altExactName #its a match !
				break

		#still no one matching
		if tgtFct is None:
			ZCIWrn(ZCI, "The following methods could have match if they were declared: " + strLst_toDsp(fctExactName_alternatives), prtSubCtxs=False, prtLine=False)
			ZCIErr(ZCI, "No matching method \"" + fctExactName + "\" found for type " + unpfxTypeName(ZCI.zCtx, methodTypeInst.name)[0] + " (parsing call)" + ZCIKindIfErr_ending)

	#match (debug)
	ZCIDeepDbg(ZCI, "Found matching method \"" + fctExactName + "\".", prtLine=False)

	#check ret type
	if not allowVFC and tgtFct.retType == TYPE_ID__UNKNOWN:
		ZCIErr(ZCI, "Can't have void returning function call here (only !VFC allowed)" + ZCIKindIfErr_ending)

	#collect params info
	unpfxParams = []
	for p in range(len(tgtFct.params)):
		if p != 0 or not isMethod:
			pDI = tgtFct.params[p]
			unpfxParams.append(datItm( pDI.Type, pDI.name[1:], pDI.inited, pDI.initVal )) #copy params but without 'L' pfx

	#read param vals
	paramVals_fmap = readValSeq(ZCI,
		ZCIKindIfErr,
		unpfxParams,
		scope,
		cstOnly           = cstOnly,
		dcnKwLstToReplace = dcnKwLstToReplace
	)

	#set under lst[val] for call format
	paramVals_valLst = []
	if isMethod:
		paramVals_valLst.append(methodCaller) #add "sbj" in param vals
	for p in unpfxParams:
		paramVals_valLst.append(paramVals_fmap[p.name]) #ensure to add each param in the correct order !

	#create call
	return call(fctExactName, paramVals_valLst, tgtFct.retType)

def listAllExistingFct(zCtx):
	nl = []
	for f in zCtx.cpl.fcts:
		nl.append(unpfxFctName(zCtx, f))
	return strLst_toDsp(nl)
