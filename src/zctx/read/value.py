# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value.py

#tool for reading value sequences
def readValSeq(ZCI, ZCIKindIfErr, tgtFields, scope, cstOnly=False, dcnKwLstToReplace=None):
	ZCIDbg2(ZCI, "Reading value sequence.")

	#initial conditions
	if ZCI.get() not in INCLUDERS.keys():
		ZCIInt(ZCI, "Must be at the beginning of an includer to read value sequence.")

	#sub-err indication
	ZCIKindIfErr_ending = "."
	if ZCIKindIfErr is not None:
		ZCIKindIfErr_ending = ", in " + ZCIKindIfErr

	#prepare data structure to store the user given fields
	givenFields = {} #fmap[str,value]
	for f in tgtFields:
		givenFields[f.name] = None

	#read fields
	givenFieldsIdx = 0
	peerIdx        = ZCI.pairs[ZCI.ctx.icontent.idx]
	ZCI.inc()
	while True:
		optionalBlanks(ZCI, None)

		#try reading a name (on a copy) for "NAME = VALUE" notation
		tmpCopy   = ZCI.copy()
		fieldName = readName(tmpCopy, None)[1]

		#valid name => check for a following assignment symbol '='
		if len(fieldName) != 0:
			optionalBlanks(tmpCopy, None)

			#no assignment symbol => that was not a "NAME = VALUE" notation => reset everything, we will read again the whole thing as "VALUE" notation
			if readSym(tmpCopy) != SYM__ASG:
				fieldName = ""

			#assignment symbol => alright! let's move our ZCI then
			else:
				ZCI.forwardAlike(tmpCopy)
				ZCI.forward(SYM_LENGTHS[SYM__ASG])
				optionalBlanks(ZCI, "Value after assignment symbol in \"NAME = VALUE\" association (reading value sequence, field " + fieldName + ")" + ZCIKindIfErr_ending)

		#value empty or simply not given
		if ZCI.ctx.icontent.idx == peerIdx:
			ZCI.inc()
			break
		if ZCI.get() == ',':
			ZCIErr(ZCI, "Missing element given in value sequence (\"VALUE\" or \"NAME = VALUE\" expected)" + ZCIKindIfErr_ending)

		#read value
		v = readVal(ZCI,
			"Field VALUE in structure definition" + ZCIKindIfErr_ending,
			scope,
			cstOnly           = cstOnly,
			dcnKwLstToReplace = dcnKwLstToReplace
		)

		#solve name if not explicitely given
		if len(fieldName) == 0:
			if givenFieldsIdx >= len(tgtFields):
				ZCIErr(ZCI, "Too much fields given in value sequence (max " + str(len(tgtFields)) + " fields allowed, " + str(givenFieldsIdx) + " given)" + ZCIKindIfErr_ending)

			#use the next field in logical order
			fieldName       = tgtFields[givenFieldsIdx].name
			givenFieldsIdx += 1

		#invalid explicit field name
		if fieldName not in givenFields.keys():
			ZCIErr(ZCI, "No field \"" + fieldName + "\" can be targetted in value sequence" + ZCIKindIfErr_ending)

		#set value to corresponding field
		if givenFields[fieldName] is not None:
			ZCIErr(ZCI, "Value for field \"" + fieldName + "\" is already set (reading value sequence)" + ZCIKindIfErr_ending)
		givenFields[fieldName] = v

		#must be followed by coma or closing brace
		optionalBlanks(ZCI, None)
		next = ZCI.get()
		if next in INCLUDERS.values():
			if ZCI.ctx.icontent.idx != peerIdx:
				ZCIInt(ZCI, "Ending value sequence with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
			ZCI.inc()
			break
		if next != ',':
			ZCIErr(ZCI, "Invalid element " + next + " given in value sequence, following a field value (2nd analysis, expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIdx] + "')" + ZCIKindIfErr_ending)
		ZCI.inc()

	#fill missing fields with their default value
	for f in givenFields.keys():
		if givenFields[f] is None:

			#target the correct field
			defVal = None
			for tf in tgtFields:
				if tf.inited:
					givenFields[f] = tf.initVal
					ZCIDbg1(ZCI, "No value given for field " + f + " in value sequence (=> set default value: " + tf.initVal.toStr())
				break

			#unable to find def value for that field
			if defVal is None:
				ZCIErr(ZCI, "Value required for field " + f + " in value sequence (no default value for that field)" + ZCIKindIfErr_ending)

	#return completed result
	ZCIDbg1(ZCI, "Ended reading value sequence.")
	return givenFields



#value analysis process (VAP), main entry point
def readVal(ZCI, ZCIKindIfErr, scope, cstOnly=False, dcnKwLstToReplace=None, allowVFC=False):
	ZCIDbg2(ZCI, "Reading value.")



	#STEP 1: PREPARE

	#work on copy
	tmpZCI = ZCI.copy()

	#create a fancy pack to transport redundant dat (VAP 2nd analysis info)
	v2i = vap2info(ZCIKindIfErr, scope, cstOnly, dcnKwLstToReplace)



	#STEP 2: VAP

	#1st analysis: ODP
	firstAnalysisRes = ODP(tmpZCI)
	tmpZCI.forwardUntil(firstAnalysisRes.maxStopIdx+1) #as far as ODP could see, 2nd analysis can go

	#2nd analysis: recursively applied in ODP res
	secondAnalysisRes = applySecondAnalysis(firstAnalysisRes.mainPOCall, tmpZCI, v2i, allowVFC=allowVFC)



	#STEP 3: FORWARD ZCI ACCORDINGLY

	#no value read but err allowed => just stop here, without affecting ZCI
	if ZCIKindIfErr is None:
		if secondAnalysisRes is None:
			return None

	#no value read and that was not allowed => should be handled in 2nd analysis parsing directly
	elif secondAnalysisRes is None:
		ZCIInt(ZCI, "Having null value from 2nd analysis but we don't allow to have \"no value found\".")

	#set maxStopIdx according to 2nd analysis (and not the one of ODP)
	ZCI.forwardUntil(v2i.maxStopIdx)

	#res
	ZCIDbg2(ZCI, "Ended reading value.")
	return secondAnalysisRes
