# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/dataItem.py

#WARNING! Returns data item WITHOUT ANY prefix
def readDataItem(ZCI, ZCIKindIfErr, scope, cstInitialValueOnly=False, allowUnsolvableType=False):
	ZCIDeepDbg(ZCI, "Reading data item.", prtLine=False)

	#read type (if any. Else, continue as nothing happened)
	Type = readType(ZCI, "data item declarator, in " + ZCIKindIfErr, errorIfNotExisting=False)
	if Type != TYPE_ID__UNKNOWN:
		jumpBlankZone(ZCI, "data item name") #no line feed allowed between type-name-initialValue

	#read name
	name = readName(ZCI, "data item name", parseModPfxes=True, modPfxes_asHeaderOnly=True)

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
			ZCIErr(ZCI, "Invalid symbol given here, can only have assignment.")
		ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])

		#read given initial value
		initialized = True
		optionalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
		initialValue = readValue(ZCI, ZCIKindIfErr, scope, cstOnly=cstInitialValueOnly)

		#solve type if missing using initialValue
		if Type == TYPE_ID__UNKNOWN:
			Type = initialValue.Type
			ZCIDeepDbg(ZCI, "Solving missing type using initial value given \"" + ZCI.getTypeInstanceFromID(Type).name + "\".")
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

	#missing Type still not solved
	if Type == TYPE_ID__UNKNOWN:
		if not allowUnsolvableType:
			ZCIErr(ZCI, "Unsolvable type to given element \"" + name + "\" (required either explicitely or implicity using initial value).")

	#result
	ZCIDeepDbg(ZCI, "Ended reading data item.")
	return dataItem(Type, name, initialized, initialValue)



#read dataitem sequence
# Given ZCI must be at an opening includer character.
def readDataItemSequence(
	ZCI, ZCIKindIfErr, scope,
	cstValuesOnly = False, allowUnsolvableTypes = False,
	allowEmpty    = False
):
	ZCIDeepDbg(ZCI, "Reading sequence of data item(s).")

	#initial conditions
	if ZCI.get() not in INCLUDERS.keys():
		ZCIInternal(ZCI, "Must be at the beginning of an includer to read data item sequence.")
	initialIdx = ZCI.ctx.icontent.idx
	peerIdx    = ZCI.pairs[initialIdx]
	ZCI.inc()

	#emptyness
	dis = [] #lst[dataItem]
	optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
	if ZCI.ctx.icontent.idx == peerIdx:
		if allowEmpty:
			ZCI.inc()
			ZCIDeepDbg(ZCI, "Data item sequence is empty (allowed here) => ending reading here.")
			return dis
		ZCIErr(ZCI, "Missing at least one data item declaration in " + ZCIKindIfErr)

	#read sequence
	while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read & store data item
			di = readDataItem(
				ZCI, ZCIKindIfErr, scope,
				cstInitialValueOnly = cstValuesOnly,
				allowUnsolvableType = allowUnsolvableTypes
			)
			checkAlreadyDeclaredDataItemOrField(ZCI, di, dis)
			dis.append(di)
			ZCIDeepDbg(ZCI, "Got data item " + di.toStr(ZCI))

			#must be followed by coma or closing peer
			optionalBlanks(ZCI, None)
			next = ZCI.get()
			if next in INCLUDERS.values():
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInternal(ZCI, "Ending data item sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			if next != ',':
				ZCIErr(ZCI, "Invalid element " + next + " given in data item sequence (expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIdx] + "').")
			ZCI.inc()

	#return result
	ZCIDeepDbg(ZCI, "Ended reading sequence of data item(s).")
	return dis






