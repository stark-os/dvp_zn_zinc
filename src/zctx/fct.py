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
	methodOf = TYPE_ID__UNKNOWN
):
	#check scope: calls are only allowed in non-global scope
	if scope == ZCI.zCtx.cpl.gblScp:
		ZCIErr(ZCI, "Calls are not allowed in global scope in " + ZCIKindIfErr)

	#sub-err indication
	ZCIKindIfErr_ending = "."
	if ZCIKindIfErr is not None:
		ZCIKindIfErr_ending = ", in " + ZCIKindIfErr

	#method related
	isMethod       = (methodOf != TYPE_ID__UNKNOWN)
	methodTypeInst = None
	methodHeader   = "F"
	if isMethod:
		methodTypeInst = ZCI.getTypeInstanceFromID(methodOf)
		methodHeader   = 'T' + methodTypeInst.name + '_'

	#try get function matching exact name
	fctExactName = fctModPfx + methodHeader + fctRawName
	tgtFct       = getFctFromName(ZCI, fctExactName)
	ZCIDeepDbg(ZCI, "Trying to find matching fct call with exact name \"" + fctExactName + "\".")

	#no exact match
	if tgtFct is None:

		#not a method => no other alternative
		if not isMethod:
			ZCIErr(ZCI, "No matching function \"" + unpfxMod(fctModPfx) + fctRawName + "\" found (parsing call)" + ZCIKindIfErr_ending)
		ZCIDeepDbg(ZCI, "No matching function with that exact name but this is a method call => trying alternatives.", prtLine=False)

		#get some info about tgt method type
		methodTypeName_alternatives = ZCI.zCtx.getTypeAlternativeNames(methodOf)
		fctExactName_alternatives   = []

		#at least one dcn in type => gather every combination, including with "dcn" kw (dcn-dep methods)
		dcnsCombinations = []
		if len(methodTypeInst.dcnCommon.dcns) != 0:
			dcnsCombinations += zCtx__listAllDcnsNameCombinations(methodTypeInst)

		#look in parents for a match
		for parentAltName in methodTypeName_alternatives:

			#declinated parent can match
			for dc in dcnsCombinations:
				fctExactName_alternatives = fctModPfx + 'T' + parentAltName + dc + '_' + fctRawName

			#undcn parent can also match
			fctExactName_alternatives = fctModPfx + 'T' + parentAltName + '_' + fctRawName

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
			ZCIErr(ZCI, "No matching method \"" + fctExactName + "\" found for type " + unpfxTypeName(ZCI.zCtx, tInst.name) + " (parsing call)" + ZCIKindIfErr_ending)
		ZCIDeepDbg(ZCI, "Found matching method \"" + fctExactName + "\".", prtLine=False)

	#check ret type
	if not allowVFC and tgtFct.retType == TYPE_ID__UNKNOWN:
		ZCIErr(ZCI, "Can't have void returning function call here (only !VFC allowed)" + ZCIKindIfErr_ending)

	#read params
	unpfxParams = []
	for p in tgtFct.params:
		unpfxParams.append(datItm( p.Type, p.name[1:], p.inited, p.initVal )) #copy params but without 'L' pfx
	paramVals_fmap = readValSeq(ZCI,
		ZCIKindIfErr,
		unpfxParams,
		scope,
		cstOnly           = cstOnly,
		dcnKwLstToReplace = dcnKwLstToReplace
	)
	ZCI.inc()

	#set under lst[val] for call format
	paramVals_valLst = []
	for p in unpfxParams:
		paramVals_valLst.append(paramVals_fmap[p.name]) #ensure to add each param in the correct order !

	#create call
	return call(fctExactName, paramVals_valLst, tgtFct.retType)

def listAllExistingFct(zCtx):
	nl = []
	for f in zCtx.cpl.fcts:
		nl.append(f.name)
	return strLst_toDsp(nl)
