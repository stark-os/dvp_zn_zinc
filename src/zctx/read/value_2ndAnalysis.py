# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/value_2ndAnalysis.py

#second analysis: number parsing (integers & floating point)
def parseLiteralIntOrFloat(ZCI):
	c = ZCI.get()



	#STEP 1: Identify what kind of notation is used

	#prepare for identification
	resText       = ""
	resDigitPower = 0
	resIsNegative = False
	resType       = TYPE_ID__UNKNOWN
	resAtmID      = 0 #no initial value is preferable <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

	#negativity
	if c == '-':
		resIsNegative = True
		if ZCI.inc():
			unknownValueErrIn2ndAnalysis(ZCI) #lonely minus sign => invalid
		c = ZCI.get()

	#first character is important (in all cases, must be a decimal digit)
	if c in STR__DECIMAL:
		ZCIDeepDbg(ZCI, "2nd analysis: Integer or float detected.", prtLine=False)
		resType  = ZCI.zCtx.rootTypes[RT__S32] #default case, considering an S32
		resAtmID = ATM__S32

		#non-zero => literal decimal
		if c != '0':
			resDigitPower = 10
			resText       = readNbrAsText(ZCI, STR__DECIMAL)

		#zero => can be anything
		else:
			if ZCI.inc(): #lonely '0'
				return value(
					ZCI.zCtx.rootTypes[RT__S32],
					atm(ATM__S32, 0),
					True
				)

			#binary, octal, hexadecimal
			c = ZCI.get()
			if c == 'b':
				if ZCI.inc():
					ZCIErr("Incomplete literal number given, binary notation must be followed by a digit sequence.")
				resDigitPower = 2
				resText       = readNbrAsRawText(ZCI, STR__BINARY)
			elif c == 'o':
				if ZCI.inc():
					ZCIErr("Incomplete literal number given, octal notation must be followed by a digit sequence.")
				resDigitPower = 8
				resText       = readNbrAsRawText(ZCI, STR__OCTAL)
			elif c == 'x':
				if ZCI.inc():
					ZCIErr("Incomplete literal number given, hexadecimal notation must be followed by a digit sequence.")
				resDigitPower = 16
				resText       = readNbrAsRawText(ZCI, STR__HEXADECIMAL_LOWERCASE)
			else:
				ZCIErr("Invalid character '" + c + "' given for literal numeric notation (allowed are 'b', 'o', 'x').")

		#weird cases: negative sign on non-decimal
		if resIsNegative and resDigitPower != 10:
			ZCIErr("Cannot apply negativity on a non-decimal literal notation.")



		#STEP 2: Check terminator to get correct res type

		#read terminator if any
		c = ZCI.get()
		if c == 'u':
			ZCI.inc()
			if c == 's':
				resType  = ZCI.zCtx.rootTypes[RT__U16]
				resAtmID = ATM__U16
				ZCI.inc()
			elif c == 'l':
				resType  = ZCI.zCtx.rootTypes[RT__U64]
				resAtmID = ATM__U64
				ZCI.inc()
			else:
				resType  = ZCI.zCtx.rootTypes[RT__U32]
				resAtmID = ATM__U32
		elif c == 's':
			resType  = ZCI.zCtx.rootTypes[RT__S16]
			resAtmID = ATM__S16
			ZCI.inc()
		elif c == 'l':
			resType  = ZCI.zCtx.rootTypes[RT__S64]
			resAtmID = ATM__S64
			ZCI.inc()

		#having unsigned terminator on negative value
		if resIsNegative and resAtmID in (ATM__U16, ATM__U32, ATM__U64):
			ZCIErr("Cannot have terminator on negative value.")



		#STEP 3: Check digit number depending on expected ranges

		#32b arch does not allow 64b values => AUTO CASHT
		if ZCI.zCtx.cpl.opts["ARCH"] != "64":
			if resAtmID in ATM__S64:
				ZCIWrn(ZCI, "Auto cashting long signed integer value into 32b (targetting 32b arch).")
				resAtmID = ATM__S32
				resType  = ZCI.zCtx.rootTypes[RT__S32]
			if resAtmID in ATM__U64:
				ZCIWrn(ZCI, "Auto cashting long unsigned integer value into 32b (targetting 32b arch).")
				resAtmID = ATM__U32
				resType  = ZCI.zCtx.rootTypes[RT__U32]

		#check if too much digits have been given: binary
		if resDigitPower == 2:
			if resAtmID in (ATM__S16, ATM__U16):
				if len(resText) > MAX_BINARY_DIGITS_ALLOWED__U16:
					ZCIErr(ZCI, "Too much digits given in 2 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U16 + " allowed).")
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_BINARY_DIGITS_ALLOWED__U32:
					ZCIErr(ZCI, "Too much digits given in 4 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U32 + " allowed).")
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_BINARY_DIGITS_ALLOWED__U64:
					ZCIErr(ZCI, "Too much digits given in 8 bytes literal binary value (maximum " + MAX_BINARY_DIGITS_ALLOWED__U64 + " allowed).")

		#check if too much digits have been given: octal
		elif resDigitPower == 8:
			if resAtmID in (ATM__S16, ATM__U16):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U16:
					ZCIErr(ZCI, "Too much digits given in 2 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U16 + " allowed).")
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U32:
					ZCIErr(ZCI, "Too much digits given in 4 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U32 + " allowed).")
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U64:
					ZCIErr(ZCI, "Too much digits given in 8 bytes literal octal value (maximum " + MAX_OCTAL_DIGITS_ALLOWED__U64 + " allowed).")

		#check if too much digits have been given: hexadecimal
		elif resDigitPower == 16:
			if resAtmID in (ATM__S16, ATM__U16):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U16:
					ZCIErr(ZCI, "Too much digits given in 2 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U16 + " allowed).")
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U32:
					ZCIErr(ZCI, "Too much digits given in 4 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U32 + " allowed).")
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U64:
					ZCIErr(ZCI, "Too much digits given in 8 bytes literal hexadecimal value (maximum " + MAX_HEXADECIMAL_DIGITS_ALLOWED__U64 + " allowed).")

		#check if too much digits have been given: decimal
		else:
			if resAtmID == ATM__S16:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S16:
					ZCIErr(ZCI, "Too much digits given in 2 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S16 + " allowed).")
			elif resAtmID == ATM__S32:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S32:
					ZCIErr(ZCI, "Too much digits given in 4 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S32 + " allowed).")
			elif resAtmID == ATM__S64:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S64:
					ZCIErr(ZCI, "Too much digits given in 8 bytes literal signed decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__S64 + " allowed).")
			elif resAtmID == ATM__U16:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U16:
					ZCIErr(ZCI, "Too much digits given in 2 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U16 + " allowed).")
			elif resAtmID == ATM__U32:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U32:
					ZCIErr(ZCI, "Too much digits given in 4 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U32 + " allowed).")
			else: #if resAtmID == ATM__U64:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U64:
					ZCIErr(ZCI, "Too much digits given in 8 bytes literal unsigned decimal value (maximum " + MAX_DECIMAL_DIGITS_ALLOWED__U64 + " allowed).")



		#STEP 3: finally, compute the actual value

		#compute value
		resNbr  = 0 #here, we must use a ulng for storage in Z <<<<<<<<<<<<<<<<<<<
		lastIdx = len(resText)-1
		for r in range(len(resText)):
			resNbr += chr_halfHex_toS8(resText[r]) * (resDigitPower**(lastIdx-r))



		#STEP 4: Floating point possibility

		#only for decimal without terminator
		if resDigitPower == 10 and resAtmID == ATM__S32 and c == '.':
			resAsFloat = float(resNbr) #<<<<<<<<<<<<<<<<<<<<<<<<<<< switch from ulng to dbl storage
			resType    = ZCI.zCtx.rootTypes[RT__F32]
			resAtmID   = ATM__F32

			#nothing after point => incomplete
			if ZCI.inc():
				ZCIErr("Incomplete floating point notation, missing value after point.")

			#read after point
			afterPoint = readNbrAsRawText(ZCI, STR__DECIMAL)
			lastIdx    = len(resText)-1
			for r in range(len(resText)):
				resFloatingNbr += chr_dec_toS8(afterPoint[r]) * 1/(10**(lastIdx-r))

			#long float terminator
			if ZCI.get() == 'l':
				ZCI.inc()
				resType  = ZCI.zCtx.rootTypes[RT__F64]
				resAtmID = ATM__F64

				#32b arch does not allow 64b values => AUTO CASHT
				if ZCI.zCtx.cpl.opts["ARCH"] != "64":
					ZCIWrn(ZCI, "Auto cashting long float value into 32b float (targetting 32b arch).")
					resType  = ZCI.zCtx.rootTypes[RT__F32]
					resAtmID = ATM__F32



			#FINAL STEP: Apply negativity & return

			#apply negativity
			if resIsNegative:
				resAsFloat = -1.0*resAsFloat

			#end of value parsing (floating point)
			return value(resType, atm(resAtmID, resFloatingNbr), True)

		#end of value parsing (integer)
		if resIsNegative:
			return val(resType, atm(resAtmID, -1*resNbr), True) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Can be optimized in a single return in python, but in Z it may be better this way since resNbr is a ULNG
		return val(resType, atm(resAtmID, resNbr), True)

	#no literal number found
	return None



