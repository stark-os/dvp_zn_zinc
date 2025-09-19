# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/type.py

# -------- TYPE RELATED TOOLS --------

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



	#operator matching !WARNING: High complexity !!!
	def getTypeMatchingAlternativeNames(sbj, tgtTypeName):
		alternatives = [tgtTypeName]
		tInst        = sbj.getTypeInstanceFromName(tgtTypeName)

		#first: declinations
		dcnNames                  = [] #in Z, better with tabs: tab[lst[str]] dcnNames = ^Tab.new(tInst.dcns.length)
		dcnIndividualCombinations = []
		for dcn in range(len(tInst.dcns)):
			dcnName = sbj.getTypeNameFromID(tInst.dcns[dcn])
			dcnNames.append(name)

			#get individual combinations for each declination
			dcnIndividualCombinations.append( sbj.getTypeMatchingAlternativeNames(dcnName) )

		#get combinations of these individuals together <---------------- !WARNING: Pretty complex stuff here !
		dcnCollectiveCombinations = Combinations__makeAll(dcnIndividualCombinations)

		#get some information to reconstitute declination names (here, we keep the starting 'D' in rawName)
		exactNameWithoutDcns = cutDcnFromTypeName(tgtTypeName)

		#add dcn related alternatives
		for combination in dcnCollectiveCombinations:
			sfx = ""
			for d in range(len(tInst.dcns)):
				sfx += '_' + combination[d]
			alternatives.append(exactNameWithoutDcns + sfx)

		#second: parents (or multi-type keyword if no one)
		if tInst.dcnCommon.parent is None:
			alternatives.append("GUtyp")
		else:
			alternatives += sbj.getTypeMatchingAlternativeNames( sbj.getTypeNameFromID(tInst.dcnCommon.parent) )

		return alternatives



	#list every EXISTING operator of specified kind
	def listAllOperatorAlternatives(sbj, opeHeader):
		l = []
		for f in sbj.cpl.fcts:
			if f.name.startswith(opeHeader):
				l.append(f)
		return l



	#list every operator name that can ever exist to match with the given parameters
	def listAllTargettableOperatorNames(sbj, opeHeader, paramTypeNames):

		#get alternatives for each parameter individually
		paramIndividualAlternatives = []
		for p in paramTypeNames:
			paramIndividualAlternatives.append( sbj.getTypeMatchingAlternativeNames(p) )

		print("PARAM INDIVIDUAL ALTERNATIVES: PARAM[0] [")
		for p in paramIndividualAlternatives[0]:
			print("\t\"" + p + "\"")
		print("]")
		print("PARAM INDIVIDUAL ALTERNATIVES: PARAM[1] [")
		for p in paramIndividualAlternatives[1]:
			print("\t\"" + p + "\"")
		print("]")

		#get every combination of them together
		paramAlternativesTogether = Combinations__makeAll(paramIndividualAlternatives)

		#get every operator name corresponding to these combinations
		possibleOpeNames = []
		for combination in paramAlternativesTogether:
			sfx = ""
			for n in range(len(paramTypeNames)):
				sfx += '_' + combination[n]
			possibleOpeNames.append(opeHeader + sfx)

		#result
		return possibleOpeNames



	#find THE RIGHT matching operator among, the first one among the possible names that truely exists
	def findMatchingOperator(sbj, opeHeader, paramTypeNames):
		existingOpeAlternatives  = sbj.listAllOperatorAlternatives(opeHeader)
		possibleMatchingOpeNames = sbj.listAllTargettableOperatorNames(opeHeader, paramTypeNames)

		print("EXISTING OPE ALTERNATIVES [")
		for ope in existingOpeAlternatives:
			print("\t\"" + ope.name + "\"")
		print("]")
		print("POSSIBLE_MATCHING_NAMES [")
		for p in possibleMatchingOpeNames:
			print("\t\"" + p + "\"")
		print("]")

		#look for the 1st existing operator among those mentionned as "possible matching"
		for p in possibleMatchingOpeNames:
			for ope in existingOpeAlternatives:

				#match => stop here
				if ope.name == p:
					return ope

		#no alternative found
		return None







