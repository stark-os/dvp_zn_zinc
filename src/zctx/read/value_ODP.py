# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value_ODP.py

#ODP
def ODP_readAndSplitByOperators(ZCI, allowedOperators):
	maxStopIdx           = 0
	allowedOperatorsText = "" #only for deep debug

	#deep debug
	if ZCI.zCtx.deepDbgMode:
		allowedOperatorsText = "["
		for o in allowedOperators:
			allowedOperatorsText += OPERATOR_NAMES[o] + ','
		allowedOperatorsText += "]"
		ZCIDeepDbg(ZCI, "ODP-1: Reading & splitting ZCI content \"" + ZCI.textFormat() + "\" by operators " + allowedOperatorsText)

	#split by operator symbols
	operands          = [] #lst[zci]
	operators         = [] #lst (certainly ubyt but prefer using only undeclinated for enm storage)
	operatorIdxes     = []
	operandInitialCtx = ZCI.ctx.copy()
	while not ZCI.reachedEnd() and ZCI.get() in VALUE_CHARSET:



		#checking for symbol
		operator = readSymbol(ZCI)

		#CASE 1: not a symbol (that can be anything and especially an includer)
		if operator == SYMBOL__NOT_FOUND:
			if ZCI.ctx.icontent.idx in ZCI.pairs.keys():
				ZCI.forwardUntil( ZCI.pairs[ZCI.ctx.icontent.idx] ) #includer? It also belongs to the operand no matter what's inside => skip parsing its content
			ZCI.inc()
			continue

		#CASE 2: '^'
		elif operator == SYMBOL__LXO:
			if ZCI.ctx.icontent.idx >= ZCI.stopIdx:
				ZCI.inc()
				ZCIErr(ZCI, "Missing second operand to logical XOR operator (LXO, \"^\"), reached end of ZCI.")

			#look at the following character to determine whether it is a module prefix or a regular LXO operator
			nextChr = ZCI.ctx.icontent.s[ZCI.ctx.icontent.idx+1]
			if nextChr == '.' or nextChr in DEFAULT_NAME_CHARSET:
				ZCIDeepDbg(ZCI, "ODP-1: '^' symbol detected as module prefix and not as LXO operator.")
				ZCI.inc() #not an operator actually => skipping it
				continue

		#CASE 3: it is a symbol but not allowed
		if operator not in allowedOperators:
			ZCI.forward(SYMBOL_LENGTHS[operator])
			continue



		#create operand as a unique ZCI.
		# This is actually a value to be analyzed in further steps.
		# However, to parse it easilly, we store it as a fragment of the original ZCI (which is, here, a copy of the original but doesn't matter).
		operand          = ZCI.copy(ctxCopy=operandInitialCtx)
		operand.startIdx = operandInitialCtx.icontent.idx #initial context must be at operand beginning index
		operand.stopIdx  = ZCI.ctx.icontent.idx-1         #we are just before operator index, so at operand end index
		operand.strip()

		#special case for negative number notation, we will skip them, it was not an operator
		itWasJustANegativeSign = False

		#empty 1st operand
		operandIsEmpty = (ZCI.ctx.icontent.idx == operandInitialCtx.icontent.idx)
		if operandIsEmpty:
			if operator == SYMBOL__BSU:
				itWasJustANegativeSign = True
				ZCIDeepDbg(ZCI, "SPECIAL CASE IN ODP: Found operator BSU without first operand => considerated as negative sign only (no operation).")
			else:
				ZCIErr(ZCI, "Missing first operand to operator " + OPERATOR_NAMES[operator])
		elif operator in MONO_OPERAND:
			ZCIErr(ZCI, "Got too much operands for single operator " + OPERATOR_NAMES[operator] + " (only 1 allowed after symbol).")

		#store operand & operator
		if not itWasJustANegativeSign:
			operands.append(operand)
			operators.append(operator)
			operatorIdxes.append(ZCI.ctx.icontent.idx)
			ZCIDeepDbg(ZCI, "ODP-1: New operator " + OPERATOR_NAMES[operator] + " found, cur operating sequence is " + opSeq(ZCI.ctx.icontent.idx, operands, operators, operatorIdxes).toStr())

		#moving after symbol
		ZCI.forward(SYMBOL_LENGTHS[operator])

		#prepare next operand
		operandInitialCtx = ZCI.ctx.copy()

	#set maxStopIdx
	maxStopIdx = ZCI.ctx.icontent.idx - 1

	#no operator found at all => not an operating sequence => return as it was an operating sequence with no operator and only one operand
	if len(operators) == 0:
		ZCIDeepDbg(ZCI, "ODP-1: No operator found at all => Finished with null operating sequence.")
		return opSeq(maxStopIdx, None, None, None)

	#last operand cannot be empty
	if ZCI.ctx.icontent.idx == operandInitialCtx.icontent.idx:
		lastOperator = operators[-1]
		if lastOperator in MONO_OPERAND:
			ZCIErr(ZCI, "Missing first (and only) operand to single operator " + OPERATOR_NAMES[lastOperator])
		else:
			ZCIErr(ZCI, "Missing second operand to operator " + OPERATOR_NAMES[lastOperator])

	#create last operand
	operand          = ZCI.copy(ctxCopy=operandInitialCtx)
	operand.startIdx = operandInitialCtx.icontent.idx
	operand.stopIdx  = ZCI.ctx.icontent.idx - 1
	operand.strip()

	#add last operand
	operands.append(operand)
	ZCIDeepDbg(ZCI, "ODP-1: Last operand added, final operating sequence is " + opSeq(maxStopIdx, operands, operators, operatorIdxes).toStr())

	#deep debug
	ZCIDeepDbg(ZCI, "ODP-1: Finished reading & splitting ZCI content \"" + ZCI.textFormat() + "\" by operators " + allowedOperatorsText)
	return opSeq(maxStopIdx, operands, operators, operatorIdxes)



