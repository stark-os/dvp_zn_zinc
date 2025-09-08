# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value_ODP.py

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

			#special case for negative number notation, we will skip them, it was not an operator
			itWasJustANegativeSign = False

			#empty 1st operand
			operandIsEmpty = (ZCI.ctx.icontent.index == operandInitialCtx.icontent.index)
			if operandIsEmpty:
				if operator == SYMBOL__BSU:
					itWasJustANegativeSign = True
					self.ZCIDeepDebug(ZCI, "SPECIAL CASE IN ODP: Found operator BSU without first operand => considerated as negative sign only (no operation).")
				else:
					self.ZCIError(ZCI, "Missing first operand to operator " + OPERATOR_NAMES[operator])
			elif operator in MONO_OPERAND:
				self.ZCIError(ZCI, "Got too much operands for single operator " + OPERATOR_NAMES[operator] + " (only 1 allowed after symbol).")

			#store operand & operator
			if not itWasJustANegativeSign:
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








