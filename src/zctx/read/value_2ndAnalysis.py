# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value_2ndAnalysis.py

	#second analysis: number parsing (integers & floating point)
	def parseLiteralIntOrFloat(self, ZCI):
		c = ZCI.get()



		#STEP 1: Identify what kind of notation is used

		#prepare for identification
		resultText       = ""
		resultDigitPower = 0
		resultIsNegative = False
		resultType       = None #type
		resultAtmID      = 0 #no initial value is preferable <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

		#negativity
		if c == '-':
			resultIsNegative = True
			if ZCI.inc():
				self.unknownValueErrorIn2ndAnalysis(ZCI) #lonely minus sign => invalid
			c = ZCI.get()

		#first character is important (in all cases, must be a decimal digit)
		if c in STR__DECIMAL:
			resultType  = self.rootTypes[RT__S4] #default case, considering an S4
			resultAtmID = ATM__S4

			#non-zero => literal decimal
			if c != '0':
				resultDigitPower = 10
				resultText       = readNbrAsText(ZCI, STR__DECIMAL)

			#zero => can be anything
			else:
				if ZCI.inc():
					return value(self.rootTypes[RT__S4], atm(ATM__S4, 0)) #lonely '0'

				#binary, octal, hexadecimal
				c = ZCI.get()
				if c == 'b':
					if ZCI.inc():
						self.ZCIError("Incomplete literal number given, binary notation must be followed by a digit sequence.")
					resultDigitPower = 2
					resultText       = readNbrAsRawText(ZCI, STR__BINARY)
				elif c == 'o':
					if ZCI.inc():
						self.ZCIError("Incomplete literal number given, octal notation must be followed by a digit sequence.")
					resultDigitPower = 8
					resultText       = readNbrAsRawText(ZCI, STR__OCTAL)
				elif c == 'x':
					if ZCI.inc():
						self.ZCIError("Incomplete literal number given, hexadecimal notation must be followed by a digit sequence.")
					resultDigitPower = 16
					resultText       = readNbrAsRawText(ZCI, STR__HEXADECIMAL_LOWERCASE)
				else:
					self.ZCIError("Invalid character '" + c + "' given for literal numeric notation (allowed are 'b', 'o', 'x').")

			#weird cases: negative sign on non-decimal
			if resultIsNegative and resultDigitPower != 10:
				self.ZCIError("Cannot apply negativity on a non-decimal literal notation.")



			#STEP 2: Check terminator to get correct result type

			#read terminator if any
			if c == 'u':
				ZCI.inc()
				if c == 's':
					resultType  = self.rootTypes[RT__U2]
					resultAtmID = ATM__U2
					ZCI.inc()
				elif c == 'l':
					resultType  = self.rootTypes[RT__U8]
					resultAtmID = ATM__U8
					ZCI.inc()
				else:
					resultType  = self.rootTypes[RT__U4]
					resultAtmID = ATM__U4
			elif c == 's':
				resultType  = self.rootTypes[RT__S2]
				resultAtmID = ATM__S2
				ZCI.inc()
			elif c == 'l':
				resultType  = self.rootTypes[RT__S8]
				resultAtmID = ATM__S8
				ZCI.inc()

			#having unsigned terminator on negative value
			if resultIsNegative and resultAtmID in (ATM__U2, ATM__U4, ATM__U8):
				self.ZCIError("Cannot have terminator on negative value.")



			#STEP 3: Check digit number depending on expected ranges

			#32b arch does not allow long values (64b)
			if self.cpl.options["ARCH"] != "64" and resultAtmID in (ATM__S8, ATM__U8):
				self.ZCIError("Cannot have 64b values when targetting 32b architecture (8 bytes integer).")

			#check if too much digits have been given: binary
			if resultDigitPower == 2:
				if resultAtmID in (ATM__S2, ATM__U2):
					if len(resultText) > MAX_BINARY_DIGITS_ALLOWED__U2:
						self.ZCIError(ZCI, "Too much digits given in 2 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U2 + " allowed).")
				elif resultAtmID in (ATM__S4, ATM__U4):
					if len(resultText) > MAX_BINARY_DIGITS_ALLOWED__U4:
						self.ZCIError(ZCI, "Too much digits given in 4 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U4 + " allowed).")
				else: #if resultAtmID in (ATM__S8, ATM__U8):
					if len(resultText) > MAX_BINARY_DIGITS_ALLOWED__U8:
						self.ZCIError(ZCI, "Too much digits given in 8 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U8 + " allowed).")

			#check if too much digits have been given: octal
			elif resultDigitPower == 8:
				if resultAtmID in (ATM__S2, ATM__U2):
					if len(resultText) > MAX_OCTAL_DIGITS_ALLOWED__U2:
						self.ZCIError(ZCI, "Too much digits given in 2 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U2 + " allowed).")
				elif resultAtmID in (ATM__S4, ATM__U4):
					if len(resultText) > MAX_OCTAL_DIGITS_ALLOWED__U4:
						self.ZCIError(ZCI, "Too much digits given in 4 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U4 + " allowed).")
				else: #if resultAtmID in (ATM__S8, ATM__U8):
					if len(resultText) > MAX_OCTAL_DIGITS_ALLOWED__U8:
						self.ZCIError(ZCI, "Too much digits given in 8 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U8 + " allowed).")

			#check if too much digits have been given: hexadecimal
			elif resultDigitPower == 16:
				if resultAtmID in (ATM__S2, ATM__U2):
					if len(resultText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U2:
						self.ZCIError(ZCI, "Too much digits given in 2 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U2 + " allowed).")
				elif resultAtmID in (ATM__S4, ATM__U4):
					if len(resultText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U4:
						self.ZCIError(ZCI, "Too much digits given in 4 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U4 + " allowed).")
				else: #if resultAtmID in (ATM__S8, ATM__U8):
					if len(resultText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U8:
						self.ZCIError(ZCI, "Too much digits given in 8 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U8 + " allowed).")

			#check if too much digits have been given: decimal
			else:
				if resultAtmID == ATM__S2:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__S2:
						self.ZCIError(ZCI, "Too much digits given in 2 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S2 + " allowed).")
				elif resultAtmID == ATM__S4:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__S4:
						self.ZCIError(ZCI, "Too much digits given in 4 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S4 + " allowed).")
				elif resultAtmID == ATM__S8:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__S8:
						self.ZCIError(ZCI, "Too much digits given in 8 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S8 + " allowed).")
				elif resultAtmID == ATM__U2:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__U2:
						self.ZCIError(ZCI, "Too much digits given in 2 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U2 + " allowed).")
				elif resultAtmID == ATM__U4:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__U4:
						self.ZCIError(ZCI, "Too much digits given in 4 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U4 + " allowed).")
				else: #if resultAtmID == ATM__U8:
					if len(resultText) > MAX_DECIMAL_DIGITS_ALLOWED__U8:
						self.ZCIError(ZCI, "Too much digits given in 8 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U8 + " allowed).")



			#STEP 3: finally, compute the actual value

			#compute value
			resultNbr = 0 #here, we must use a ulng for storage in Z <<<<<<<<<<<<<<<<<<<
			lastIndex = len(resultText)-1
			for r in range(len(resultText)):
				resultNbr += chr_halfHex_toS1(resultText[r]) * (resultDigitPower**(lastIndex-r))



			#STEP 4: Floating point possibility

			#only for decimal without terminator
			if resultDigitPower == 10 and resultAtmID == ATM__S4 and ZCI.get() == '.':
				resultAsFloat = float(resultNbr) #<<<<<<<<<<<<<<<<<<<<<<<<<<< switch from ulng to dbl storage
				resultType    = self.rootTypes[RT__F4]
				resultAtmID   = ATM__F4

				#nothing after point => incomplete
				if ZCI.inc():
					self.ZCIError("Incomplete floating point notation, missing value after point.")

				#read after point
				afterPoint = readNbrAsRawText(ZCI, STR__DECIMAL)
				lastIndex  = len(resultText)-1
				for r in range(len(resultText)):
					resultFloatingNbr += chr_dec_toS1(afterPoint[r]) * 1/(10**(lastIndex-r))

				#long float terminator
				if ZCI.get() == 'l':
					ZCI.inc()
					resultType  = self.rootTypes[RT__F8]
					resultAtmID = ATM__F8

					#32b arch does not allow long values (64b)
					if self.cpl.options["ARCH"] != "64":
						self.ZCIError("Cannot have 64b values when targetting 32b architecture (8 bytes floating point).")



				#FINAL STEP: Apply negativity & return

				#apply negativity
				if resultIsNegative:
					resultAsFloat = -1.0*resultAsFloat

				#end of value parsing (floating point)
				return value(resultType, atm(resultAtmID, resultFloatingNbr))

			#end of value parsing (integer)
			if resultIsNegative:
				return value(resultType, atm(resultAtmID, -1*resultNbr)) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Can be optimized in a single return in python, but in Z it may be better this way since resultNbr is a ULNG
			return value(resultType, atm(resultAtmID, resultNbr))

		#no literal number found
		return None



	#2nd analysis
	def unknownValueErrorIn2ndAnalysis(self, ZCI):
		self.ZCIError(ZCI, "Unknown value given (not respecting any format supported by VAP in 2nd analysis).")

	def secondAnalysis(self, ZCI, vap2info):
		self.ZCIDeepDebug(ZCI, "2nd analysis: Reading ZCI fragment " + ZCI.textFormat() + " to apply second analysis on it.")
		result = None
		c = ZCI.get()



		# I] LITERAL: COMMON DATA STRUCTURE SHORTCUT

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
			self.ZCIDeepDebug(ZCI, "Start reading sub values sequence.", printLine=False)
			while True:

				#read subvalue
				self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
				self.ZCIDeepDebug(ZCI, "=> Reading " + str(len(subValues)+1) + "th sub value.", printLine=False)
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

			#debug
			self.ZCIDeepDebug(ZCI, "Stop reading sub values sequence.")

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
				self.ZCIDeepDebug(ZCI, "Reading hexadecimal value in multi-bytes notation.")
				if ZCI.inc():
					self.ZCIError(ZCI, "Missing content after multiple-bytes notation.")

				#prepare sequence
				sequence = [] #lst[value]
				while ZCI.get() in HEX_DIGITS_LOWERCASE:
					sequence.append(
						value(self.rootTypes[RT__BYT], atm(ATM__S1, self.readHexByte(ZCI)) )
					)
					if ZCI.inc():
						break

				#missing characters
				if len(sequence) == 0:
					self.ZCIError(ZCI, "Missing valid hexadecimal characters in multi-bytes notation.")

				#finish result
				result = value(self.rootTypes[RT__PTR], atm(ATM__LST, sequence))
				self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in MULTI-BYTE NOTATION " + result.toStr())
				return result

			#single-byte sequence
			self.ZCIDeepDebug(ZCI, "Reading hexadecimal value in single-byte notation.")
			result = value(
				self.rootTypes[RT__S1],
				atm(ATM__BYT, self.readHexByte(ZCI))
			)
			ZCI.inc()
			self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in SINGLE-BYTE NOTATION " + result.toStr())
			return result



		# III] LITERAL: INTEGERS & FLOATING POINT

		#parsing is quite complex => has been taken appart in another method
		v = self.parseLiteralIntOrFloat(ZCI)
		if v is not None:
			return v

		#unknown value format
		self.unknownValueErrorIn2ndAnalysis(ZCI)



	def secondAnalysisIncludingFOs(self, ZCI, vap2info):
		starter = ZCI.get()



		# 1) PROCESSING FOs: MONO-OPERAND

		#size (FSZ)
		if starter == '#':
			self.ZCIDeepDebug(ZCI, "2nd analysis: Processing FSZ operator.")
			ZCI.inc()
			Type = self.readType(ZCI, vap2info.ZCIKindIfError)

			#get size
			if Type.commonDcnData.nature != NATURE__PRIMITIVE:
				size = Type.commonDcnData.stcSize
			else:
				size = Type.size

			#result
			self.ZCIDeepDebug("2nd analysis: FSZ resulted into fsz(" + unprefixize(Type.name) + ") = " + str(size))
			if self.cpl.options["ARCH"] == 64:
				return value(self.rootTypes[RT__U8], atm(ATM__U8, size))
			return value(self.rootTypes[RT__U4], atm(ATM__U4, size))

		#reference (FRF)
		if starter == '@':
			self.ZCIDeepDebug(ZCI, "2nd analysis: Processing FRF operator.")
			ZCI.inc()

			#target data item
			di = self.tryReadDataItemIncludingFields(ZCI, vap2info.scope)
			if di is None:
				self.ZCIError(ZCI, "Missing or invalid data item given for reference operator '@' (FRF).")

			#result
			self.ZCIDeepDebug("2nd analysis: FRF resulted into call to frf()") #<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
			return value(self.rootTypes[RT__PTR], atm(ATM__PTR, 0))           #<<<<<<<<<<<<<<<<<<<<<<<<<<<<



		# 2) SECOND ANALYSIS WITHOUT END-CHECK

		#read value but don't care if there are still things to analyze
		result = self.secondAnalysis(ZCI, vap2info) #after this, ZCI index is right AFTER the value read
		self.optionnalBlanks(ZCI, None)

		#nothing left to analyze
		if ZCI.reachedEnd():
			return result



		# 3) PROCESSING FOs: 2-OPERANDS

		#casht (FCA)
		if ZCI.get() == '$':
			ZCI.inc()
			self.optionnalBlanks(ZCI, None)

			#read explicit type
			self.ZCIDeepDebug(ZCI, "2nd analysis: Processing FCA operator on value " + result.toStr())
			Type = self.readType(ZCI, vap2info.ZCIKindIfError)

			#overwrite result type
			result.Type = Type
			self.ZCIDeepDebug("2nd analysis: FCA operator applied type " + unprefixize(Type.name) + " on value " + result.toStr())

		#field access (FFA)
		#else:
			#result = self.readFields(ZCI, ): #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
			#return 

		#too much content in VALUE ZCE
		if not ZCI.reachedEnd():
			self.ZCIError(ZCI, "Too much elements in VALUE ZCE (2nd analysis parsing).")

		#success
		return result



	#RECURSIVE entry point for 2nd analysis (applying it on the whole ODP result)
	def applySecondAnalysis(self, currentPOCall, originalZCI, vap2info): #originalZCI only used for error accuracy

		#process 1st operand
		firstOperandValue = None
		if currentPOCall.firstOperand is not None:

			#recursively solving children before
			if currentPOCall.firstOperand.id == ATM__POCALL:
				firstOperandValue = self.applySecondAnalysis(currentPOCall.firstOperand.data, originalZCI, vap2info)

			#UNITARY entry point for 2nd analysis
			elif currentPOCall.firstOperand.id == ATM__ZCI:
				firstOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.firstOperand.data, vap2info)

			#should never happen
			else:
				self.internal("Found a non-POCall & non-ZCI atom in ODP result.")

		#process 2nd operand
		secondOperandValue = None
		if currentPOCall.secondOperand is not None:

			#recursively solving children before
			if currentPOCall.secondOperand.id == ATM__POCALL:
				secondOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.secondOperand.data, originalZCI, vap2info)

			#UNITARY entry point for 2nd analysis
			elif currentPOCall.secondOperand.id == ATM__ZCI:
				secondOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.secondOperand.data, vap2info)

			#should never happen
			else:
				self.internal("Found a non-POCall & non-ZCI atom in ODP result.")



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
			self.ZCIError(originalZCI, "No operator \"" + unprefixize(f.name) + "\" declared yet.")

		#result
		return value(
			matchingFunction.retType,
			atm(ATM__CALL, call(operatorFullName, params))
		)



	#value analysis process, main entry point (VAP)
	def readValue(self, ZCI, ZCIKindIfError, scope, cstOnly=False):
		self.ZCIDeepDebug(ZCI, "Reading value.")

		#1st analysis: ODP
		firstAnalysisResult = self.ODP(ZCI)
		ZCI.forward( firstAnalysisResult.maxStopIndex - ZCI.ctx.icontent.index +1)

		#apply 2nd analysis recursively in ODP result
		secondAnalysisResult = self.applySecondAnalysis(firstAnalysisResult.mainPOCall, ZCI, vap2(ZCIKindIfError, scope, cstOnly)) #here, ZCI is given for error messages only
		self.ZCIDeepDebug(ZCI, "Ended reading value with result :" + secondAnalysisResult.toStr())
		return secondAnalysisResult




