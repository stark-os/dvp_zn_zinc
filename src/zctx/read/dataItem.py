# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/dataItem.py

#data items
def checkAlreadyDeclaredDataItemOrField(ZCI, dis, di):
	for other in dis:
		if other.name == di.name:
			ZCIError(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")



#WARNING! Returns data item WITHOUT ANY prefix
def readDataItem(ZCI, ZCIKindIfError, scope, cstInitialValueOnly=False, allowMissingType=False):
	ZCIDeepDebug(ZCI, "Reading data item.", printLine=False)

	#read type (if any. Else, continue as nothing happened)
	Type = readType(ZCI, "data item declarator, in " + ZCIKindIfError, errorIfNotExisting=False)
	if Type != TYPE_ID__NOT_FOUND:
		jumpBlankZone(ZCI, "data item name") #no line feed allowed between type-name-initialValue

	#read name
	name = readName(ZCI, "data item name", parseModPrefixes=True, modPrefix_asHeaderOnly=True)

	#default initial value: uninitialized
	initialized  = False
	initialValue = None

	#special behavior in global scope
	if scope == ZCI.zCtx.cpl.gblScp:
		cstInitialValueOnly = True #force cst values

	#optional assignment symbol => initial value given
	optionalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
	sym = readSymbol(ZCI)
	if sym != SYMBOL__NOT_FOUND: #found a symbol
		if sym != SYMBOL__ASG:
			ZCIError(ZCI, "Invalid symbol given here, can only have assignment.")
		ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])

		#read given initial value
		initialized = True
		optionalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
		initialValue = readValue(ZCI, ZCIKindIfError, scope, cstOnly=cstInitialValueOnly)

		#solve type if missing using initialValue
		if Type == TYPE_ID__NOT_FOUND:
			Type = initialValue.Type
			ZCIDeepDebug(ZCI, "Solving missing type using initial value given \"" + ZCI.getTypeInstanceFromID(Type).name + "\".")
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

	#missing Type still not solved
	if Type == TYPE_ID__NOT_FOUND:
		if not allowMissingType:
			ZCIError(ZCI, "Missing type to given element \"" + name + "\" (required either explicitely or implicity using initial value).")

	#result
	ZCIDeepDebug(ZCI, "Ended reading data item.")
	return dataItem(Type, name, initialized, initialValue)



#read dataitem sequence
# Given ZCI must be at an opening includer character.
def readDataItemSequence(
	ZCI, ZCIKindIfError, scope,
	cstValuesOnly = False, allowMissingTypes = False,
	allowEmpty    = False
):
	ZCIDeepDebug(ZCI, "Reading sequence of data item(s).")

	#initial conditions
	initialIdx = ZCI.ctx.icontent.idx
	peerIdx    = ZCI.pairs[initialIdx]
	if ZCI.get() not in INCLUDERS.keys():
		ZCIInternal(ZCI, "Must be at the beginning of an includer to read data item sequence.")
	ZCI.inc()

	#emptyness
	dis = [] #lst[dataItem]
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
	if ZCI.ctx.icontent.idx == peerIdx:
		if allowEmpty:
			ZCI.inc()
			return dis
		ZCIError(ZCI, "Missing at least one data item declaration in " + ZCIKindIfError)

	#read sequence
	foundSelfKw = False
	while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read & store data item
			di = readDataItem(
				ZCI, ZCIKindIfError, scope,
				cstInitialValueOnly = cstValuesOnly,
				allowMissingType    = allowMissingTypes
			)
			checkAlreadyDeclaredDataItemOrField(ZCI, dis, di)
			dis.append(di)
			ZCIDeepDebug(ZCI, "Got data item " + di.toStr())

			#must be followed by coma or closing peer
			next = ZCI.get()
			if next in INCLUDERS.values():
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInternal(ZCI, "Ending data item sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			if next != ',':
				ZCIError(ZCI, "Invalid element " + next + " given in data item sequence (expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIdx] + "').")
			ZCI.inc()

	#return result
	ZCIDeepDebug(ZCI, "Ended reading sequence of data item(s).")
	return dis






