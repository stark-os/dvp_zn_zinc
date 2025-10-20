# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ffa.py

# -------- FFA RELATED TOOLS --------

#turn FAChain (resulted from 2nd analysis) into a single call
def FAChainToCall(ZCI, scope, FAChain, ZCIKindIfErr_ending, mustEndWithCall):

	#check last element: must be a call
	if mustEndWithCall:
		if lst_last(FAChain).id != ATM__CALL:
			ZCIErr(ZCI, "Last element of field access chain must be a call here" + ZCIKindIfErr_ending)

	#solving each value
	latestIdx          = len(FAChain)-1
	latestIntermediate = None #datItm <<<<<<<<<<<<<<< MUST BE INITED TO null !
	cstFAChain         = False #can only be affected if starting with cst datItm & having only field NAMES
	for i in range(len(FAChain)):
		curElm = FAChain[i]



		# DATITM, FIRST ELEMENT ONLY !

		#datitm directly
		if curElm.id == ATM__DATITM:

			#should never occur
			if latestIntermediate is not None:
				ZCIInt(ZCI, "Got NON-1ST elm of FAChain (resulting from 2nd analysis) as datItm atm => it should only be str or call.")

			#simply set latest intermediate
			latestIntermediate = curElm.dat
			cstFAChain         = curElm.isCst



		# FIELD NAME, NON-FIRST ELEMENT ONLY !

		#field name
		elif curElm.id == ATM__STR:

			#should never occur
			if latestIntermediate is None:
				ZCIInt(ZCI, "1st elm of FAChain (resulting from 2nd analysis) is a str atm => it should only be datItm or call.")

			#generate FA call
			fieldDI = getTypeFieldFromName(ZCI, latestIntermediate.Type, curElm.dat)
			FACall  = call(
				"fa",
				[
					val(ZCI.zCtx.rootTypes[RT__U32], atm(ATM__U32,    latestIntermediate.Type), True),
					val(ZCI.zCtx.rootTypes[RT__REF], atm(ATM__STR,    curElm.dat             ), True),
					val(latestIntermediate.Type,     atm(ATM__DATITM, latestIntermediate     ), latestIntermediate.isCst)
				],
				tgtField.Type
			)

			#create new intermediate
			latestIntermediate = scope.nextDcpDatItmName(fieldDI.Type)

			#decompose, being the last elm => no dcp intermediate, directly add to scope as call (=VFC_VFC)
			if i == latestIdx:
				return atm(ATM__CALL, FACall)

			#decompose, regular case => create asg between new intermediate and generated "fa" call
			scope.exes.append(
				atm(ATM__ASG, asg(
					latestIntermediate,
					val(FACall.retType, atm(ATM__CALL, FACall), cstFAChain)
				))
			)



		# METHOD CALL

		#method call
		elif curElm.id == ATM__CALL:
			curCall = curElm.dat

			#not 1st element in chain => complete cur call with latestIntermediate instance as 1st param (invoker)
			if latestIntermediate is not None:
				lst_insertBefore(curCall.paramVals, 0, val(
					latestIntermediate.Type,
					atm(ATM__DATITM, latestIntermediate),
					False
				))

			#decompose, being the last elm => no dcp intermediate, directly add to scope as call (=VFC_VFC)
			if i == latestIdx:
				return atm(ATM__CALL, curCall)

			#decompose, regular case => create asg between intermediate and cur call
			else:
				latestIntermediate = scope.nextDcpDatItmName(curCall.retType)
				scope.exes.append(
					atm(ATM__ASG, asg(
						latestIntermediate,
						val(curCall.retType, atm(ATM__CALL, curCall), False)
					))
				)



		#should never occur
		else:
			ZCIInt(ZCI, "Got unexpected atm with id " + str(e.id) + " in FAChain.")

	#should never occur
	ZCIInt(ZCI, "Reached end of decomposeFAChain().")
	return None

