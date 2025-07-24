# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/generic.py

	# GENERAL PARSING TOOLS

	#move ctx cursor just before the first non-blank character found
	def jumpBlankZone(self, ZCI, missingFieldIfError, blanks=BLANKS): #!WARNING: we MUST be on a blank character before calling that function
		while not ZCI.inc():
			if ZCI.get() not in blanks:
				return
		if missingFieldIfError is not None:
			self.ZCIError(ZCI, "Expected something after blank zone: " + missingFieldIfError)

	def optionnalBlanks(self, ZCI, missingFieldIfError, blanks=BLANKS):
		if ZCI.get() in blanks:
			self.jumpBlankZone(ZCI, missingFieldIfError, blanks=blanks)

	def endOfZCI(self, ZCI, ZCIKindIfError):
		if not ZCI.reachedEnd():
			self.ZCIError(ZCI, "Too much elements in " + ZCIKindIfError + " Should stop here.")






	# REAL ZCE PARSING TOOLS (bare metal syntax-related)

	#read hexadecimal byte
	def readHexByte(self, ZCI):

		#read & check 1st digit
		h1 = ZCI.get()
		if h1 not in HEX_DIGITS_LOWERCASE:
			self.ZCIError(ZCI, "Invalid first hexadecimal digit '" + h1 + "' given in byte notation.")

		#read & check 2nd digit
		if ZCI.inc():
			self.ZCIError(ZCI, "Missing second hexadecimal digit in byte notation.")
		h0 = ZCI.get()
		if h0 not in HEX_DIGITS_LOWERCASE:
			self.ZCIError(ZCI, "Invalid second hexadecimal digit '" + h0 + "' given in byte notation.")

		#return byte
		return hex_toByt(h1, h0)



	#try reading symbol (don't move ZCI ctx)
	def readSymbol(self, ZCI):
		self.ZCIDeepDebug(ZCI, "Reading symbol.")
		tmpZCI = ZCI.copy()
		c1 = tmpZCI.get()

		#1-character symbol
		if c1 == '~':
			return SYMBOL__SIN
		elif c1 == '/':
			return SYMBOL__ADI
		elif c1 == '+':
			return SYMBOL__BAD
		elif c1 == '%':
			return SYMBOL__AMO
		elif c1 == '^':
			return SYMBOL__LXO
		elif c1 == '#':
			return SYMBOL__FSZ
		elif c1 == '@':
			return SYMBOL__FRF
		elif c1 == '$':
			return SYMBOL__FCA
		elif c1 == '.':
			return SYMBOL__FFA

		#multi-character symbol: starting with '!'
		elif c1 == '!':
			tmpZCI.inc()
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CNE
			elif c2 == '?':
				return SYMBOL__INA
			return SYMBOL__SNO

		#multi-character symbol: starting with '*'
		elif c1 == '*':
			if tmpZCI.inc():
				return SYMBOL__AMU
			if tmpZCI.get() == '*':
				return SYMBOL__APO
			return SYMBOL__AMU

		#multi-character symbol: starting with '&'
		elif c1 == '&':
			self.ZCIDeepDebug(tmpZCI, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + tmpZCI.toStr())
			if tmpZCI.inc():
				return SYMBOL__LAN #ending with lonely '&'
			if tmpZCI.get() == '&':
				return SYMBOL__DAN
			return SYMBOL__LAN

		#multi-character symbol: starting with '|'
		elif c1 == '|':
			tmpZCI.inc()
			c2 = tmpZCI.get()
			if c2 == '|':
				return SYMBOL__DOR
			elif c2 == '<':
				if tmpZCI.inc():
					return SYMBOL__LOR
				if tmpZCI.get() == '<':
					return SYMBOL__LLB
			return SYMBOL__LOR

		#multi-character symbol: starting with '-'
		elif c1 == '-':
			tmpZCI.inc()
			if tmpZCI.get() == '>':
				if tmpZCI.inc():
					return SYMBOL__BSU
				if tmpZCI.get() == '>':
					return SYMBOL__LRR
			return SYMBOL__BSU

		#multi-character symbol: starting with '<'
		elif c1 == '<':
			if tmpZCI.inc():
				return SYMBOL__CLT
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CLE
			elif c2 == '<':
				if tmpZCI.inc():
					return SYMBOL__LLS
				if tmpZCI.get() == '-':
					return SYMBOL__LLR
				return SYMBOL__LLS
			return SYMBOL__CLT

		#multi-character symbol: starting with '>'
		elif c1 == '>':
			if tmpZCI.inc():
				return SYMBOL__CGT
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CGE
			elif c2 == '>':
				if tmpZCI.inc():
					return SYMBOL__LRS
				if tmpZCI.get() == '|':
					return SYMBOL__LRB
				return SYMBOL__LRS
			return SYMBOL__CGT

		#multi-character symbol: starting with '='
		elif c1 == '=':
			if tmpZCI.inc():
				return SYMBOL__ASG
			if tmpZCI.get() == '=':
				return SYMBOL__CEQ
			return SYMBOL__ASG

		#multi-character symbol: starting with '?'
		elif c1 == '?':
			return SYMBOL__IAM

		#no match
		return SYMBOL__NOT_FOUND



	#read a name according to the given charset (either blacklist or whitelist)
	# IMPORTANT : Reading ctx from its CURRENT position and move it right AFTER the extracted result
	#also, blacklist is prioritary : if null => use whitelist, else, use it (no matter whitelist value)
	#
	# /!\ This method must be included in STDZ into ^Parsing.ctx whithout the module prefix part.
	#     Must also include the first 2 lines of comment over it
	#
	def readName(self,
		ZCI,
		missingFieldIfError, #null means "don't raise error if empty"
		blacklist=None, whitelist=DEFAULT_NAME_CHARSET,
		doubleUnderscores=False,
		parseModulePrefixes=False,
		modulePrefix_asHeaderOnly=False #means "if any, it must BEGIN with it and be the only occurrence"
	):
		self.ZCIDeepDebug(ZCI, "Reading name.")
		if parseModulePrefixes:
			doubleUnderscores = True #doesn't make sens to double underscores in module prefixes but not in the name => force it

		#read until given blacklist/whitelist no longer matches
		name           = ""
		firstCharacter = True
		while True:
			if not firstCharacter: #skip ZCI.inc() for first character only
				if ZCI.inc():
					break
			c = ZCI.get()



			# I] MODULE PREFIX PARSING

			#module prefix detection
			if parseModulePrefixes and c == '^':
				modules           = []
				currentModuleName = ""

				#only allowing it as name header
				if modulePrefix_asHeaderOnly and not firstCharacter:
					self.ZCIError(ZCI, "Module prefixes only allowed at beginning of name here.")



				# I.1) EXTRACTING MODULE NAMES

				#read module names until the end
				while not ZCI.inc():
					c = ZCI.get() #always using the same 'c'

					#end of current module name
					if c == '.':
						modules.append(currentModuleName)
						currentModuleName = ""

						#can't continue ? => ending ZCI text without giving the module element to target
						if ZCI.inc():
							zCtx.ZCIError(ZCI, "Missing an element name to target inside that module (reached end of ZCI)")

						#chaining with another module name (potentially) => continue in the same loop, else => break here, we reached our next "name" character
						c = ZCI.get()
						if c == '^':
							continue
						else:
							break

					#doubling underscores
					if c == '_':
						currentModuleName += '_'

					#not part of module name => break here, that one is the next "name" character actually
					if c not in DEFAULT_NAME_CHARSET:
						break

					#part of module name
					currentModuleName += c



				# I.2) SOLVE THEM

				#unfinished module name access
				if len(currentModuleName) != 0:
					self.ZCIError(ZCI, "Missing ending dot delimiter '.' when targetting something from module.")

				#there was no module names actually, it was just a lonely '^' => do as nothing happened
				if len(modules) == 0:
					name += '^'

				#at least one module name => add it to name
				else:

					#resolve implicit module naming
					for m in range(len(modules)):
						if len(modules[m]) == 0:
							if len(ZCI.modulePrefix) == 0:
								self.ZCIError(ZCI, "Can't resolve implicit module prefix, we are outside of any module.")
							modules[m] = ZCI.modulePrefix

					#add module prefix to our name
					name += 'M' + "_M".join(modules) + '_'

				#reached end of ZCI => regular end of name
				if ZCI.reachedEnd():
					break



			# II] STORE IN NAME OR STOP

			#stopping condition
			if blacklist is None:
				if c not in whitelist:
					break
			elif c in blacklist:
				break

			#allowed character => add it
			name += c
			if doubleUnderscores and c == '_':
				name += '_'

			#no longer in first character (maybe, getting rid of the "if" and keeping only the assignment would be more optimized ?)
			if firstCharacter:
				firstCharacter = False
		self.ZCIDeepDebug(ZCI, "Ended reading name.")

		#missing name field
		if len(name) == 0:
			if missingFieldIfError is None:
				return ""
			self.ZCIError(ZCI, "Missing or invalid name : " + missingFieldIfError)

		#return result
		return name



	def lookForFieldsAccessInDataItem(self, ZCI, di): #basically FFA application
		if di is None:
			return None

		#as long as we try to access fields
		while ZCI.get() == '.':
			fieldName = self.readName(ZCI, "Field from data item " + unprefixize(di.name))

			#found a field with that name in our dataItem
			fieldFound = None
			for f in di.fields:
				if f.name == fieldName:
					fieldFound = f
					break
			if fieldFound is None:
				self.ZCIError(ZCI, "Data item " + di.name + " has no field " + fieldName)

			#update result (field access)
			di = fieldFound

		#return result (whenever it has changed or not)
		return di



	#WARNING! This function is not to be used as part of ODP (symbol '^' should never refer to XOR operator)
	#         Technically, we should only use it in 2nd analysis.
	def tryReadDataItemIncludingFields(self, ZCI, scope):
		starter = ZCI.get()

		#read name (will have module prefix if any)
		name = self.readName(ZCI, "Any data item name", parseModulePrefixes=True, modulePrefix_asHeaderOnly=True),
		di   = None #just declare

		#case 1: having a module prefix => looking directly in global scope
		if starter == '^':
			for ldi in self.cpl.globalScope.dataItems:
				if name == ldi.name: #name should exactly correspond (full name given from readName in case of module prefix)
					di = ldi
					break

		#case 2: no module prefix => getting through every local elements until non-module global ones
		else:
			di = getDataItem(name, scope)

		#field access if any
		return self.lookForFieldsAccessInDataItem(ZCI, di)