#2nd analysis
def unknownValueErrIn2ndAnalysis(ZCI):
	ZCIErr(ZCI, "Unknown value given (2nd analysis, not respecting any format supported by VAP).")

def secondAnalysis(ZCI, v2i):
	ZCIDeepDbg(ZCI, "2nd analysis: Reading ZCI fragment \"" + ZCI.txtFormat() + "\" to apply second analysis on it.")
	res = None
	c = ZCI.get()



	# I] LITERAL: COMMON DATA STRUCTURE SHORTCUT

	#map starter symbol
	tgtMap = False
	if c == ':':
		if ZCI.inc():
			unknownValueErrIn2ndAnalysis(ZCI)
		tgtMap = True
		ZCIDeepDbg(ZCI, "2nd analysis: Potential map-type detected.", prtLine=False)

	#starting with includer
	if c in ('(', '[', '{'):
		ZCIDeepDbg(ZCI, "2nd analysis: Includer detected => Potentially targetting tab,lst,fly,fmap,mmap.", prtLine=False)
		#Seems similar to check in the whole INCLUDERS.keys() but this is not related to these actually.
		#We are specificly targetting these 3 and not because they are includer keys but because we have specific pattern associated to them.
		tgtType_inside = None #for maps only
		if c == '(':
			if tgtMap:
				tgtType        = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__FMAP, v2i.ZCIKindIfErr)
				tgtType_inside = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__TAB,  v2i.ZCIKindIfErr) #require 2 tab for fmap initialization
			else:
				tgtType = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__TAB, v2i.ZCIKindIfErr)
		elif c == '[':
			if tgtMap:
				tgtType        = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__MMAP, v2i.ZCIKindIfErr)
				tgtType_inside = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__LST,  v2i.ZCIKindIfErr) #require 2 lst for mmap initialization
			else:
				tgtType = createFakeZCIAndReadCommonType(ZCI, TYPE_FULLNAME__LST, v2i.ZCIKindIfErr)
		elif c == '{':
			if tgtMap:
				ZCIErr(ZCI, "2nd analysis: Associative notation cannot be set to braces includer (\":{...}\" is linked to nothing).")
			tgtType = createFakeZCIAndTryReadingCommonType(ZCI, TYPE_FULLNAME__FLY, v2i.ZCIKindIfErr)

		#init limits
		peerIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		tgtEnd  = ZCI.ctx.icontent.s[peerIdx]
		ZCI.inc()

		#read subvalues as long as we have some (separated by comas)
		subVals        = [] #lst[val]
		subVals_inside = [] #for maps
		ZCIDeepDbg(ZCI, "2nd analysis: Start reading sub values sequence.", prtLine=False)
		while True:

			#read subvalue
			optionalBlanks(ZCI, None, BLANKS_EXTENDED)
			ZCIDeepDbg(ZCI, "2nd analysis: => Reading " + str(len(subVals)+1) + "th sub value.", prtLine=False)
			subVals.append( readVal(ZCI, v2i.ZCIKindIfErr, v2i.scope, v2i.cstOnly) )

			#read second subValue (for maps only)
			if tgtMap:

				#colon separator required
				optionalBlanks(ZCI, None, BLANKS_EXTENDED)
				next = ZCI.get()
				if next != ':':
					ZCIErr(ZCI, "2nd analysis: Invalid element " + next + " given in associative sequence (expected colon separator ':').")
				ZCI.inc()

				#read a second subvalue (require a couple for association)
				optionalBlanks(ZCI, None, BLANKS_EXTENDED)
				subVals_inside.append( readVal(ZCI, v2i.ZCIKindIfErr, v2i.scope, v2i.cstOnly) )

			#look for end separator
			optionalBlanks(ZCI, None, BLANKS_EXTENDED)
			next = ZCI.get()
			if next == tgtEnd:
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInternal(ZCI, "2nd analysis: Ending value sequence inside includer with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			if next != ',':
				ZCIErr(ZCI, "2nd analysis: Invalid element " + next + " given in value sequence between includers (expected coma separator ',' or closing includer '" + targettedEnd + "').")
			ZCI.inc()

		#debug
		ZCIDeepDbg(ZCI, "2nd analysis: Stop reading sub values sequence.")

		#table with only one element => explicit priorization
		if tgtEnd == ')' and not tgtMap and len(subVals) == 1:
			res = subVals[0]
			ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in EXPLICIT PRIORIZATION:\n" + res.toStr())
			return res

		#finishing result: maps
		if tgtMap:

			#set keys et values for map initialization
			keys = val(
				tgtType_inside,
				atm(ATM__LST_VAL, subVals),
				True
			)
			valuePeers = val(
				tgtType_inside,
				atm(ATM__LST_VAL, subVals_inside),
				True
			)
			res = val(
				tgtType,
				atm(ATM__LST_VAL, [keys, valuePeers]),
				True
			)

		#finishing result: tab, lst & fly
		else:
			res = val(tgtType, atm(ATM__LST_VAL, subVals), True)

		#return result
		ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in COMMON DATA STRUCTURE SHORTCUT NOTATION:\n" + res.toStr())
		return res

	#having found a colon but wasn't a map => no pattern matches such a thing
	if tgtMap:
		unknownValueErrIn2ndAnalysis(ZCI)



	# II] LITERAL: BYTE NOTATIONS

	#prefix found
	if c == BN_PFX:
		if ZCI.inc():
			ZCIErr(ZCI, "2nd analysis: Missing content after byte notation.")

		#multi-byte sequence
		if ZCI.get() == BN_PFX:
			ZCIDeepDbg(ZCI, "2nd analysis: Reading hexadecimal value in multi-bytes notation.")
			if ZCI.inc():
				ZCIErr(ZCI, "2nd analysis: Missing content after multiple-bytes notation.")

			#prepare sequence
			seq = [] #lst[value]
			while ZCI.get() in HEX_DIGITS_LOWERCASE:
				seq.append(
					val(
						ZCI.zCtx.rootTypes[RT__S8],
						atm(ATM__S8, readHexByte(ZCI)),
						True
					)
				)
				if ZCI.inc():
					break

			#missing characters
			if len(seq) == 0:
				ZCIErr(ZCI, "2nd analysis: Missing valid hexadecimal characters in multi-bytes notation.")

			#finish result
			res = val(ZCI.zCtx.rootTypes[RT__REF], atm(ATM__LST_VAL, seq), True)
			ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in MULTI-BYTE NOTATION:\n" + res.toStr())
			return res

		#single-byte sequence
		ZCIDeepDbg(ZCI, "2nd analysis: Reading hexadecimal value in single-byte notation.")
		res = val(
			ZCI.zCtx.rootTypes[RT__S8],
			atm(ATM__S8, readHexByte(ZCI)),
			True
		)
		ZCI.inc()
		ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in SINGLE-BYTE NOTATION:\n" + res.toStr())
		return res



	# III] LITERAL: INTEGERS & FLOATING POINT

	#parsing is quite complex => has been taken away in another method
	v = parseLiteralIntOrFloat(ZCI)
	if v is not None:
		ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in INTEGER/FLOAT:\n" + v.toStr())
		return v



	# IV] LITERAL: STRUCTURE DEFINITION

	#try reading a type
	tID   = readType(ZCI, None, errIfNotExisting=False)
	tInst = ZCI.getTypeInstanceFromID(tID)
	if tID != TYPE_ID__UNKNOWN:
		ZCIDeepDbg(ZCI, "2nd analysis: Structure definition detected.")

		#must be a structure
		if tInst.dcnCommon.nature != NATURE__STC:
			ZCIErr(ZCI, "2nd analysis: Only structure types are allowed as type definition value.")

		#continue parsing to get its fields
		optionalBlanks(ZCI, "2nd analysis: Value parsing (structure definition with type \"" + tInst.name + "\" detected).")
		if ZCI.get() != '{':
			ZCIErr(ZCI, "2nd analysis: Expected a braces includer for structure definition value.")

		#read given values between braces includer
		givenFields = readValSeq(ZCI, tInst.dcnCommon.fields, v2i.scope, cstOnly=v2i.cstOnly)

		#return complete fields map as value
		res = val(
			tID,
			atm(ATM__FMAP_STR_VAL, givenFields),
			True
		)
		ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in STRUCTURE DEFINITION:\n" + res.toStr())
		return res



	# V] VFC/!VFC OR DATA ITEM NAME

	#regular name found
	pfxName = readName(ZCI, None, parseModPfxes=True, modPfxes_asHeaderOnly=True)
	if len(pfxName) != 0:

		#followed by parentheses => VFC/!VFC
		if ZCI.get() == '(':
			ZCIDeepDbg(ZCI, "2nd analysis: VFC/!VFC detected.")

			#cstOnly => not allowed
			if v2i.cstOnly:
				ZCIErr(ZCI, "2nd analysis: Only constant values allowed here (got a VFC/!VFC => variable return value).")

			#prepare fct name
			fctName = getFctNameFromPfxName(ZCI, pfxName)

			#parse & check call elements given
			parsedCall = checkAll_thenReadParams_thenCreateCall(ZCI, fctName, v2i.scope, v2i.cstOnly)

			#return complete value (call)
			ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in !VFC:\n" + res.toStr())
			return val(
				parsedCall.retType,
				atm(ATM__CALL, parsedCall),
				False
			)

		#just a regular name actually => DI NAME
		di = getDatItmFromPfxName(pfxName, v2i.scope)
		if di is None:
			ZCIErr(ZCI, "2nd analysis: Cannot find data item " + unpfxMod(pfxName) + " in cur scope or higher.")

		#cstOnly => not allowed
		if v2i.cstOnly and not di.Cst:
			ZCIErr(ZCI, "2nd analysis: Only constant values allowed here (got a variable data item).")

		#return datItm found
		res = val(
			di.Type,
			atm(ATM__DATITM, di),
			di.Cst
		)
		ZCIDeepDbg(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in DATA ITEM:\n" + res.toStr())
		return res



	#unknown value format
	unknownValueErrIn2ndAnalysis(ZCI)



def secondAnalysisIncludingFOs(ZCI, v2i):
	starter = ZCI.get()



	# 1) PROCESSING FOs: MONO-OPERAND

	#size (FSZ)
	if starter == '#':
		ZCIDeepDbg(ZCI, "2nd analysis: Processing FSZ operator (2nd analysis).")
		ZCI.inc()
		Type = readType(ZCI, v2i.ZCIKindIfErr)

		#get size
		tInst = ZCI.getTypeInstanceFromID(Type)
		if tInst.dcnCommon.nature != NATURE__PRM:
			size = tInst.dcnCommon.stcSize
		else:
			size = tInst.size

		#result
		ZCIDeepDbg(ZCI,"2nd analysis: FSZ resulted into fsz(" + unpfxMod(tInst.name) + ") = " + str(size))
		if ZCI.zCtx.cpl.opts["ARCH"] == 64:
			return val(
				ZCI.zCtx.rootTypes[RT__U64],
				atm(ATM__U64, size),
				True
			)
		return val(
			ZCI.zCtx.rootTypes[RT__U32],
			atm(ATM__U32, size),
			True
		)

	#reference (FRF)
	if starter == '@':
		ZCIDeepDbg(ZCI, "2nd analysis: Processing FRF operator.")
		ZCI.inc()

		#target data item
		pfxName = readName(ZCI, "2nd analysis: Missing data item name for reference operator '@' (FRF).", parseModPfxes=True, modPfxes_asHeaderOnly=True)
		di      = getDatItmFromPfxName(pfxName, v2i.scope)
		if di is None:
			ZCIErr(ZCI, "2nd analysis: Unable to find data item given " + pfxName + " (2nd analysis, concerning reference operator '@' FRF).")

		#result
		ZCIDeepDbg(ZCI, "2nd analysis: FRF resulted into call to frf()") #<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
		return value(
			ZCI.zCtx.rootTypes[RT__REF],
			atm(ATM__REF, 0),
			True #<<<<<<<<<<<<<<<<<<< this will depend on the data item targetted (static => cst adr, else variable)
		)



	# 2) SECOND ANALYSIS WITHOUT END-CHECK

	#read value but don't care if there are still things to analyze
	res = secondAnalysis(ZCI, v2i) #after this, ZCI index is right AFTER the value read
	optionalBlanks(ZCI, None)

	#nothing left to analyze
	if ZCI.reachedEnd():
		return res



	# 3) PROCESSING FOs: 2-OPERANDS

	#casht (FCA)
	following = ZCI.get()
	if following == '$':
		ZCI.inc()
		optionalBlanks(ZCI, None)

		#read explicit type
		ZCIDeepDbg(ZCI, "2nd analysis: Processing FCA operator on " + res.toStr())
		res.Type = readType(ZCI, v2i.ZCIKindIfErr)

		#overwrite result type
		ZCIDeepDbg(ZCI, "2nd analysis: FCA operator applied type " + unpfxMod(ZCI.getTypeNameFromID(Type)) + " on value " + res.toStr())

	#field access (FFA)
	elif following == '.':
		ZCI.inc()

		#invalid element to operate FFA onto
		if res.vdata.id != ATM__DATITM:
			ZCIErr(ZCI, "2nd analysis: Can only operate field access operator (FFA) on data item names.")

		#get the complete chain of accessed fields
		FAChain       = [atm(ATM__STR, res.vdat.dat.name)] #store the NAME of the first data item parsed (in 2nd analysis)
		latestChkType = res.vdat.dat.Type
		isCst         = res.vdat.dat.Cst
		while not ZCI.reachedEnd():
			newChkName = readName(ZCI, "[2nd analysis] Missing second operand after field access operator (FFA).", parseModPfxes=True, modPfxes_asHeaderOnly=True)

			#case 1: following parentheses => METHOD call (and not function call)
			if ZCI.get() == '(':
				isCst = False #got a method call => value is no longer constant

				#parse call
				newChkName = getFctNameFromPfxName(ZCI, newChkName, methodOf=latestChkType)
				newChk     = checkAll_thenReadParams_thenCreateCall(ZCI, newChkName, v2i.scope, v2i.cstOnly)

				#update latest chunk type & add to chain
				latestChkType = newChk.retType
				FAChain.append( atm(ATM__CALL, newChk) )

			#case 2: else => stc/enm field
			else:
				latestChkType = getTypeFieldFromName(ZCI, latestChkType, newChkName).Type
				FAChain.append( atm(ATM__STR, newChkName) )

			#another field => continue
			if ZCI.get() != '.':
				break
			ZCI.inc()

		#format chain under VALUE format
		res = val(
			latestChkType,
			atm(ATM__LST_ATM, FAChain),
			isCst
		)

	#too much content in VALUE ZCE
	if not ZCI.reachedEnd():
		ZCIErr(ZCI, "Too much elements in VALUE ZCE (2nd analysis, parsing including FOs).")

	#success
	return res



#RECURSIVE entry point for 2nd analysis (applying it on the whole ODP result)
def applySecondAnalysis(curPOCall, oriZCI, v2i): #oriZCI only used for error accuracy

	#process 1st operand
	opand1Val = None
	if curPOCall.opand1 is not None:

		#recursively solving children before
		if curPOCall.opand1.id == ATM__POCALL:
			opand1Val = applySecondAnalysis(curPOCall.opand1.dat, oriZCI, v2i)

		#UNITARY entry point for 2nd analysis
		elif curPOCall.opand1.id == ATM__ZCI:
			opand1Val = secondAnalysisIncludingFOs(curPOCall.opand1.dat, v2i)

		#should never happen
		else:
			ZCIInternal(oriZCI, "Found a non-POCall & non-ZCI atom in ODP result.")

	#process 2nd operand
	opand2Val = None
	if curPOCall.opand2 is not None:

		#recursively solving children before
		if curPOCall.opand2.id == ATM__POCALL:
			opand2Val = applySecondAnalysis(curPOCall.opand2.dat, oriZCI, v2i)

		#UNITARY entry point for 2nd analysis
		elif curPOCall.opand2.id == ATM__ZCI:
			opand2Val = secondAnalysisIncludingFOs(curPOCall.opand2.dat, v2i)

		#should never happen
		else:
			ZCIInternal(oriZCI, "Found a non-POCall & non-ZCI atom in ODP result.")



	#1ST CASE: SINGLE VALUE UNIT (NON-CALL)

	#null name => mono-operand mandatorily
	if curPOCall.name is None:
		tgt = None
		if curPOCall.opand1 is None:
			tgt = opand2Val
		elif curPOCall.opand2 is None:
			tgt = opand1Val

		#should never occur
		if tgt is None:
			ZCIInternal(oriZCI, "Found null-name POCall with 2 null or 2 non-null operands (inconsistent result from ODP).")
		return tgt



	#2ND CASE: OPERATOR CALL

	#set operator parameters
	paramVals      = []
	paramTypeNames = []
	if opand1Val is not None:
		paramVals.append(                               opand1Val       )
		paramTypeNames.append( oriZCI.getTypeNameFromID(opand1Val.Type) )
	if opand2Val is not None:
		paramVals.append(                               opand2Val       )
		paramTypeNames.append( oriZCI.getTypeNameFromID(opand2Val.Type) )

	#solve name
	opeFullName = 'O' + curPOCall.name
	for p in paramTypeNames:
		opeFullName += '_' + p

	#check for every operator alternative
	matchingFct = oriZCI.zCtx.findMatchingOperator('O' + curPOCall.name, paramTypeNames)

	#still no one found
	if matchingFct is None:
		oriZCI.forwardUntil(curPOCall.opeIdx)
		ZCIErr(oriZCI, "No operator " + curPOCall.name + " matching for parameters (" + ','.join(paramTypeNames) + ").")

	#result
	return val(
		matchingFct.retType,
		atm(ATM__CALL, call(opeFullName, paramVals, matchingFct.retType)),
		False
	)