#progressive priorizing equivalent for mono operand operators
def monoOperandOpSeqConcatenation(zCtx, curOpSeq):
	lastOperand = curOpSeq.operands.pop()

	#check other operands (not necessary, internal consistency check only)
	for a in curOpSeq.operands:
		if a.stopIdx - a.startIdx >= 0:
			zCtx.internal("Non-empty operand found in mono-operand operating sequence (last element excepted).")

	#deep debug: before
	zCtx.deepDbg("ODP-2: Applying mono-operand operating sequence concatenation on " + curOpSeq.toStr())

	#associate each operand to its operator
	res = POCall(
		None,
		atm(ATM__ZCI, lastOperand)
	)
	cur = res
	while len(curOpSeq.operators) != 0:
		cur.name        = OPERATOR_NAMES[curOpSeq.operators.pop(0)]
		cur.operatorIdx = curOpSeq.operatorIdxes.pop(0)
		cur.secondOperand = atm(
			ATM__POCALL,
			POCall(
				None,
				cur.secondOperand
			)
		)
		cur = cur.secondOperand.data

	#deep debug: after
	zCtx.deepDbg("ODP-2: Mono-operand operating sequence concatenation resulted into the following POCall " + res.toStr())
	return res



#transform an operating sequence into a single POCall (destroying the given opSeq!)
def progressivePriorizing(zCtx, curOpSeq, monoOperand): #WARNING! DO NOT USE WITH SO !!!
	if len(curOpSeq.operands) == 0:
		zCtx.internal("Got no operand in operating sequence when running progressive priorizing.")

	#mono-operand operating sequence => redirect to the adapted equivalent
	if monoOperand:
		return monoOperandOpSeqConcatenation(zCtx, curOpSeq)

	#deep debug: before
	zCtx.deepDbg("ODP-2: Applying progressive priorizing on operating sequence " + curOpSeq.toStr())

	#first element (we must keep track of it)
	res = POCall(
		None,
		atm(ATM__ZCI, curOpSeq.operands.pop())
	)
	cur = res

	#for each remaining operand, make function calls (Potential Operator Call)
	while len(curOpSeq.operands) != 0:
		cur.name        = OPERATOR_NAMES[curOpSeq.operators.pop()]
		cur.operatorIdx = curOpSeq.operatorIdxes.pop()
		cur.firstOperand = atm(
			ATM__POCALL,
			POCall(
				None,
				atm(ATM__ZCI, curOpSeq.operands.pop())
			)
		)
		cur = cur.firstOperand.data

	#deep debug: after
	zCtx.deepDbg("ODP-2: Progressive priorizing resulted into the following POCall " + res.toStr())
	return res



