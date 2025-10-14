# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value_ODP.py

#ODP
def ODP_readAndSplitByOperators(ZCI, allowedOpes):
	maxStopIdx     = 0
	allowedOpesTxt = "" #only for deep debug

	#deep debug
	if ZCI.zCtx.deepDbgMode:
		allowedOpesTxt = "["
		for o in allowedOpes:
			allowedOpesTxt += OPERATOR_NAMES[o] + ','
		allowedOpesTxt += "]"
		ZCIDeepDbg(ZCI, "ODP-1: Reading & splitting ZCI content \"" + ZCI.txtFormat() + "\" by operators " + allowedOpesTxt)

	#split by operator symbols
	opands            = [] #lst[zci]
	opes              = [] #lst (certainly ubyt but prefer using only undeclinated for enm storage)
	opeIdxes          = []
	opandInitialCtx = ZCI.ctx.copy()
	while not ZCI.reachedEnd() and ZCI.get() in VALUE_CHARSET:



		#checking for symbol
		ope = readSym(ZCI)

		#CASE 1: not a symbol (that can be anything and especially an includer)
		if ope == SYM__NOT_FOUND:
			if ZCI.ctx.icontent.idx in ZCI.pairs.keys():
				ZCI.forwardUntil( ZCI.pairs[ZCI.ctx.icontent.idx] ) #includer? It also belongs to the operand no matter what's inside => skip parsing its content
			ZCI.inc()
			continue

		#CASE 2: '^'
		elif ope == SYM__LXO:
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
		if ope not in allowedOpes:
			ZCI.forward(SYM_LENGTHS[ope])
			continue



		#create operand as a unique ZCI.
		# This is actually a value to be analyzed in further steps.
		# However, to parse it easilly, we store it as a fragment of the ori ZCI (which is, here, a copy of the original but doesn't matter).
		opand          = ZCI.copy(ctxCopy=opandInitialCtx)
		opand.startIdx = opandInitialCtx.icontent.idx #initial context must be at operand beginning index
		opand.stopIdx  = ZCI.ctx.icontent.idx-1       #we are just before operator index, so at operand end index
		opand.strip()

		#special case for negative number notation, we will skip them, it was not an operator
		itWasJustANegSign = False

		#empty 1st operand
		opandIsEmpty = (ZCI.ctx.icontent.idx == opandInitialCtx.icontent.idx)
		if opandIsEmpty:
			if ope == SYM__BSU:
				itWasJustANegSign = True
				ZCIDeepDbg(ZCI, "SPECIAL CASE IN ODP: Found operator BSU without first operand => considerated as negative sign only (no operation).")
			else:
				ZCIErr(ZCI, "Missing first operand to operator " + OPERATOR_NAMES[ope])
		elif ope in MONO_OPERAND:
			ZCIErr(ZCI, "Got too much operands for single operator " + OPERATOR_NAMES[ope] + " (only 1 allowed after symbol).")

		#store operand & operator
		if not itWasJustANegSign:
			opands.append(opand)
			opes.append(ope)
			opeIdxes.append(ZCI.ctx.icontent.idx)
			ZCIDeepDbg(ZCI, "ODP-1: New operator " + OPERATOR_NAMES[ope] + " found, cur operating sequence is " + opSeq(ZCI.ctx.icontent.idx, opands, opes, opeIdxes).toStr())

		#moving after symbol
		ZCI.forward(SYM_LENGTHS[ope])

		#prepare next opand
		opandInitialCtx = ZCI.ctx.copy()

	#set maxStopIdx
	maxStopIdx = ZCI.ctx.icontent.idx - 1

	#no operator found at all => not an operating sequence => return as it was an operating sequence with no operator and only one operand
	if len(opes) == 0:
		ZCIDeepDbg(ZCI, "ODP-1: No operator found at all => Finished with null operating sequence.")
		return opSeq(maxStopIdx, None, None, None)

	#last operand cannot be empty
	if ZCI.ctx.icontent.idx == opandInitialCtx.icontent.idx:
		lastOpe = opes[-1]
		if lastOpe in MONO_OPERAND:
			ZCIErr(ZCI, "Missing first (and only) operand to single operator " + OPERATOR_NAMES[lastOpe])
		else:
			ZCIErr(ZCI, "Missing second operand to operator " + OPERATOR_NAMES[lastOpe])

	#create last operand
	opand          = ZCI.copy(ctxCopy=opandInitialCtx)
	opand.startIdx = opandInitialCtx.icontent.idx
	opand.stopIdx  = ZCI.ctx.icontent.idx - 1
	opand.strip()

	#add last operand
	opands.append(opand)
	ZCIDeepDbg(ZCI, "ODP-1: Last operand added, final operating sequence is " + opSeq(maxStopIdx, opands, opes, opeIdxes).toStr())

	#deep debug
	ZCIDeepDbg(ZCI, "ODP-1: Finished reading & splitting ZCI content \"" + ZCI.txtFormat() + "\" by operators " + allowedOpesTxt)
	return opSeq(maxStopIdx, opands, opes, opeIdxes)



