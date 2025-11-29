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
			return ZCIErr_vap2(ZCI, "Lonely negative sign found => invalid value", v2i)
		c = ZCI.get()

	#first character is important (in all cases, must be a decimal digit)
	if c in STR__DECIMAL:
		ZCIDbg1(ZCI, "2nd analysis: Integer or float detected.", prtLine=False)
		resType  = ZCI.zCtx.rootTypes[RT__S32] #default case, considering an S32
		resAtmID = ATM__S32

		#non-zero => literal decimal
		if c != '0':
			resDigitPower = 10
			resText       = readNbrAsText(ZCI, STR__DECIMAL)

		#zero => can be anything
		else:
			if ZCI.inc(): #lonely '0'
				return val(
					ZCI.zCtx.rootTypes[RT__S32],
					atm(ATM__S32, 0),
					True
				)

			#binary, octal, hexadecimal
			c = ZCI.get()
			if c == 'b':
				if ZCI.inc():
					return ZCIErr_vap2(ZCI, "Incomplete literal number given, binary notation must be followed by a digit sequence", v2i)
				resDigitPower = 2
				resText       = readNbrAsText(ZCI, STR__BINARY)
			elif c == 'o':
				if ZCI.inc():
					return ZCIErr_vap2(ZCI, "Incomplete literal number given, octal notation must be followed by a digit sequence", v2i)
				resDigitPower = 8
				resText       = readNbrAsText(ZCI, STR__OCTAL)
			elif c == 'x':
				if ZCI.inc():
					return ZCIErr_vap2(ZCI, "Incomplete literal number given, hexadecimal notation must be followed by a digit sequence", v2i)
				resDigitPower = 16
				resText       = readNbrAsText(ZCI, STR__HEXADECIMAL_LOWERCASE)

		#weird cases: negative sign on non-decimal
		if resIsNegative and resDigitPower != 10:
			return ZCIErr_vap2(ZCI, "Cannot apply negativity on a non-decimal literal notation", v2i)



		#STEP 2: Check terminator to get correct res type

		#read terminator if any
		c = ZCI.get()
		if c == 'u':
			ZCI.inc()
			c = ZCI.get()
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
			return ZCIErr_vap2(ZCI, "Cannot have terminator on negative value", v2i)



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
					return ZCIErr_vap2(ZCI, "Too much digits given in 2 bytes literal binary value (maximum " + str(MAX_BINARY_DIGITS_ALLOWED__U16) + " allowed)", v2i)
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_BINARY_DIGITS_ALLOWED__U32:
					return ZCIErr_vap2(ZCI, "Too much digits given in 4 bytes literal binary value (maximum " + str(MAX_BINARY_DIGITS_ALLOWED__U32) + " allowed)", v2i)
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_BINARY_DIGITS_ALLOWED__U64:
					return ZCIErr_vap2(ZCI, "Too much digits given in 8 bytes literal binary value (maximum " + str(MAX_BINARY_DIGITS_ALLOWED__U64) + " allowed)", v2i)

		#check if too much digits have been given: octal
		elif resDigitPower == 8:
			if resAtmID in (ATM__S16, ATM__U16):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U16:
					return ZCIErr_vap2(ZCI, "Too much digits given in 2 bytes literal octal value (maximum " + str(MAX_OCTAL_DIGITS_ALLOWED__U16) + " allowed)", v2i)
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U32:
					return ZCIErr_vap2(ZCI, "Too much digits given in 4 bytes literal octal value (maximum " + str(MAX_OCTAL_DIGITS_ALLOWED__U32) + " allowed)", v2i)
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_OCTAL_DIGITS_ALLOWED__U64:
					return ZCIErr_vap2(ZCI, "Too much digits given in 8 bytes literal octal value (maximum " + str(MAX_OCTAL_DIGITS_ALLOWED__U64) + " allowed)", v2i)

		#check if too much digits have been given: hexadecimal
		elif resDigitPower == 16:
			if resAtmID in (ATM__S16, ATM__U16):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U16:
					return ZCIErr_vap2(ZCI, "Too much digits given in 2 bytes literal hexadecimal value (maximum " + str(MAX_HEXADECIMAL_DIGITS_ALLOWED__U16) + " allowed)", v2i)
			elif resAtmID in (ATM__S32, ATM__U32):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U32:
					return ZCIErr_vap2(ZCI, "Too much digits given in 4 bytes literal hexadecimal value (maximum " + str(MAX_HEXADECIMAL_DIGITS_ALLOWED__U32) + " allowed)", v2i)
			else: #if resAtmID in (ATM__S64, ATM__U64):
				if len(resText) > MAX_HEXADECIMAL_DIGITS_ALLOWED__U64:
					return ZCIErr_vap2(ZCI, "Too much digits given in 8 bytes literal hexadecimal value (maximum " + str(MAX_HEXADECIMAL_DIGITS_ALLOWED__U64) + " allowed)", v2i)

		#check if too much digits have been given: decimal
		else:
			if resAtmID == ATM__S16:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S16:
					return ZCIErr_vap2(ZCI, "Too much digits given in 2 bytes literal signed decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__S16) + " allowed)", v2i)
			elif resAtmID == ATM__S32:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S32:
					return ZCIErr_vap2(ZCI, "Too much digits given in 4 bytes literal signed decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__S32) + " allowed)", v2i)
			elif resAtmID == ATM__S64:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__S64:
					return ZCIErr_vap2(ZCI, "Too much digits given in 8 bytes literal signed decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__S64) + " allowed)", v2i)
			elif resAtmID == ATM__U16:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U16:
					return ZCIErr_vap2(ZCI, "Too much digits given in 2 bytes literal unsigned decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__U16) + " allowed)", v2i)
			elif resAtmID == ATM__U32:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U32:
					return ZCIErr_vap2(ZCI, "Too much digits given in 4 bytes literal unsigned decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__U32) + " allowed)", v2i)
			else: #if resAtmID == ATM__U64:
				if len(resText) > MAX_DECIMAL_DIGITS_ALLOWED__U64:
					return ZCIErr_vap2(ZCI, "Too much digits given in 8 bytes literal unsigned decimal value (maximum " + str(MAX_DECIMAL_DIGITS_ALLOWED__U64) + " allowed)", v2i)



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
				return ZCIErr_vap2(ZCI, "Incomplete floating point notation, missing value after point", v2i)

			#read after point
			afterPoint = readNbrAsText(ZCI, STR__DECIMAL)
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
			return val(resType, atm(resAtmID, resFloatingNbr), True)

		#end of value parsing (integer)
		if resIsNegative:
			return val(resType, atm(resAtmID, -1*resNbr), True) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Can be optimized in a single return in python, but in Z it may be better this way since resNbr is a ULNG
		return val(resType, atm(resAtmID, resNbr), True)

	#no literal number found
	return None



