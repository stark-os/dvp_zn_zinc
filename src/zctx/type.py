# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/type.py

	# ---------------- TYPES RELATED TOOLS ----------------

	#access using zCtx
	def getTypeInstanceFromID(sbj, id):
		if id >= 0 and id < len(sbj.cpl.types):
			return sbj.cpl.types[id]
		return None

	def getTypeIDFromName(sbj, name):
		for t in range(len(sbj.cpl.types)):
			if sbj.cpl.types[t].name == name:
				return t
		return TYPE_ID__UNKNOWN

	def getTypeNameFromID(sbj, id):
		i = sbj.getTypeInstanceFromID(id)
		if i is None:
			return "<void>"
		return i.name

	def getTypeInstanceFromName(sbj, name):
		for t in range(len(sbj.cpl.types)):
			if sbj.cpl.types[t].name == name:
				return sbj.cpl.types[t]
		return None



	#check something in declinations
	def checkIDRecursivelyInType(sbj, tID, tgtID):
		if tID == tgtID:
			return True
		dcns = sbj.getTypeInstanceFromID(tID).dcns
		if dcns is not None:
			for d in dcns:
				if sbj.checkIDRecursivelyInType(d, tgtID):
					return True
		return False



	#inheritance !WARNING: A bit of complexity !!!
	def getTypeAlternatives(sbj, tgtType):
		alternatives = [tgtType]
		tInst        = sbj.getTypeInstanceFromID(tgtType)

		#step 1: get individual combinations for each declination
		dcnIndividualCombinations = []
		for dcn in tInst.dcns:
			dcnIndividualCombinations.append( sbj.getTypeAlternatives(dcn) )

		#step 2: combine them together <---------------- !WARNING: Pretty complex stuff here !
		dcnCollectiveCombinations = Combinations__makeAll(dcnIndividualCombinations)

		#step 3: cut declinations from name (here, we keep the starting 'D'/'U' in rawName)
		exactNameWithoutDcns = undblUnderscores(
			cutDcnFromTypeName( sbj.getTypeNameFromID(tgtType) )
		)

		#step 4: gather dcn-related alternatives
		for combination in dcnCollectiveCombinations:
			sfx = ""
			for d in range(len(tInst.dcns)):
				sfx += '_' + sbj.getTypeNameFromID(combination[d])

			#add this dcn-related alternative as ID
			alternatives.append( sbj.getTypeIDFromName(exactNameWithoutDcns + sfx) )

		#step 5: add also parent's alternatives
		if tInst.dcnCommon.parent is not None:
			alternatives += sbj.getTypeAlternatives(tInst.dcnCommon.parent)
		return alternatives

	def getTypeAlternativeNames(sbj, tgtType):
		altIDs   = sbj.getTypeAlternatives(tgtType)
		altNames = []
		for i in altIDs:
			altNames.append(sbj.getTypeNameFromID(i))
		return altNames

	def typeIDContainsDcnKw(sbj, tID):
		return tID in sbj.spcDcnTypes or tID == sbj.gncDcnType

	def listTypeNames(sbj):
		typeNames = []
		skip      = False
		for tID in range(len(sbj.cpl.types)):
			tInst = sbj.cpl.types[tID]

			#skip dcn kw (either is or contain in dcns)
			if sbj.typeIDContainsDcnKw(tID):
				skip = True
			else:
				for d in tInst.dcns:
					if sbj.typeIDContainsDcnKw(d):
						skip = True
						break

			#skip mechanism
			if skip:
				skip = False
				continue

			#add name: enm
			n = ""
			if tInst.name[2] == 'N':
				n += "(enm) "
			n += unpfxTypeName(sbj, tInst.name)[0]
			typeNames.append(n)

		#pretty display
		return strLst_toDsp(typeNames)



#type fields
def getTypeFieldFromName(ZCI, tgtTypeID, tgtFieldName):
	tInst = ZCI.zCtx.getTypeInstanceFromID(tgtTypeID)

	#type nature check
	if tInst.dcnCommon.nature == NATURE__PRM:
		ZCIErr(ZCI, "Type " + unpfxTypeName(ZCI.zCtx, tInst.name)[0] + " is a primitive type, cannot get fields from it.")

	#look for the given name in type fields
	for f in tInst.dcnCommon.fields:
		if f.name == tgtFieldName:
			return f
	ZCIErr(ZCI, "Type " + unpfxTypeName(ZCI.zCtx, tInst.name)[0] + " has no field \"" + tgtFieldName + "\".")



#get / create specific declination for a given type
def getOrCreateSpcTypeDcn(ZCI, ZCIKindIfErr_ending, tUndecInst, dcns):

	#get modPfx & rawName
	tModPfx  = ""
	tRawName = ""
	if tUndecInst.name[0] == 'G':
		tModPfx  = "G"
		tRawName = tUndecInst.name[2:]
	else:
		tModPfx  = unpfxMod(tUndecInst.name)
		tRawName = str_sub(tUndecInst.name, start=len(tModPfx)+1)

	#one dcn does not exist => can't make it
	for d in dcns:
		if d == TYPE_ID__UNKNOWN:
			return TYPE_ID__UNKNOWN

	#check declination length
	if len(dcns) < tUndecInst.dcnCommon.dcnDeg:
		ZCIErr(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.dcnCommon.dcnDeg) + " required)" + ZCIKindIfErr_ending)
	elif len(dcns) > tUndecInst.dcnCommon.dcnDeg:
		ZCIErr(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.dcnCommon.dcnDeg) + " required)" + ZCIKindIfErr_ending)

	#re-build full type name including declinations this time (tModulePfx can be set to "G" by the way, same logic as undeclinated types)
	tDecFullName = tModPfx + 'D' + tRawName
	for d in dcns:
		tDecFullName += '_' + ZCI.getTypeNameFromID(d)

	#check for that declination in currently declared types
	existingID = ZCI.getTypeIDFromName(tDecFullName)

	#not found => create that declination (this new combination must exist)
	if existingID == TYPE_ID__UNKNOWN:
		newID         = ZCI.zCtx.cpl.newTyp(tDecFullName, dcnCommon=tUndecInst.dcnCommon) #share the same dcnCommon (affecting the undeclinated instance will affect every declination)
		tDecInst      = ZCI.getTypeInstanceFromID(newID)
		tDecInst.dcns = dcns
		ZCIDbg(ZCI, "First call of declination \"" + tDecFullName + "\" from type \"" + tUndecInst.name + "\", adding it.")
		return newID

	#found => just use it
	return existingID
