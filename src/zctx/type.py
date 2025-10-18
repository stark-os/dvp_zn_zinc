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

	def listTypeNames(sbj):
		typeNames = []
		for t in sbj.cpl.types:
			n = unpfxTypeName(sbj, t.name)[0]
			typeNames.append(n)

		#pretty display
		return strLst_toDsp(typeNames)



#type fields
def getTypeFieldFromName(ZCI, tgtTypeID, tgtFieldName):
	tInst = ZCI.zCtx.getTypeInstanceFromID(tgtTypeID)

	#type nature check
	if tInst.dcnCommon.nature == NATURE__PRM:
		ZCIErr(ZCI, "Type " + unpfxMod(tInst.name) + " is a primitive type, cannot get fields from it.")

	#look for the given name in type fields
	for f in tInst.dcnCommon.fields:
		if f.name == tgtFieldName:
			return f
	ZCIErr(ZCI, "Type " + unpfxMod(tInst.name) + " has no field \"" + tgtFieldName + "\".")
