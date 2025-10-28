# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value.py

#tool for reading value sequences
def readValSeq(ZCI, ZCIKindIfErr, tgtFields, scope, cstOnly=False, dcnKwLstToReplace=None):

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
		if ZCI.ctx.icontent.idx >= peerIdx: #should never be greater (could have set an internal error here)
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
			ZCIErr(ZCI, "Value for field " + fieldName + " is already set (reading value sequence)" + ZCIKindIfErr_ending)
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
			di = tgtFields[f]

			#set default value if no one given
			if not di.inited:
				ZCIErr(ZCI, "Value required for field " + f + " in value sequence (no default value set for that field)" + ZCIKindIfErr_ending)
			ZCIDeepDbg(ZCI, "No value given for field " + f + " in value sequence (=> set default value: " + di.initVal.toStr())
			givenFields[f] = di.initVal

	#return completed result
	return givenFields



#value analysis process (VAP), main entry point
def readVal(ZCI, ZCIKindIfErr, scope, cstOnly=False, dcnKwLstToReplace=None, allowVFC=False):
	ZCIDeepDbg(ZCI, "Reading value.")

	#can have err => use a copy just in case
	if ZCIKindIfErr is None:
		tgtZCI = ZCI.copy()
	else:
		tgtZCI = ZCI

	#1st analysis: ODP
	firstAnalysisRes = ODP(tgtZCI)
	tgtZCI.forwardUntil(firstAnalysisRes.maxStopIdx+1)

	#apply 2nd analysis recursively in ODP result
	secondAnalysisRes = applySecondAnalysis(
		firstAnalysisRes.mainPOCall,
		tgtZCI, #for err msg only
		vap2info(ZCIKindIfErr, scope, cstOnly, dcnKwLstToReplace),
		allowVFC=allowVFC
	)

	#no value found is allowed => share the forwarding with ori ZCI
	if ZCIKindIfErr is None:
		if secondAnalysisRes is not None:
			ZCI.forwardAlike(tgtZCI)

	#should never happen
	elif secondAnalysisRes is None:
		ZCIInt(ZCI, "Having null value from 2nd analysis but we don't allow to have \"no value found\".")

	#res
	ZCIDeepDbg(ZCI, "Ended reading value.")
	return secondAnalysisRes