#2nd analysis
def ZCIErr_vap2(ZCI, msg, v2i):
	if v2i.ZCIKindIfErr is None:
		return None
	ZCIErr(ZCI, msg + v2i.ZCIKindIfErr_ending)
	return None #dead code but required as semantically secure (in Z)

def secondAnalysis(ZCI, allowVFC, v2i):
	ZCIDbg0(ZCI, "2nd analysis: Reading ZCI fragment \"" + ZCI.txtFormat() + "\" to apply second analysis on it.")
	res = None
	c   = ZCI.get()



	# I] LITERAL: COMMON DATA STRUCTURE SHORTCUT

	#map starter symbol
	tgtMap = False
	if c == ':':
		if ZCI.inc():
			return ZCIErr_vap2(ZCI, "Lonely colon ':' found as value => invalid", v2i)
		tgtMap = True
		ZCIDbg1(ZCI, "2nd analysis: Potential map-type detected.", prtLine=False)

	#starting with includer
	if c in ('(', '[', '{'):
		ZCIDbg1(ZCI, "2nd analysis: Includer detected => Potentially targetting tab,lst or fmap,mmap.", prtLine=False)



		#STEP 1: INIT

		#Seems similar to check in the whole INCLUDERS.keys() but this is not related to these actually.
		#We are specificly targetting these 3 and not because they are includer keys but because we have specific pattern associated to them.
		mainStc_typeID = 0
		subStc1_typeID = 0 #subStcs for maps only
		subStc2_typeID = 0
		mainStc_typeName = ""
		subStc1_typeName = "" #idem

		#maps
		if tgtMap:
			if c == '(':
				mainStc_typeName = "fmap"
				subStc1_typeName = "GUtab"
			elif c == '[':
				mainStc_typeName = "mmap"
				subStc1_typeName = "GUlst"
			elif c == '{':
				return ZCIErr_vap2(ZCI, "Associative notation on braces includer is not linked to anything yet", v2i)

			#look for ID
			subStc1_typeID = ZCI.getTypeIDFromName(subStc1_typeName)
			subStc2_typeID = subStc1_typeID

			#subStcs type must already exist yet
			if subStc1_typeID == TYPE_ID__UNKNOWN:
				return ZCIErr_vap2(ZCI,
					"Here are all the available types for now " + ZCI.zCtx.listTypeNames() + \
					"\nNo type \"" + subStc1_typeName + "\" found to be used in common data structure shortcut notation",
					v2i
				)

		#tab, lst
		else:
			if c == '(':
				mainStc_typeName = "GUtab"
			elif c == '[':
				mainStc_typeName = "GUlst"
			elif c == '{':
				return ZCIErr_vap2(ZCI, "Braces includer notation is not linked to anything yet", v2i)

		#mainStc type must already exist yet
		mainStc_typeID = ZCI.getTypeIDFromName(mainStc_typeName)
		if mainStc_typeID == TYPE_ID__UNKNOWN:
			return ZCIErr_vap2(ZCI,
				"Here are all the available types for now " + ZCI.zCtx.listTypeNames() + \
				"\nNo type \"" + mainStc_typeName + "\" found to be used in common data structure shortcut notation",
				v2i
			)

		#init limits
		peerIdx = ZCI.pairs[ZCI.ctx.icontent.idx]
		tgtEnd  = ZCI.ctx.icontent.s[peerIdx]
		ZCI.inc()



		#STEP 2: READ CONTENT

		#inner types
		innerType1 = TYPE_ID__UNKNOWN
		innerType2 = TYPE_ID__UNKNOWN

		#explicitly given
		if ZCI.get() == '$':
			innerType1 = readType(ZCI, "inner type in common data structure shortcut", dcnKwLstToReplace=v2i.dcnKwLstToReplace)
			if tgtMap:
				if ZCI.get() != ',':
					return ZCIErr_vap2(ZCI, "Expected coma separator and a second inner type in " + mainStc_typeName + " common data structure shortcut", v2i)
				innerType2 = readType(ZCI, "second inner type in common data structure shortcut", dcnKwLstToReplace=v2i.dcnKwLstToReplace)

		#read subvalues as long as we have some (separated by comas)
		subVals1 = [] #lst[val]
		subVals2 = [] #for maps
		ZCIDbg1(ZCI, "2nd analysis: Start reading sub values sequence.", prtLine=False)
		while True:
			optionalBlanks(ZCI, None, BLANKS_EXTENDED)

			#read subvalue
			ZCIDbg1(ZCI, "2nd analysis: => Reading " + str(len(subVals1)+1) + "th sub value.", prtLine=False)
			v = readVal(ZCI,
				None, v2i.scope,
				cstOnly           = v2i.cstOnly,
				dcnKwLstToReplace = v2i.dcnKwLstToReplace
			)
			if v is not None:
				subVals1.append(v)

				#check its type also, they must all have the same one
				if innerType1 == TYPE_ID__UNKNOWN:
					innerType1 = v.Type
				else:
					if v.Type != innerType1:
						ZCIWrn(ZCI, "2nd analysis: " + str(len(subVals1)+1) + "th value given in collection has different type than expected (expected " + unpfxTypeName(ZCI.getTypeNameFromID(innerType1))[0] + ", got " + unpfxTypeName(ZCI.getTypeNameFromID(v.Type))[0] + ")" + v2i.ZCIKindIfErr_ending)
						typeSizesMustMatch(ZCI, ", in common data structure shortcut notation" + v2i.ZCIKindIfErr, v.Type, innerType1)

				#read second subValue (for maps only)
				if tgtMap:

					#colon separator required
					optionalBlanks(ZCI, None, BLANKS_EXTENDED)
					next = ZCI.get()
					if next != ':':
						return ZCIErr_vap2(ZCI, "Invalid element " + next + " given in associative sequence (expected colon separator ':')", v2i)
					ZCI.inc()

					#read a second subvalue (require a couple for association)
					optionalBlanks(ZCI, None, BLANKS_EXTENDED)
					v = readVal(ZCI,
						"associated value in common data structure shortcut notation" + v2i.ZCIKindIfErr_ending,
						v2i.scope,
						cstOnly           = v2i.cstOnly,
						dcnKwLstToReplace = v2i.dcnKwLstToReplace
					)
					subVals2.append(v)

					#check its type also, they must all have the same one
					if innerType2 == TYPE_ID__UNKNOWN:
						innerType2 = v.Type
					else:
						if v.Type != innerType2:
							ZCIWrn(ZCI, "2nd analysis: " + str(len(subVals1)+1) + "th value given in collection has different type than expected (expected " + unpfxTypeName(ZCI.getTypeNameFromID(innerType2))[0] + ", got " + unpfxTypeName(ZCI.getTypeNameFromID(v.Type))[0] + ")" + v2i.ZCIKindIfErr_ending)
							typeSizesMustMatch(ZCI, ", in common data structure shortcut notation" + v2i.ZCIKindIfErr, v.Type, innerType2)

			#look for end separator
			optionalBlanks(ZCI, None, BLANKS_EXTENDED)
			next = ZCI.get()
			if next == tgtEnd:
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInt(ZCI, "2nd analysis: Ending value sequence inside includer with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			if next != ',':
				return ZCIErr_vap2(ZCI, "Invalid element " + next + " given in value sequence between includers (expected coma separator ',' or closing includer '" + tgtEnd + "')", v2i)
			ZCI.inc()

		#debug
		ZCIDbg1(ZCI, "2nd analysis: Stop reading sub values sequence.")



		#STEP 3: CONCLUSION

		#unable to solve inner types => err (no need to check whether the 2nd one is set for maps)
		if innerType1 == TYPE_ID__UNKNOWN:
			return ZCIErr_vap2(ZCI, "Unable to determine inner type of common data structure shortcut notation (require explicit inner type or at least one value inside)", v2i)

		#maps
		if tgtMap:

			#sub vals are going to be stored in custom datItms actually
			rawKeys           = val(subStc1_typeID, atm(ATM__LST_VAL, subVals1), True)
			rawValuePeers     = val(subStc2_typeID, atm(ATM__LST_VAL, subVals2), True)
			datItm_keys       = v2i.scope.nxtDcpDatItm(subStc1_typeID)
			datItm_valuePeers = v2i.scope.nxtDcpDatItm(subStc2_typeID)

			#then, real sub vals are just other refs to these datItm
			keys       = val(subStc1_typeID, atm(ATM__DATITM, datItm_keys      ), False)
			valuePeers = val(subStc2_typeID, atm(ATM__DATITM, datItm_valuePeers), False)

			#res val is also going to be stored in a custom datItm actually
			rawRes     = val(mainStc_typeID, atm(ATM__LST_VAL, [keys, valuePeers]), True)
			datItm_res = v2i.scope.nxtDcpDatItm(mainStc_typeID)

			#then, real res is just another ref to that datItm
			res = val(mainStc_typeID, atm(ATM__DATITM, datItm_res), False)

		#tab,lst
		else:

			#table with only one element => explicit priorization (wasn't a tab actually)
			if len(subVals1) == 1 and tgtEnd == ')':
				res = subVals1[0]
				ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in EXPLICIT PRIORIZATION:\n" + res.toStr())
				return res

			#res val is going to be stored in a custom datItm actually
			rawRes     = val(mainStc_typeID, atm(ATM__LST_VAL, subVals1), True)
			datItm_res = v2i.scope.nxtDcpDatItm(mainStc_typeID)

			#then, real res is just another ref to that datItm
			res = val(mainStc_typeID, atm(ATM__DATITM, datItm_res), False)

		#create common data structure delimitations
		v2i.scope.header.append(asg(
			val(datItm_res.Type, atm(ATM__DATITM, datItm_res), False),
			rawRes
		))
		v2i.scope.footer.append(call("GT" + mainStc_typeName + "_Ffree", [datItm_res], TYPE_ID_UNKNOWN)) #btw, for maps, no need to free sub dat stc, maps "free()" will take this in charge

		#return result
		ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in COMMON DATA STRUCTURE SHORTCUT NOTATION:\n" + res.toStr())
		return res

	#having found a colon but wasn't a map => no pattern matches such a thing
	if tgtMap:
		unknownValueErrIn2ndAnalysis(ZCI, v2i)



	# II] LITERAL: BYTE NOTATIONS

	#prefix found
	if c == BN_PFX:
		if ZCI.inc():
			return ZCIErr_vap2(ZCI, "Missing content after byte notation", v2i)

		#multi-byte sequence
		if ZCI.get() == BN_PFX:
			ZCIDbg1(ZCI, "2nd analysis: Reading hexadecimal value in multi-bytes notation.")
			if ZCI.inc():
				return ZCIErr_vap2(ZCI, "Missing content after multiple-bytes notation", v2i)

			#prepare sequence
			seq = [] #lst[value]
			while ZCI.get() in HEX_DIGITS_LOWERCASE:
				seq.append(val(
					ZCI.zCtx.rootTypes[RT__S8],
					atm(ATM__S8, readHexByte(ZCI)),
					True
				))
				if ZCI.inc():
					break

			#missing characters
			if len(seq) == 0:
				return ZCIErr_vap2(ZCI, "Missing valid hexadecimal characters in multi-bytes notation", v2i)

			#finish result
			res = val(ZCI.zCtx.rawType, atm(ATM__LST_VAL, seq), True)
			ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in MULTI-BYTE NOTATION:\n" + res.toStr())
			return res

		#single-byte sequence
		ZCIDbg1(ZCI, "2nd analysis: Reading hexadecimal value in single-byte notation.")
		res = val(
			ZCI.zCtx.rootTypes[RT__S8],
			atm(ATM__S8, readHexByte(ZCI)),
			True
		)
		ZCI.inc()
		ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in SINGLE-BYTE NOTATION:\n" + res.toStr())
		return res



	# III] LITERAL: INTEGERS & FLOATING POINT

	#parsing is quite complex => has been taken away in another method
	v = parseLiteralIntOrFloat(ZCI)
	if v is not None:
		ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in INTEGER/FLOAT:\n" + v.toStr())
		return v



	# IV] LITERAL: STARTING WITH TYPE

	#try reading a type
	tID = readType(ZCI, None, errIfNotExisting=False, dcnKwLstToReplace=v2i.dcnKwLstToReplace)
	if tID != TYPE_ID__UNKNOWN:
		tInst = ZCI.getTypeInstanceFromID(tID)



		#case 1: enm value
		if tInst.dcnCommon.nature == NATURE__ENM:
			ZCIDbg1(ZCI, "2nd analysis: Enm value detected.")

			#must be followed by field name
			if ZCI.get() != '.':
				return ZCIErr_vap2(ZCI, "Expected field access operator '.' after enm type given as value", v2i)
			ZCI.inc()
			fieldName = readName(ZCI, "field name after enm type given as value" + v2i.ZCIKindIfErr_ending, dblUnderscores=True)

			#get idx
			idx    = -1
			fields = tInst.dcnCommon.fields
			for f in range(len(fields)):
				if fields[f].name == fieldName: #found it
					idx = f
					break

			#no field found with given name
			if idx == -1:
				return ZCIErr_vap2(ZCI, "Enumerate type " + unpfxTypeName(ZCI.zCtx, tInst.name)[0] + " has no field \"" + fieldName + '\"', v2i)

			#associated idx is the final resulting value, but type is still the one of the ENM itself (not the one of the field)
			res = val(tID, atm(ATM__U64, idx), True)
			return res



		#case 2: structure definition
		else:
			ZCIDbg1(ZCI, "2nd analysis: Structure definition detected.")
			if tInst.dcnCommon.nature != NATURE__STC:
				return ZCIErr_vap2(ZCI, "Only structure types are allowed as type definition value", v2i)

			#continue parsing to get its fields
			optionalBlanks(ZCI, "2nd analysis: Value parsing (structure definition with type \"" + tInst.name + "\" detected).")
			if ZCI.get() != '{':
				return ZCIErr_vap2(ZCI, "Expected a braces includer for structure definition value", v2i)

			#read given values between braces includer
			givenFields = readValSeq(ZCI,
				v2i.ZCIKindIfErr,
				tInst.dcnCommon.fields,
				v2i.scope,
				cstOnly=v2i.cstOnly
			)

			#return complete fields map as value
			res = val(tID, atm(ATM__FMAP_STR_VAL, givenFields), True)
			ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in STRUCTURE DEFINITION:\n" + res.toStr())
			return res



	# V] VFC/!VFC OR DATA ITEM NAME

	#regular name found
	modPfx, rawName = readName(ZCI, None, parseModPfxes=True)
	if len(rawName) != 0:

		#followed by parentheses => VFC/!VFC
		if ZCI.get() == '(':
			ZCIDbg1(ZCI, "2nd analysis: VFC/!VFC detected.")

			#cstOnly => not allowed
			if v2i.cstOnly:
				return ZCIErr_vap2(ZCI, "Only constant values allowed here (got a VFC/!VFC => variable return value)", v2i)

			#parse & check call elements given
			parsedCall = checkAll_thenReadParams_thenCreateCall(ZCI,
				allowVFC,  v2i.ZCIKindIfErr,
				modPfx,    rawName,
				v2i.scope, v2i.cstOnly,
				v2i.dcnKwLstToReplace
			)

			#return complete value (call)
			res = val(
				parsedCall.retType,
				atm(ATM__CALL, parsedCall),
				False
			)
			ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in !VFC:\n" + res.toStr())
			return res

		#just a regular name actually => DI NAME
		di = getDatItmFromScopeAndParents(modPfx, rawName, v2i.scope)
		if di is None:
			return ZCIErr_vap2(ZCI,
				"Maybe you wanted to target a type among the available " + ZCI.zCtx.listTypeNames() + \
				"\nMaybe you wanted to target a data item among the available " + listDatItmNamesAvailable(v2i.scope) + \
				"\nCannot find data item \"" + unpfxMod(modPfx) + undblUnderscores(rawName) + "\" in current scope or higher",
				v2i
			)

		#cstOnly => not allowed
		if v2i.cstOnly and not di.Cst:
			return ZCIErr_vap2(ZCI, "Only constant values allowed here (got a variable data item)", v2i)

		#return datItm found
		res = val(
			di.Type,
			atm(ATM__DATITM, di),
			di.Cst
		)
		ZCIDbg1(ZCI, "2nd analysis: Finished reading ZCI fragment \"" + ZCI.txtFormat() + "\", resulted in DATA ITEM:\n" + res.toStr())
		return res



	#unknown value format
	return ZCIErr_vap2(ZCI, "Content does not match any possible pattern", v2i)



def secondAnalysisIncludingExtraOpes(ZCI, allowVFC, v2i):
	starter = ZCI.get()



	# 1) PROCESSING MONO-OPERAND

	#case 1: size (FSZ)
	if starter == '#':
		ZCIDbg1(ZCI, "2nd analysis: Processing FSZ operator (2nd analysis).")
		ZCI.inc()
		Type = readType(ZCI, v2i.ZCIKindIfErr, dcnKwLstToReplace=v2i.dcnKwLstToReplace)

		#get size
		tInst = ZCI.getTypeInstanceFromID(Type)
		size  = tInst.dcnCommon.size

		#result
		ZCIDbg1(ZCI,"2nd analysis: FSZ resulted into fsz(" + unpfxMod(tInst.name) + ") = " + str(size))
		if ZCI.zCtx.cpl.opts["ARCH"] == "64":
			return val(
				ZCI.zCtx.rootTypes[RT__S64],
				atm(ATM__S64, size),
				True
			)
		return val(
			ZCI.zCtx.rootTypes[RT__S32],
			atm(ATM__S32, size),
			True
		)

	#case 2: reference (FRF)
	if starter == '@':
		if ZCI.zCtx.cpl.mode == CPL__MODE_Z:
			return ZCIErr_vap2(ZCI, "Reference operator (FRF) is forbiden", v2i)
		ZCIDbg1(ZCI, "2nd analysis: Processing FRF operator.")
		ZCI.inc()

		#read datItm name
		modPfx, rawName = readName(ZCI, "2nd analysis: Missing data item name for reference operator '@' (FRF)" + v2i.ZCIKindIfErr_ending, parseModPfxes=True)
		di              = getDatItmFromScopeAndParents(modPfx, rawName, v2i.scope)
		if di is None:
			ZCIErr(ZCI, "2nd analysis: Unable to find data item given " + unpfxMod(modPfx) + rawName + " (2nd analysis, concerning reference operator '@' FRF)" + v2i.ZCIKindIfErr_ending)

		#get it
		di = getDatItmFromScopeAndParents(modPfx, rawName, v2i.scope)
		if di is None:
			ZCIErr(ZCI,
				"Maybe you wanted to target a data item among the available " + listDatItmNamesAvailable(v2i.scope) + \
				"\n2nd analysis: Cannot find data item " + unpfxMod(modPfx) + undblUnderscores(rawName) + " in current scope or higher" + v2i.ZCIKindIfErr_ending
			)

		#res
		res = val(
			ZCI.zCtx.refType,
			atm(ATM__CALL, call(
				"frf",
				[val(
					di.Type,
					atm(ATM__DATITM, di),
					di.Cst
				)],
				ZCI.zCtx.refType
			)),
			True
		)
		ZCIDbg1(ZCI, "2nd analysis: FRF resulted into call " + res.toStr())
		return res



	# 2) SECOND ANALYSIS WITHOUT END-CHECK

	#read value but don't care if there are still things to analyze
	res = secondAnalysis(ZCI, allowVFC, v2i) #after this, ZCI index is right AFTER the value read

	#no value found is acceptable => don't go further
	if res is None and v2i.ZCIKindIfErr is None:
		return None



	# 3) PROCESSING 2-OPERANDS

	#as long as we have other operand
	while True:
		optionalBlanks(ZCI, None)
		if ZCI.reachedEnd():
			break
		following = ZCI.get()



		#case 1: casht (FCA)
		if following == '$':
			ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE FCA in process.")
			ZCI.inc()
			optionalBlanks(ZCI, None)

			#read explicit type & apply it
			res.Type = readType(ZCI, v2i.ZCIKindIfErr, dcnKwLstToReplace=v2i.dcnKwLstToReplace)
			ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE FCA resulted into " + res.toStr())



		#case 2: field access (FFA) or method call
		elif following == '.':
			ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE FFA or METHOD CALL in process.")
			ZCI.inc()

			#read name & prepare extraction of modPfx
			modPfx, rawName = readName(ZCI, "2nd analysis: Missing second operand after field access operator (FFA)" + v2i.ZCIKindIfErr_ending, parseModPfxes=True)



			#case 2.1: following parentheses => METHOD call (and not function call)
			if ZCI.get() == '(':
				ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE METHOD CALL in process.")

				#err case: call from VFC
				if res.vdat.id == ATM__CALL:
					if res.vdat.dat.retType == TYPE_ID__UNKNOWN:
						ZCIErr(ZCI, "2nd analysis: Cannot call method " + unpfxMod(modPfx) + rawName + " on void value" + v2i.ZCIKindIfErr_ending)

				#parse method call
				c = checkAll_thenReadParams_thenCreateCall(ZCI,
					allowVFC,  v2i.ZCIKindIfErr,
					modPfx,    rawName,
					v2i.scope, v2i.cstOnly,
					v2i.dcnKwLstToReplace,
					methodCaller = res
				)

				#update res with that method call
				res = val(c.retType, atm(ATM__CALL, c), False)
				ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE METHOD CALL resulted into " + res.toStr())



			#case 2.2: else => stc field
			else:
				ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE FFA in process.")

				#error case
				if modPfx != "G":
					return ZCIErr_vap2(ZCI, "Can't use module prefix when trying to access stc field (field \"" + rawName + "\" from module " + unpfxMod(modPfx) + ")", v2i)

				#stc only
				stcInst = ZCI.zCtx.getTypeInstanceFromID(res.Type)
				if stcInst.dcnCommon.nature != NATURE__STC:
					return ZCIErr_vap2(ZCI, "Type " + unpfxTypeName(ZCI.zCtx, stcInst.name)[0] + " is not a structure type, cannot get fields from it", v2i)

				#get field from stc
				offset    = 0
				fieldType = TYPE_ID__UNKNOWN
				for f in stcInst.dcnCommon.fields:
					if f.name == rawName: #found it
						fieldType = f.Type
						break
					offset += ZCI.zCtx.getTypeInstanceFromID(f.Type).dcnCommon.size

				#no field found with given name
				if fieldType == TYPE_ID__UNKNOWN:
					return ZCIErr_vap2(ZCI, "Structure type " + unpfxTypeName(ZCI.zCtx, stcInst.name)[0] + " has no field \"" + rawName + '\"', v2i)

				''' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<< RELY ON C STRUCTURES SYNTAX INSTEAD OF FFA CALL <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

				#use appropriate "ffa" call, keep the info that this "ffa_get_<fieldTypeID>" must be generated later
				if fieldType not in ZCI.zCtx.cpl.ffa_fieldTypeIDs:
					ZCI.zCtx.cpl.ffa_fieldTypeIDs.append(fieldType)

				#res will be given to "ffa" call as a ref
				refRes = val(
					ZCI.zCtx.refType,
					atm(ATM__CALL, call("frf", [res], ZCI.zCtx.refType)),
					True
				)

				#update res with ffa call and computed offset
				res = val(
					fieldType,
					atm(ATM__CALL, call(
						"ffa_get_" + str(fieldType), [
							refRes,
							val(ZCI.zCtx.smaxType, atm(ATM__U32, offset), True)
						], fieldType
					)),
					res.Cst
				)
				ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE FFA resulted into " + res.toStr())
				'''

				#rely on C compiler <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
				res = val(fieldType, atm(ATM__FFA, ffa(res, rawName)), res.Cst)



		#case 3: IIN, ISU, IIA, ISA
		elif following == '[':
			ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE IIN/ISU/IIA/ISA in process.")
			ZCI.inc()
			opeHeader = "Oiin"
			paramVals = [res] #<======= in Z, declare 4 elements and call tab.rmLast() thrice right after (this way we are sure to have room for each param in all cases (IIN requires 2, ISU & IIA 3, ISA 4)

			#set some info for ope search
			paramTypeIDs   = [                      res.Type ]
			paramTypeNames = [ZCI.getTypeNameFromID(res.Type)]

			#read 1st value given in brackets includer
			optionalBlanks(ZCI, None)
			v = readVal(ZCI,
				"indexing value in IIN/ISU/IIA/ISA operator call" + v2i.ZCIKindIfErr_ending,
				v2i.scope,
				cstOnly           = v2i.cstOnly,
				dcnKwLstToReplace = v2i.dcnKwLstToReplace
			)
			paramVals.append(v)

			#add info for ope search
			paramTypeIDs.append(v.Type)
			paramTypeNames.append(ZCI.getTypeNameFromID(v.Type))
			optionalBlanks(ZCI, None)

			#sub targetted
			if ZCI.get() == ':':
				optionalBlanks(ZCI, None)
				opeHeader = "Oisu"

				#read 2nd value given in brackets includer
				v = readVal(ZCI,
					"stop indexing value in ISU operator call" + v2i.ZCIKindIfErr_ending,
					v2i.scope,
					cstOnly          = v2i.cstOnly,
					dcnKwLstToReplace = v2i.dcnKwLstToReplace
				)
				paramVals.append(v)

				#add info for ope search
				paramTypeIDs.append(v.Type)
				paramTypeNames.append(ZCI.getTypeNameFromID(v.Type))
				optionalBlanks(ZCI, None)

			#must be at end of brackets includer
			if ZCI.reachedEnd() or ZCI.get() != ']':
				ZCIErr(ZCI, "2nd analysis: Expected closing bracket in " + opeHeader[1:].upper() + " operator call" + v2i.ZCIKindIfErr_ending)
			ZCI.inc()

			#possibly having IIA / ISU
			if allowVFC:
				optionalBlanks(ZCI, None)

				#definitely got asg
				if readSym(ZCI) == SYM__ASG:
					ZCI.forward(SYM_LENGTHS[SYM__ASG])
					optionalBlanks(ZCI, None)

					#read & add value to assign
					v = readVal(ZCI,
						"assignment value for IIA/ISA operator call" + v2i.ZCIKindIfErr_ending,
						v2i.scope,
						cstOnly           = v2i.cstOnly,
						dcnKwLstToReplace = v2i.dcnKwLstToReplace
					)
					paramVals.append(v)

					#add info for ope search
					paramTypeIDs.append(v.Type)
					paramTypeNames.append(ZCI.getTypeNameFromID(v.Type))

					#turn IIN into IIA & ISU into ISA
					if opeHeader == "Oiin":
						opeHeader = "Oiia"
					elif opeHeader == "Oisu":
						opeHeader = "Oisa"

			#try find an appropriate ope
			matchingOpe = zCtx__findMatchingOperator(ZCI.zCtx, opeHeader, paramTypeIDs, paramTypeNames)

			#no one found
			if matchingOpe is None:
				ZCIErr(ZCI,
					"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(ZCI.zCtx, opeHeader) + \
					"\n2nd analysis: No operator " + opeHeader[1:].upper() + " matching for parameters (" + ','.join(paramTypeNames) + ')' + v2i.ZCIKindIfErr_ending
				)

			#corresponding ope call
			c = call(matchingOpe.name, paramVals, matchingOpe.retType)

			#update res with corresponding ope call
			res = val(c.retType, atm(ATM__CALL, c), False)
			ZCIDbg1(ZCI, "2nd analysis: EXTRA OPE " + opeHeader[1:].upper() + " resulted into " + res.toStr())



		#unknown following chr => not part of the value itself, stop 2nd analysis here
		else:
			break



	#check last elm retType if we must ret !void
	if not allowVFC:
		if res.Type == TYPE_ID__UNKNOWN:
			return ZCIErr_vap2(ZCI, "Extra operator parsing resulted in void value => forbiden here", v2i)

	#success
	return res



#RECURSIVE entry point for 2nd analysis (applying it on the whole ODP result)
def applySecondAnalysis(curPOCall, oriZCI, v2i, allowVFC=False): #oriZCI only used for error accuracy

	#process 1st operand
	opand1Val = None
	if curPOCall.opand1 is not None:

		#recursively solving children before
		if curPOCall.opand1.id == ATM__POCALL:
			opand1Val = applySecondAnalysis(curPOCall.opand1.dat, oriZCI, v2i) #DON'T TRANSMIT "allowVFC" !!! THIS IS RESERVED FOR THE MAIN POCALL ONLY !

		#UNITARY entry point for 2nd analysis
		elif curPOCall.opand1.id == ATM__ZCI:
			opand1Val = secondAnalysisIncludingExtraOpes(curPOCall.opand1.dat, allowVFC, v2i)

			#update maxStopIdx ACCORDING TO 2ND ANALYSIS (ODP can't have the accuracy we have here, so we RE-compute a better maxStopIdx)
			if curPOCall.opand1.dat.ctx.icontent.idx > v2i.maxStopIdx:
				v2i.maxStopIdx = curPOCall.opand1.dat.ctx.icontent.idx

		#should never happen
		else:
			ZCIInt(oriZCI, "Found a non-POCall & non-ZCI atom in ODP result.")

	#process 2nd operand
	opand2Val = None
	if curPOCall.opand2 is not None:

		#recursively solving children before
		if curPOCall.opand2.id == ATM__POCALL:
			opand2Val = applySecondAnalysis(curPOCall.opand2.dat, oriZCI, v2i) #DON'T TRANSMIT "allowVFC" !!! THIS IS RESERVED FOR THE MAIN POCALL ONLY !

		#UNITARY entry point for 2nd analysis
		elif curPOCall.opand2.id == ATM__ZCI:
			opand2Val = secondAnalysisIncludingExtraOpes(curPOCall.opand2.dat, allowVFC, v2i)

			#update maxStopIdx ACCORDING TO 2ND ANALYSIS (ODP can't have the accuracy we have here, so we RE-compute a better maxStopIdx)
			if curPOCall.opand2.dat.ctx.icontent.idx > v2i.maxStopIdx:
				v2i.maxStopIdx = curPOCall.opand2.dat.ctx.icontent.idx

		#should never happen
		else:
			ZCIInt(oriZCI, "Found a non-POCall & non-ZCI atom in ODP result.")



	#1ST CASE: SINGLE VALUE UNIT (NON-CALL)

	#null name => mono-operand mandatorily
	if curPOCall.name is None:
		tgt = None
		if curPOCall.opand1 is not None:
			if curPOCall.opand2 is not None:
				ZCIInt(oriZCI, "Found null-name POCall with 2 non-null operands (inconsistent result from ODP).")
			else:
				tgt = opand1Val
		else:
			if curPOCall.opand2 is not None:
				tgt = opand2Val
			elif v2i.ZCIKindIfErr is not None:
				ZCIInt(oriZCI, "Found null-name POCall with 2 null operands, and we don't allow null from 2nd analysis here (=> probably inconsistent result from ODP).")

		#lonely ZCI fragment to be returned
		return tgt



	#2ND CASE: OPERATOR CALL

	#gather ope params info
	opeHeader      = 'O' + curPOCall.name
	paramVals      = []
	paramTypeIDs   = []
	paramTypeNames = []
	if opand1Val is not None:
		paramVals.append(                               opand1Val       )
		paramTypeIDs.append(                            opand1Val.Type  )
		paramTypeNames.append( oriZCI.getTypeNameFromID(opand1Val.Type) )
	if opand2Val is not None:
		paramVals.append(                               opand2Val       )
		paramTypeIDs.append(                            opand2Val.Type  )
		paramTypeNames.append( oriZCI.getTypeNameFromID(opand2Val.Type) )

	#invalid nbr of params for tgt ope
	if len(paramTypeIDs) != 2 - int(curPOCall.name in MONO_OPERAND_NAMES):
		if v2i.ZCIKindIfErr is None: #no value found is allowed => null
			return None

		#should never occur
		ZCIInt(ZCI, "Got invalid nbr of operands in 2nd analysis and value can't be null (wrong ope name given ?).")

	#check for every operator alternative
	matchingFct = zCtx__findMatchingOperator(oriZCI.zCtx, opeHeader, paramTypeIDs, paramTypeNames)

	#still no one found
	if matchingFct is None:
		oriZCI.forwardUntil(curPOCall.opeIdx)
		ZCIErr(oriZCI,
			"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(oriZCI.zCtx, opeHeader) + \
			"\n2nd analysis: No operator " + curPOCall.name.upper() + " matching for parameters (" + ','.join(paramTypeNames) + ")" + v2i.ZCIKindIfErr_ending
		)

	#result
	return val(
		matchingFct.retType,
		atm(ATM__CALL, call(opeHeader + '_' + '_'.join(paramTypeNames), paramVals, matchingFct.retType)),
		False
	)
