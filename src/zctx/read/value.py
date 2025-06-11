
	#ODP
	def ODP_readAndSplitByOperators(self, ZCI, allowedOperators):
		maxStopIndex         = 0
		allowedOperatorsText = "" #only for deep debug

		#deep debug
		if self.deepDebugMode:
			allowedOperatorsText = "["
			for o in allowedOperators:
				allowedOperatorsText += OPERATOR_NAMES[o] + ','
			allowedOperatorsText += "]"
			self.ZCIDeepDebug(ZCI, "ODP-1: Reading & splitting ZCI content " + ZCI.textFormat() + " by operators " + allowedOperatorsText)

		#split by operator symbols
		operands          = [] #lst[zci]
		operators         = [] #lst (certainly ubyt but prefer using only undeclinated for enm storage)
		operatorIndexes   = []
		operandInitialCtx = ZCI.ctx.copy()
		while not ZCI.reachedEnd() and ZCI.get() in VALUE_CHARSET:



			#checking for symbol
			operator = self.readSymbol(ZCI)

			#CASE 1: not a symbol (that can be anything and especially an includer)
			if operator == SYMBOL__NOT_FOUND:
				if ZCI.ctx.icontent.index in ZCI.pairs.keys():
					ZCI.forward(ZCI.pairs[ZCI.ctx.icontent.index] - ZCI.ctx.icontent.index) #includer? It also belongs to the operand no matter what's inside => skip parsing its content
				ZCI.inc()
				continue

			#CASE 2: '^'
			elif operator == SYMBOL__LXO:
				if ZCI.ctx.icontent.index >= ZCI.stopIndex:
					ZCI.inc()
					self.ZCIError(ZCI, "Missing second operand to logical XOR operator (LXO, \"^\"), reached end of ZCI.")

				#look at the following character to determine whether it is a module prefix or a regular LXO operator
				nextChr = ZCI.ctx.icontent.s[ZCI.ctx.icontent.index+1]
				if nextChr == '.' or nextChr in DEFAULT_NAME_CHARSET:
					self.ZCIDeepDebug(ZCI, "ODP-1: '^' symbol detected as module prefix and not as LXO operator.")
					ZCI.inc() #not an operator actually => skipping it
					continue

			#CASE 3: it is a symbol but not allowed
			if operator not in allowedOperators:
				ZCI.forward(SYMBOL_LENGTHS[operator])
				continue



			#create operand as a unique ZCI.
			# This is actually a value to be analyzed in further steps.
			# However, to parse it easilly, we store it as a fragment of the original ZCI (which is, here, a copy of the original but doesn't matter).
			operand            = ZCI.copy(ctxCopy=operandInitialCtx)
			operand.startIndex = operandInitialCtx.icontent.index #initial context must be at operand beginning index
			operand.stopIndex  = ZCI.ctx.icontent.index-1         #we are just before operator index, so at operand end index
			operand.strip()

			#empty operand
			operandIsEmpty = (ZCI.ctx.icontent.index == operandInitialCtx.icontent.index)
			if operator in MONO_OPERAND:
				if not operandIsEmpty:
					self.ZCIError(ZCI, "Got too much operands for single operator " + OPERATOR_NAMES[operator] + " (only 1 allowed after symbol).")
			else:
				if operandIsEmpty:
					self.ZCIError(ZCI, "Missing first operand to operator " + OPERATOR_NAMES[operator])

			#store operand & operator
			operands.append(operand)
			operators.append(operator)
			operatorIndexes.append(ZCI.ctx.icontent.index)
			self.ZCIDeepDebug(ZCI, "ODP-1: New operator " + OPERATOR_NAMES[operator] + " found, current operating sequence is " + opSeq(ZCI.ctx.icontent.index, operands, operators, operatorIndexes).toStr())

			#moving after symbol
			ZCI.forward(SYMBOL_LENGTHS[operator])

			#prepare next operand
			operandInitialCtx = ZCI.ctx.copy()

		#set maxStopIndex
		maxStopIndex = ZCI.ctx.icontent.index - 1

		#no operator found at all => not an operating sequence => return as it was an operating sequence with no operator and only one operand
		if len(operators) == 0:
			self.ZCIDeepDebug(ZCI, "ODP-1: No operator found at all => Finished with null operating sequence.")
			return opSeq(maxStopIndex, None, None, None)

		#last operand cannot be empty
		if ZCI.ctx.icontent.index == operandInitialCtx.icontent.index:
			lastOperator = operators[-1]
			if lastOperator in MONO_OPERAND:
				self.ZCIError(ZCI, "Missing first (and only) operand to single operator " + OPERATOR_NAMES[lastOperator])
			else:
				self.ZCIError(ZCI, "Missing second operand to operator " + OPERATOR_NAMES[lastOperator])

		#create last operand
		operand            = ZCI.copy(ctxCopy=operandInitialCtx)
		operand.startIndex = operandInitialCtx.icontent.index
		operand.stopIndex  = ZCI.ctx.icontent.index - 1
		operand.strip()

		#add last operand
		operands.append(operand)
		self.ZCIDeepDebug(ZCI, "ODP-1: Last operand added, final operating sequence is " + opSeq(maxStopIndex, operands, operators, operatorIndexes).toStr())

		#deep debug
		self.ZCIDeepDebug(ZCI, "ODP-1: Finished reading & splitting ZCI content " + ZCI.textFormat() + " by operators " + allowedOperatorsText)
		return opSeq(maxStopIndex, operands, operators, operatorIndexes)



	#progressive priorizing equivalent for mono operand operators
	def monoOperandOpSeqConcatenation(self, currentOpSeq):
		lastOperand = currentOpSeq.operands.pop()

		#check other operands (not necessary, internal consistency check only)
		for a in currentOpSeq.operands:
			if a.stopIndex - a.startIndex >= 0:
				self.internal("Non-empty operand found in mono-operand operating sequence (last element excepted).")

		#deep debug: before
		self.deepDebug("ODP-2: Applying mono-operand operating sequence concatenation on " + currentOpSeq.toStr())

		#associate each operand to its operator
		result = POCall(
			None,
			atm(ATM__ZCI, lastOperand)
		)
		current = result
		while len(currentOpSeq.operators) != 0:
			current.name          = OPERATOR_NAMES[currentOpSeq.operators.pop(0)]
			current.operatorIndex = currentOpSeq.operatorIndexes.pop(0)
			current.secondOperand = atm(
				ATM__POCALL,
				POCall(
					None,
					current.secondOperand
				)
			)
			current = current.secondOperand.data

		#deep debug: after
		self.deepDebug("ODP-2: Mono-operand operating sequence concatenation resulted into the following POCall " + result.toStr())
		return result



	#transform an operating sequence into a single POCall (destroying the given opSeq!)
	def progressivePriorizing(self, currentOpSeq, monoOperand): #WARNING! DO NOT USE WITH SO !!!
		if len(currentOpSeq.operands) == 0:
			self.internal("Got no operand in operating sequence when running progressive priorizing.")

		#mono-operand operating sequence => redirect to the adapted equivalent
		if monoOperand:
			return self.monoOperandOpSeqConcatenation(currentOpSeq)

		#deep debug: before
		self.deepDebug("ODP-2: Applying progressive priorizing on operating sequence " + currentOpSeq.toStr())

		#first element (we must keep track of it)
		result = POCall(
			None,
			atm(ATM__ZCI, currentOpSeq.operands.pop())
		)
		current = result

		#for each remaining operand, make function calls (Potential Operator Call)
		while len(currentOpSeq.operands) != 0:
			current.name          = OPERATOR_NAMES[currentOpSeq.operators.pop()]
			current.operatorIndex = currentOpSeq.operatorIndexes.pop()
			current.firstOperand = atm(
				ATM__POCALL,
				POCall(
					None,
					atm(ATM__ZCI, currentOpSeq.operands.pop())
				)
			)
			current = current.firstOperand.data

		#deep debug: after
		self.deepDebug("ODP-2: Progressive priorizing resulted into the following POCall " + result.toStr())
		return result



	#group priorizing
	# This function is higly important! It applies group priorization on every value that can be found in a POCall.
	def ODP_applyGroupPriorization(self, maxStopIndex, currentPOCall, operatorsAllowed, monoOperand=False):

		#1st operand
		if currentPOCall.firstOperand is not None:

			#leaf => apply here
			if currentPOCall.firstOperand.id == ATM__ZCI:
				originalCtx  = currentPOCall.secondOperand.data.ctx.copy()
				currentOpSeq = self.ODP_readAndSplitByOperators(currentPOCall.firstOperand.data, operatorsAllowed)

				#no operator found => restore original ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
				if currentOpSeq.operators is None:
					currentPOCall.firstOperand.data.resetCtx(originalCtx)
					currentPOCall.firstOperand.data.stopIndex = currentOpSeq.stopIndex
					currentPOCall.firstOperand.data.strip()

				#operator found => progressive priorizing
				else:
					currentPOCall.firstOperand = atm(
						ATM__POCALL,
						self.progressivePriorizing(currentOpSeq, monoOperand)
					)

				#update maxStopIndex
				if maxStopIndex < currentOpSeq.stopIndex:
					maxStopIndex = currentOpSeq.stopIndex

			#tree => check deeper
			elif currentPOCall.firstOperand.id == ATM__POCALL:
				maxStopIndex = self.ODP_applyGroupPriorization(maxStopIndex, currentPOCall.firstOperand.data, operatorsAllowed, monoOperand=monoOperand)

		#2nd operand
		if currentPOCall.secondOperand is not None:

			#leaf => apply here
			if currentPOCall.secondOperand.id == ATM__ZCI:
				originalCtx  = currentPOCall.secondOperand.data.ctx.copy()
				currentOpSeq = self.ODP_readAndSplitByOperators(currentPOCall.secondOperand.data, operatorsAllowed)

				#no operator found => restore origin ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
				if currentOpSeq.operators is None:
					currentPOCall.secondOperand.data.resetCtx(originalCtx)
					currentPOCall.secondOperand.data.stopIndex = currentOpSeq.stopIndex
					currentPOCall.secondOperand.data.strip()

				#operator found => progressive priorizing
				else:
					currentPOCall.secondOperand = atm(
						ATM__POCALL,
						self.progressivePriorizing(currentOpSeq, monoOperand)
					)

				#update maxStopIndex
				if maxStopIndex < currentOpSeq.stopIndex:
					maxStopIndex = currentOpSeq.stopIndex

			#tree => check deeper
			elif currentPOCall.secondOperand.id == ATM__POCALL:
				maxStopIndex = self.ODP_applyGroupPriorization(maxStopIndex, currentPOCall.secondOperand.data, operatorsAllowed, monoOperand=monoOperand)

		#return it to know until where ODP has been (so we know where to continue reading after that Value)
		return maxStopIndex



	#entry point for Operation Decomposition Process (ODP)
	def ODP(self, originalZCI):
		ZCI            = originalZCI.copy()
		ZCI.startIndex = ZCI.ctx.icontent.index
		ZCI.updateText()

		#prepare result
		result = ODPRODPResultesult = ODPResult(
			0,
			POCall( None, atm(ATM__ZCI, ZCI) ) #formatting raw input value under POCall format
		)

		#deep debug
		self.deepDebug("Beginning ODP on ZCI " + ZCI.textFormat())

		#1st group priorization (lowest): CO
		self.deepDebug("ODP-0: Applying 1st group priorization.")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, CO)
		self.deepDebug("ODP-0: Applied 1st group priorization, resulted into " + result.mainPOCall.toStr())

		#2nd group priorization: BO
		self.deepDebug("ODP-0: Applying 2nd group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, BO)
		self.deepDebug("ODP-0: Applied 2nd group priorization, resulted into " + result.mainPOCall.toStr())

		#3rd group priorization: AO + LO
		self.deepDebug("ODP-0: Applying 3rd group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, AO + LO)
		self.deepDebug("ODP-0: Applied 3rd group priorization, resulted into " + result.mainPOCall.toStr())

		#4th group priorization: DO
		self.deepDebug("ODP-0: Applying 4th group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, DO)
		self.deepDebug("ODP-0: Applied 4th group priorization, resulted into " + result.mainPOCall.toStr())

		#5th group priorization: SO (highest treated in ODP)
		self.deepDebug("ODP-0: Applying 5th group priorization (SO)")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, SO, monoOperand=True)
		self.deepDebug("ODP-0: Applied 5th group priorization, resulted into " + result.mainPOCall.toStr())
		self.deepDebug("Ended ODP on ZCI " + ZCI.textFormat())
		return result



	#2nd analysis
	def unknownValueErrorIn2ndAnalysis(self, ZCI):
		self.ZCIError(ZCI, "Unknown value given (not respecting any format supported by VAP in 2nd analysis).")

	def secondAnalysis(self, ZCI, vap2info):
		self.ZCIDeepDebug(ZCI, "2nd analysis: Reading ZCI fragment " + ZCI.textFormat() + " to apply second analysis on it.")
		result = None
		c = ZCI.get()



		# I] LITERAL: COMMON DATA STRUCTURES

		#map starter symbol
		targettingMap = False
		if c == ':':
			if ZCI.inc():
				self.unknownValueErrorIn2ndAnalysis(ZCI)
			targettingMap = True

		#starting with includer
		if c in ('(', '[', '{'):
			#Seems similar to check in the whole INCLUDERS.keys() but this is not related to these actually.
			#We are specificly targetting these 3 and not because they are includer keys but because we have specific pattern associated to them.
			keyValue_initializerType = None #for maps only
			if c == '(':
				if targettingMap:
					targettedType            = self.getType(TYPE_FULLNAME_FMAP)
					keyValue_initializerType = self.getType(TYPE_FULLNAME_TAB) #require 2 tab for fmap initialization
				else:
					targettedType = self.getType(TYPE_FULLNAME_TAB)
			elif c == '[':
				if targettingMap:
					targettedType            = self.getType(TYPE_FULLNAME_MMAP)
					keyValue_initializerType = self.getType(TYPE_FULLNAME_LST) #require 2 lst for mmap initialization
				else:
					targettedType = self.getType(TYPE_FULLNAME_LST)
			elif c == '{':
				if targettingMap:
					self.ZCIError(ZCI, "Associative notation cannot be set to braces includer (\":{...}\" is linked to nothing).")
				targettedType = self.getType(TYPE_FULLNAME_FLY)

			#init limits
			peerIndex    = ZCI.pairs[ZCI.ctx.icontent.index]
			targettedEnd = ZCI.ctx.icontent.s[peerIndex]
			ZCI.inc()

			#read subvalues as long as we have some (separated by comas)
			subValues        = [] #lst[value]
			subValues_second = [] #for maps
			while True:

				#read subvalue
				self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
				subValues.append( self.readValue(ZCI, vap2info.ZCIKindIfError, vap2info.scope, vap2info.cstOnly) )

				#read second subValue (for maps only)
				if targettingMap:

					#colon separator required
					self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
					next = ZCI.get()
					if next != ':':
						self.ZCIError(ZCI, "Invalid element " + next + " given in associative sequence (expected colon separator ':').")
					ZCI.inc()

					#read a second subvalue (require a couple for association)
					self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
					subValues_second.append( self.readValue(ZCI, vap2info.ZCIKindIfError, vap2info.scope, vap2info.cstOnly) )

				#look for end separator
				self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
				next = ZCI.get()
				if next == targettedEnd:
					if ZCI.ctx.icontent.index != peerIndex:
						self.ZCIInternal(ZCI, "Ending value sequence inside includer with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(peerIndex) + ").")
					ZCI.inc()
					break
				if next != ',':
					self.ZCIError(ZCI, "Invalid element " + next + " given in value sequence between includers (expected coma separator ',' or closing includer '" + targettedEnd + "').")
				ZCI.inc()

			#table with only one element => explicit priorization
			if targettedEnd == ')' and not targettingMap and len(subValues) == 1:
				result = subValues[0]
				self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in EXPLICIT PRIORIZATION " + result.toStr())
				return result

			#finishing result: maps
			if targettingMap:

				#set keys et values for map initialization
				keys   = value(keyValue_initializerType, atm(ATM__LST, subValues))
				values = value(keyValue_initializerType, atm(ATM__LST, subValues_second))
				result = value(
					targettedType,
					atm(ATM__LST, [keys, values])
				)

			#finishing result: tab, lst & fly
			else:
				result = value(targettedType, atm(ATM__LST, subValues))

			#return result
			self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in COMMON DATA STRUCTURE SHORTCUT NOTATION " + result.toStr())
			return result

		#having found a colon but wasn't a map => no pattern matches such a thing
		if targettingMap:
			self.unknownValueErrorIn2ndAnalysis(ZCI)



		# II] LITERAL: BYTE NOTATIONS

		#prefix found
		if c == BN_PREFIX:
			if ZCI.inc():
				self.ZCIError(ZCI, "Missing content after byte notation.")

			#multi-byte sequence
			if ZCI.get() == BN_PREFIX:
				if ZCI.inc():
					self.ZCIError(ZCI, "Missing content after multiple-bytes notation.")

				#prepare sequence
				sequence = [] #lst[value]
				while ZCI.get() in HEX_DIGITS_LOWERCASE:
					sequence.append(
						value(self.rootTypes[RT__BYT], atm(ATM__BYT, self.readHexByte(ZCI)) )
					)
					if ZCI.inc():
						break

				#missing characters
				if len(sequence) == 0:
					self.ZCIError(ZCI, "Missing valid hexadecimal characters in multi-bytes notation.")

				#finish result
				result = value(self.rootTypes[RT__PTR], atm(ATM_LST, sequence))
				self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in MULTI-BYTE NOTATION " + result.toStr())
				return result

			#single-byte sequence
			result = value(
				self.rootTypes[RT__BYT],
				atm(ATM__BYT, self.readHexByte(ZCI))
			)
			ZCI.inc()
			self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in SINGLE-BYTE NOTATION " + result.toStr())
			return result



		# III] .

		#
		#



		#unknown value format
		self.unknownValueErrorIn2ndAnalysis(ZCI)



	def secondAnalysisIncludingFOs(self, ZCI, vap2info):

		#mono-operand FOs: size (FSZ)
		if ZCI.get() == '#':
			self.ZCIDeepDebug(ZCI, "2nd analysis: Processing FSZ operator.")
			Type = None

			#try to get type directly
			Type = self.readType(ZCI, vap2info.ZCIKindIfError, nullIfNotExisting=True)

			#rather try to get it through a data item name given
			if Type is None:
				di = getDataItem(
					self.readName(ZCI, "raw type or data item name for size operator (#)"),
					vap2info.scope
				)
				if di is None:
					self.ZCIError(ZCI, "Unable to get raw type or data item name for size operator (#).")
				Type = di.Type

			#process FO & return result
			result = value(self.rootTypes[RT__LONG], atm(ATM_CALL, result))
			size = Type.size
			if reslt
			self.ZCIDeepDebug("2nd analysis: FSZ resulted into fsz(" + Type.name + ") = " + str(Type.size))
			return result

		#mono-operand FOs: reference (FRF)
		if ZCI.get() == '@':
			return 

		#second analysis: read value but don't care if there are still things to analyze ()
		result = self.SecondAnalysis(ZCI, vap2info) #after this, ZCI index is right AFTER the value read
		self.optionnalBlanks(ZCI, None)

		#that was it
		if ZCI.reachedEnd():
			return result

		#2-operands FOs: casht (FCA)
		if ZCI.get() == '$':
			return 

		#2-operands FOs: field access (FFA)
		if ZCI.get() == '.':
			return 

		#too much content in VALUE ZCE
		self.ZCIError(ZCI, "Too much elements in VALUE ZCE (2nd analysis parsing).")



	def applySecondAnalysis(self, currentPOCall, originalZCI, vap2info):

		#process 1st operand
		firstOperandValue = None
		if currentPOCall.firstOperand is not None:

			#recursively solving children before
			if currentPOCall.firstOperand.id == ATM__POCALL:
				firstOperandValue = self.applySecondAnalysis(currentPOCall.firstOperand.data, originalZCI, vap2info)

			#considering it can only be a ZCI atm (internal error case could have added)
			else:
				firstOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.firstOperand.data, vap2info)

		#process 2nd operand
		secondOperandValue = None
		if currentPOCall.secondOperand is not None:

			#recursively solving children before
			if currentPOCall.secondOperand.id == ATM__POCALL:
				secondOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.secondOperand.data, originalZCI, vap2info)

			#considering it can only be a ZCI atm (internal error case could have added)
			else:
				secondOperandValue = self.processFOAndSecondAnalysis(currentPOCall.secondOperand.data, vap2info)



		#1ST CASE: SINGLE VALUE UNIT (NON-CALL)

		#null name => mono-operand mandatorily
		if currentPOCall.name is None:
			target = None
			if currentPOCall.firstOperand is None:
				target = secondOperandValue
			elif currentPOCall.secondOperand is None:
				target = firstOperandValue

			#should never occur
			if target is None:
				self.internal("Found null-name POCall with 2 null or 2 non-null operands (inconsistent result from ODP).")
			return target



		#2ND CASE: OPERATOR CALL

		#set operator parameters
		params = []
		if firstOperandValue is not None:
			params.append(firstOperandValue)
		if secondOperandValue is not None:
			params.append(secondOperandValue)

		#solve name
		operatorFullName = currentPOCall.name[:] #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO COMPLETE with full name constitution
		#operatorFullName = 'O' + currentPOCall.name
		#for p in params:
		#	operatorFullName += '_' + p.type.name

		#check for matching operator function
		matchingFunction = None
		for f in self.cpl.functions:
			if f.name == operatorFullName:
				matchingFunction = f
				break
		if matchingFunction is None:
			originalZCI.forward(currentPOCall.operatorIndex - originalZCI.ctx.icontent.index)
			self.ZCIError(originalZCI, "No operator \"" + f.name + "\" declared yet.")

		#result
		return value(
			matchingFunction.retType,
			atm(ATM__CALL, call(operatorFullName, params))
		)



	#value analysis process (VAP)
	def readValue(self, ZCI, ZCIKindIfError, scope, cstOnly=False):
		self.ZCIDeepDebug(ZCI, "Reading value.")

		#1st analysis: ODP
		firstAnalysisResult = self.ODP(ZCI)
		ZCI.forward( firstAnalysisResult.maxStopIndex - ZCI.ctx.icontent.index +1)

		#apply 2nd analysis recursively in ODP result
		secondAnalysisResult = self.applySecondAnalysis(firstAnalysisResult.mainPOCall, ZCI, vap2(ZCIKindIfError, scope, cstOnly)) #here, ZCI is given for error messages only
		self.ZCIDeepDebug(ZCI, "Ended reading value with result :" + secondAnalysisResult.toStr())
		return secondAnalysisResult