#group priorizing
# This function is higly important! It applies group priorization on every value that can be found in a POCall.
def ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall, operatorsAllowed, monoOperand=False):

	#1st operand
	if curPOCall.firstOperand is not None:

		#leaf => apply here
		if curPOCall.firstOperand.id == ATM__ZCI:
			originalCtx  = curPOCall.secondOperand.data.ctx.copy()
			curOpSeq = ODP_readAndSplitByOperators(curPOCall.firstOperand.data, operatorsAllowed)

			#no operator found => restore original ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
			if curOpSeq.operators is None:
				curPOCall.firstOperand.data.resetCtx(originalCtx)
				curPOCall.firstOperand.data.stopIdx = curOpSeq.stopIdx
				curPOCall.firstOperand.data.strip()

			#operator found => progressive priorizing
			else:
				curPOCall.firstOperand = atm(
					ATM__POCALL,
					progressivePriorizing(zCtx, curOpSeq, monoOperand)
				)

			#update maxStopIdx
			if maxStopIdx < curOpSeq.stopIdx:
				maxStopIdx = curOpSeq.stopIdx

		#tree => check deeper
		elif curPOCall.firstOperand.id == ATM__POCALL:
			maxStopIdx = ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall.firstOperand.data, operatorsAllowed, monoOperand=monoOperand)

	#2nd operand
	if curPOCall.secondOperand is not None:

		#leaf => apply here
		if curPOCall.secondOperand.id == ATM__ZCI:
			originalCtx  = curPOCall.secondOperand.data.ctx.copy()
			curOpSeq = ODP_readAndSplitByOperators(curPOCall.secondOperand.data, operatorsAllowed)

			#no operator found => restore origin ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
			if curOpSeq.operators is None:
				curPOCall.secondOperand.data.resetCtx(originalCtx)
				curPOCall.secondOperand.data.stopIdx = curOpSeq.stopIdx
				curPOCall.secondOperand.data.strip()

			#operator found => progressive priorizing
			else:
				curPOCall.secondOperand = atm(
					ATM__POCALL,
					progressivePriorizing(zCtx, curOpSeq, monoOperand)
				)

			#update maxStopIdx
			if maxStopIdx < curOpSeq.stopIdx:
				maxStopIdx = curOpSeq.stopIdx

		#tree => check deeper
		elif curPOCall.secondOperand.id == ATM__POCALL:
			maxStopIdx = ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall.secondOperand.data, operatorsAllowed, monoOperand=monoOperand)

	#return it to know until where ODP has been (so we know where to continue reading after that Value)
	return maxStopIdx



#entry point for Operation Decomposition Process (ODP)
def ODP(originalZCI):
	ZCI          = originalZCI.copy()
	ZCI.startIdx = ZCI.ctx.icontent.idx
	ZCI.updateText()

	#prepare result
	res = ODPRes(
		0,
		POCall( None, atm(ATM__ZCI, ZCI) ) #formatting raw input value under POCall format
	)

	#deep debug
	originalZCI.zCtx.deepDbg("Beginning ODP on ZCI \"" + ZCI.textFormat() + '\"')

	#1st group priorization (lowest): CO
	originalZCI.zCtx.deepDbg("ODP-0: Applying 1st group priorization.")
	res.maxStopIdx = ODP_applyGroupPriorization(originalZCI.zCtx, res.maxStopIdx, res.mainPOCall, CO)
	originalZCI.zCtx.deepDbg("ODP-0: Applied 1st group priorization, resulted into " + res.mainPOCall.toStr())

	#2nd group priorization: BO
	originalZCI.zCtx.deepDbg("ODP-0: Applying 2nd group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(originalZCI.zCtx, res.maxStopIdx, res.mainPOCall, BO)
	originalZCI.zCtx.deepDbg("ODP-0: Applied 2nd group priorization, resulted into " + res.mainPOCall.toStr())

	#3rd group priorization: AO + LO
	originalZCI.zCtx.deepDbg("ODP-0: Applying 3rd group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(originalZCI.zCtx, res.maxStopIdx, res.mainPOCall, AO + LO)
	originalZCI.zCtx.deepDbg("ODP-0: Applied 3rd group priorization, resulted into " + res.mainPOCall.toStr())

	#4th group priorization: DO
	originalZCI.zCtx.deepDbg("ODP-0: Applying 4th group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(originalZCI.zCtx, res.maxStopIdx, res.mainPOCall, DO)
	originalZCI.zCtx.deepDbg("ODP-0: Applied 4th group priorization, resulted into " + res.mainPOCall.toStr())

	#5th group priorization: SO (highest treated in ODP)
	originalZCI.zCtx.deepDbg("ODP-0: Applying 5th group priorization (SO)")
	res.maxStopIdx = ODP_applyGroupPriorization(originalZCI.zCtx, res.maxStopIdx, res.mainPOCall, SO, monoOperand=True)
	originalZCI.zCtx.deepDbg("ODP-0: Applied 5th group priorization, resulted into " + res.mainPOCall.toStr())
	originalZCI.zCtx.deepDbg("Ended ODP on ZCI fragment \"" + ZCI.textFormat() + '\"')
	return res








