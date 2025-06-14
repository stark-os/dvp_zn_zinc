
	#data items
	def checkAlreadyDeclaredDataItemOrField(self, ZCI, dis, di):
		for other in dis:
			if other.name == di.name:
				self.ZCIError(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")



	#WARNING! Returns data item WITHOUT ANY prefix
	def readDataItem(self, ZCI, ZCIKindIfError, scope, cstInitialValueOnly=False, allowUnsolvedType=False):
		self.ZCIDeepDebug(ZCI, "Reading data item.")

		#read type (if any. Else, continue as nothing happened)
		Type = self.readType(ZCI, "data item declarator, in " + ZCIKindIfError, nullIfNotExisting=True)
		if Type is not None:
			self.jumpBlankZone(ZCI, "data item name") #no line feed allowed between type-name-initialValue

		#read name
		name = self.readName(ZCI, "data item name", parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)

		#default initial value: uninitialized
		initialized  = False
		initialValue = None

		#special behavior in global scope
		if scope == self.cpl.globalScope:
			cstInitialValueOnly = True #force cst values

		#optionnal assignment symbol => initial value given
		self.optionnalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
		sym = self.readSymbol(ZCI)
		if sym != SYMBOL__NOT_FOUND: #found a symbol
			if sym != SYMBOL__ASG:
				self.ZCIError(ZCI, "Invalid symbol given here, can only have assignment.")
			ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])

			#read given initial value
			initialized = True
			self.optionnalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
			initialValue = self.readValue(ZCI, ZCIKindIfError, scope, cstOnly=cstInitialValueOnly)

			#solve type if missing using initialValue
			if Type is None:
				Type = initialValue.Type
				self.ZCIDeepDebug(ZCI, "Solving missing type using initial value given \"" + Type.name + "\".")
		self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

		#missing Type still not solved
		if not allowUnsolvedType:
			if Type is None:
				self.ZCIError(ZCI, "Missing type to given element (required either explicitely or implicity).")

		#result
		self.ZCIDeepDebug(ZCI, "Ended reading data item.")
		return dataItem(Type, name, initialized, initialValue)

	#read dataitem sequence
	# Given ZCI must be at an opening includer character.
	def readDataItemSequence(self, ZCI, ZCIKindIfError, scope, cstValuesOnly=False, allowUnsolvedTypes=False):
		self.ZCIDeepDebug(ZCI, "Reading sequence of data item(s).")

		#initial conditions
		initialIndex = ZCI.ctx.icontent.index
		peerIndex    = ZCI.pairs[initialIndex]
		if ZCI.get() not in INCLUDERS.keys():
			self.ZCIInternal(ZCI, "Must be at the beginning of an includer to read data item sequence.")
		ZCI.inc()

		#read sequence
		dis = []   #lst[dataItem]
		foundSelfKw = False
		while True:
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

				#read & store data item
				di = self.readDataItem(ZCI, ZCIKindIfError, scope, cstInitialValueOnly=cstValuesOnly, allowUnsolvedType=allowUnsolvedTypes)
				self.checkAlreadyDeclaredDataItemOrField(ZCI, dis, di)
				dis.append(di)
				self.ZCIDeepDebug(ZCI, "Got data item " + di.toStr())

				#must be followed by coma or closing peer
				next = ZCI.get()
				if next in INCLUDERS.values():
					if ZCI.ctx.icontent.index != peerIndex:
						self.ZCIInternal(ZCI, "Ending data item sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(peerIndex) + ").")
					ZCI.inc()
					break
				if next != ',':
					self.ZCIError(ZCI, "Invalid element " + next + " given in data item sequence (expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIndex] + "').")
				ZCI.inc()

		#return result
		self.ZCIDeepDebug(ZCI, "Ended reading sequence of data item(s).")
		return dis