#progressive priorizing equivalent for mono operand operators
def monoOperandOpSeqConcatenation(zCtx, curOpSeq):
	lastOpand = curOpSeq.opands.pop()

	#check other operands (not necessary, internal consistency check only)
	for a in curOpSeq.opands:
		if a.stopIdx - a.startIdx >= 0:
			zCtx.internal("Non-empty operand found in mono-operand operating sequence (last element excepted).")

	#deep debug: before
	zCtx.deepDbg("ODP-2: Applying mono-operand operating sequence concatenation on " + curOpSeq.toStr())

	#associate each operand to its operator
	res = POCall(
		None,
		atm(ATM__ZCI, lastOpand)
	)
	cur = res
	while len(curOpSeq.opes) != 0:
		cur.name   = OPERATOR_NAMES[curOpSeq.opes.pop(0)]
		cur.opeIdx = curOpSeq.opeIdxes.pop(0)
		cur.opand2 = atm(
			ATM__POCALL,
			POCall(None, cur.opand2)
		)
		cur = cur.opand2.dat

	#deep debug: after
	zCtx.deepDbg("ODP-2: Mono-operand operating sequence concatenation resulted into the following POCall " + res.toStr())
	return res



#transform an operating sequence into a single POCall (destroying the given opSeq!)
def progressivePriorizing(zCtx, curOpSeq, monoOpand): #WARNING! DO NOT USE WITH SO !!!
	if len(curOpSeq.opands) == 0:
		zCtx.internal("Got no operand in operating sequence when running progressive priorizing.")

	#mono-operand operating sequence => redirect to the adapted equivalent
	if monoOpand:
		return monoOperandOpSeqConcatenation(zCtx, curOpSeq)

	#deep debug: before
	zCtx.deepDbg("ODP-2: Applying progressive priorizing on operating sequence " + curOpSeq.toStr())

	#first element (we must keep track of it)
	res = POCall(
		None,
		atm(ATM__ZCI, curOpSeq.opands.pop())
	)
	cur = res

	#for each remaining operand, make function calls (Potential Operator Call)
	while len(curOpSeq.opands) != 0:
		cur.name   = OPERATOR_NAMES[curOpSeq.opes.pop()]
		cur.opeIdx = curOpSeq.opeIdxes.pop()
		cur.opand1 = atm(
			ATM__POCALL,
			POCall(
				None,
				atm(ATM__ZCI, curOpSeq.opands.pop())
			)
		)
		cur = cur.opand1.dat

	#deep debug: after
	zCtx.deepDbg("ODP-2: Progressive priorizing resulted into the following POCall " + res.toStr())
	return res



