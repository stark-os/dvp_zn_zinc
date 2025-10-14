# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/operator.py

	# ---------------- OPERATOR RELATED ----------------

	#list every EXISTING operator of specified kind
	def listAllExistingOpes(sbj, opeHeader):
		l = []
		for f in sbj.cpl.fcts:
			if f.name.startswith(opeHeader):
				l.append(f)
		return l

	def listAllExistingOpeNames(sbj, opeHeader):
		ol = sbj.listAllExistingOpes(opeHeader)
		nl = []
		for o in ol:
			nl.append(o.name)
		return strLst_toDsp(nl)



	#list every operator name that can ever exist to match with the given parameters
	def listAllTargettableOperatorNames(sbj, opeHeader, paramTypeIDs, paramTypeNames):

		#get alternatives for each parameter individually
		paramIndividualAlternatives = []
		for p in paramTypeIDs:
			paramIndividualAlternatives.append( sbj.getTypeAlternativeNames(p) )

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
	def findMatchingOperator(sbj, opeHeader, paramTypeIDs, paramTypeNames):
		sbj.deepDbg("Trying to find matching function for operator " + opeHeader + " with parameters (" + ",".join(paramTypeNames) + ").", prtSubCtxs=False, prtLine=False)
		possibleMatchingOpeNames = sbj.listAllTargettableOperatorNames(opeHeader, paramTypeIDs, paramTypeNames)
		allExistingOpes          = sbj.listAllExistingOpes(opeHeader)

		#look for the 1st existing operator among those mentionned as "possible matching"
		for p in possibleMatchingOpeNames:
			sbj.deepDbg("Next possible matching name " + p, prtSubCtxs=False, prtLine=False)
			for ope in allExistingOpes:

				#match => stop here
				if ope.name == p:
					sbj.deepDbg("Its a MATCH ! => using it.", prtSubCtxs=False, prtLine=False)
					return ope

		#no alternative found
		return None







