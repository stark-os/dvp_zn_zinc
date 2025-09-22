# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value.py

#tool for reading value sequences
def readValueSequence(ZCI, tgtFields, scope, cstOnly=False):

	#initial conditions
	if ZCI.get() not in INCLUDERS.keys():
		ZCIInternal(ZCI, "Must be at the beginning of an includer to read value sequence.")

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
		fieldName = readName(tmpCopy, None)

		#valid name => check for a following assignment symbol '='
		if len(fieldName) != 0:
			optionalBlanks(tmpCopy, None)

			#no assignment symbol => that was not a "NAME = VALUE" notation => reset everything, we will read again the whole thing as "VALUE" notation
			if readSymbol(tmpCopy) != SYMBOL__ASG:
				fieldName = ""

			#assignment symbol => alright! let's move our ZCI then
			else:
				ZCI.forwardAlike(tmpCopy)
				ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])
				optionalBlanks(ZCI, "Value after assignment symbol in \"NAME = VALUE\" association (reading value sequence, field " + fieldName + ").")

		#value empty or simply not given
		if ZCI.ctx.icontent.idx >= peerIdx: #should never be greater (could have set an internal error here)
			break
		if ZCI.get() == ',':
			ZCIError(ZCI, "Missing element given in value sequence (\"VALUE\" or \"NAME = VALUE\" expected).")

		#read value
		v = readValue(ZCI, "Field VALUE in structure definition.", scope, cstOnly=cstOnly)

		#solve name if not explicitely given
		if len(fieldName) == 0:
			if givenFieldsIdx >= len(tgtFields):
				ZCIError(ZCI, "Too much fields given in value sequence (max " + str(len(tgtFields)) + " fields allowed, " + str(givenFieldsIdx) + " given).")

			#use the next field in logical order
			fieldName       = tgtFields[givenFieldsIdx].name
			givenFieldsIdx += 1

		#set value to corresponding field
		if givenFields[fieldName] is not None:
			ZCIError(ZCI, "Value for field " + fieldName + " is already set (reading value sequence).")
		givenFields[fieldName] = v

		#must be followed by coma or closing brace
		optionalBlanks(ZCI, None)
		next = ZCI.get()
		if next in INCLUDERS.values():
			if ZCI.ctx.icontent.idx != peerIdx:
				ZCIInternal(ZCI, "Ending value sequence with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
			ZCI.inc()
			break
		if next != ',':
			ZCIError(ZCI, "Invalid element " + next + " given in value sequence, following a field value (2nd analysis, expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIdx] + "').")
		ZCI.inc()

	#fill missing fields with their default value
	for f in givenFields.keys():
		if givenFields[f] is None:
			di = tgtFields[f]

			#set default value if no one given
			if not di.initialized:
				ZCIError(ZCI, "Value required for field " + f + " in value sequence (no default value set for that field)")
			ZCIDeepDebug(ZCI, "No value given for field " + f + " in value sequence (=> set default value: " + di.initialValue.toStr(ZCI))
			givenFields[f] = di.initialValue

	#return completed result
	return givenFields



#value analysis process (VAP), main entry point
def readValue(ZCI, ZCIKindIfError, scope, cstOnly=False):
	ZCIDeepDebug(ZCI, "Reading value.")

	#1st analysis: ODP
	firstAnalysisRes = ODP(ZCI)
	ZCI.forwardUntil(firstAnalysisRes.maxStopIdx+1)

	#apply 2nd analysis recursively in ODP result
	secondAnalysisRes = applySecondAnalysis(firstAnalysisRes.mainPOCall, ZCI, vap2(ZCIKindIfError, scope, cstOnly)) #here, ZCI is given for error messages only
	ZCIDeepDebug(ZCI, "Ended reading value.")
	return secondAnalysisRes