#group priorizing
# This function is higly important! It applies group priorization on every value that can be found in a POCall.
def ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall, opesAllowed, monoOpand=False):

	#1st operand
	if curPOCall.opand1 is not None:

		#leaf => apply here
		if curPOCall.opand1.id == ATM__ZCI:
			oriCtx   = curPOCall.opand2.dat.ctx.copy()
			curOpSeq = ODP_readAndSplitByOperators(curPOCall.opand1.dat, opesAllowed)

			#no ope found => restore original ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
			if curOpSeq.opes is None:
				curPOCall.opand1.dat.resetCtx(oriCtx)
				curPOCall.opand1.dat.stopIdx = curOpSeq.stopIdx
				curPOCall.opand1.dat.strip()

			#ope found => progressive priorizing
			else:
				curPOCall.opand1 = atm(
					ATM__POCALL,
					progressivePriorizing(zCtx, curOpSeq, monoOpand)
				)

			#update maxStopIdx
			if maxStopIdx < curOpSeq.stopIdx:
				maxStopIdx = curOpSeq.stopIdx

		#tree => check deeper
		elif curPOCall.opand1.id == ATM__POCALL:
			maxStopIdx = ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall.opand1.dat, opesAllowed, monoOpand=monoOpand)

	#2nd operand
	if curPOCall.opand2 is not None:

		#leaf => apply here
		if curPOCall.opand2.id == ATM__ZCI:
			oriCtx  = curPOCall.opand2.dat.ctx.copy()
			curOpSeq = ODP_readAndSplitByOperators(curPOCall.opand2.dat, opesAllowed)

			#no ope found => restore origin ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
			if curOpSeq.opes is None:
				curPOCall.opand2.dat.resetCtx(oriCtx)
				curPOCall.opand2.dat.stopIdx = curOpSeq.stopIdx
				curPOCall.opand2.dat.strip()

			#ope found => progressive priorizing
			else:
				curPOCall.opand2 = atm(
					ATM__POCALL,
					progressivePriorizing(zCtx, curOpSeq, monoOpand)
				)

			#update maxStopIdx
			if maxStopIdx < curOpSeq.stopIdx:
				maxStopIdx = curOpSeq.stopIdx

		#tree => check deeper
		elif curPOCall.opand2.id == ATM__POCALL:
			maxStopIdx = ODP_applyGroupPriorization(zCtx, maxStopIdx, curPOCall.opand2.dat, opesAllowed, monoOpand=monoOpand)

	#return it to know until where ODP has been (so we know where to continue reading after that Value)
	return maxStopIdx



#entry point for Operation Decomposition Process (ODP)
def ODP(oriZCI):
	ZCI          = oriZCI.copy()
	ZCI.startIdx = ZCI.ctx.icontent.idx
	ZCI.updateTxt()

	#prepare result
	res = ODPRes(
		0,
		POCall( None, atm(ATM__ZCI, ZCI) ) #formatting raw input value under POCall format
	)

	#deep debug
	oriZCI.zCtx.deepDbg("Beginning ODP on ZCI \"" + ZCI.txtFormat() + '\"')

	#1st group priorization (lowest): CO
	oriZCI.zCtx.deepDbg("ODP-0: Applying 1st group priorization.")
	res.maxStopIdx = ODP_applyGroupPriorization(oriZCI.zCtx, res.maxStopIdx, res.mainPOCall, CO)
	oriZCI.zCtx.deepDbg("ODP-0: Applied 1st group priorization, resulted into " + res.mainPOCall.toStr())

	#2nd group priorization: BO
	oriZCI.zCtx.deepDbg("ODP-0: Applying 2nd group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(oriZCI.zCtx, res.maxStopIdx, res.mainPOCall, BO)
	oriZCI.zCtx.deepDbg("ODP-0: Applied 2nd group priorization, resulted into " + res.mainPOCall.toStr())

	#3rd group priorization: AO + LO
	oriZCI.zCtx.deepDbg("ODP-0: Applying 3rd group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(oriZCI.zCtx, res.maxStopIdx, res.mainPOCall, AO + LO)
	oriZCI.zCtx.deepDbg("ODP-0: Applied 3rd group priorization, resulted into " + res.mainPOCall.toStr())

	#4th group priorization: DO
	oriZCI.zCtx.deepDbg("ODP-0: Applying 4th group priorization")
	res.maxStopIdx = ODP_applyGroupPriorization(oriZCI.zCtx, res.maxStopIdx, res.mainPOCall, DO)
	oriZCI.zCtx.deepDbg("ODP-0: Applied 4th group priorization, resulted into " + res.mainPOCall.toStr())

	#5th group priorization: SO (highest treated in ODP)
	oriZCI.zCtx.deepDbg("ODP-0: Applying 5th group priorization (SO)")
	res.maxStopIdx = ODP_applyGroupPriorization(oriZCI.zCtx, res.maxStopIdx, res.mainPOCall, SO, monoOpand=True)
	oriZCI.zCtx.deepDbg("ODP-0: Applied 5th group priorization, resulted into " + res.mainPOCall.toStr())
	oriZCI.zCtx.deepDbg("Ended ODP on ZCI fragment \"" + ZCI.txtFormat() + '\"')
	return res








