# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/generic.py

# GENERAL PARSING TOOLS

#move ctx cursor just before the first non-blank character found
def jumpBlankZone(ZCI, missingFieldIfErr, blanks=BLANKS): #!WARNING: we MUST be on a blank character before calling that function
	while not ZCI.inc():
		if ZCI.get() not in blanks:
			return
	if missingFieldIfErr is not None:
		ZCIErr(ZCI, "Expected something after blank zone: " + missingFieldIfErr)

def optionalBlanks(ZCI, missingFieldIfErr, blanks=BLANKS):
	if ZCI.get() in blanks:
		jumpBlankZone(ZCI, missingFieldIfErr, blanks=blanks)

def endOfZCI(ZCI, ZCIKindIfErr):
	if not ZCI.reachedEnd():
		ZCIErr(ZCI, "Too much elements in " + ZCIKindIfErr + " Should stop here.")






# REAL ZCE PARSING TOOLS (bare metal syntax-related)

#read hexadecimal byte
def readHexByte(ZCI):

	#read & check 1st digit
	h1 = ZCI.get()
	if h1 not in HEX_DIGITS_LOWERCASE:
		ZCIErr(ZCI, "Invalid first hexadecimal digit '" + h1 + "' given in byte notation.")

	#read & check 2nd digit
	if ZCI.inc():
		ZCIErr(ZCI, "Missing second hexadecimal digit in byte notation.")
	h0 = ZCI.get()
	if h0 not in HEX_DIGITS_LOWERCASE:
		ZCIErr(ZCI, "Invalid second hexadecimal digit '" + h0 + "' given in byte notation.")

	#return byte
	return hex_toS8(h1, h0)



#try reading symbol (don't move ZCI ctx)
def readSym(ZCI):
	ZCIDeepDbg(ZCI, "Reading symbol.")
	tmpZCI = ZCI.copy()
	c1 = tmpZCI.get()

	#1-character symbol
	if c1 == '~':
		return SYM__SIN
	elif c1 == '/':
		return SYM__ADI
	elif c1 == '+':
		return SYM__BAD
	elif c1 == '%':
		return SYM__AMO
	elif c1 == '^':
		return SYM__LXO
	elif c1 == '#':
		return SYM__FSZ
	elif c1 == '@':
		return SYM__FRF
	elif c1 == '$':
		return SYM__FCA
	elif c1 == '.':
		return SYM__FFA

	#multi-character symbol: starting with '!'
	elif c1 == '!':
		tmpZCI.inc()
		c2 = tmpZCI.get()
		if c2 == '=':
			return SYM__CNE
		elif c2 == '?':
			return SYM__INA
		return SYM__SNO

	#multi-character symbol: starting with '*'
	elif c1 == '*':
		if tmpZCI.inc():
			return SYM__AMU
		if tmpZCI.get() == '*':
			return SYM__APO
		return SYM__AMU

	#multi-character symbol: starting with '&'
	elif c1 == '&':
		if tmpZCI.inc():
			return SYM__LAN #ending with lonely '&'
		if tmpZCI.get() == '&':
			return SYM__DAN
		return SYM__LAN

	#multi-character symbol: starting with '|'
	elif c1 == '|':
		tmpZCI.inc()
		c2 = tmpZCI.get()
		if c2 == '|':
			return SYM__DOR
		elif c2 == '<':
			if tmpZCI.inc():
				return SYM__LOR
			if tmpZCI.get() == '<':
				return SYM__LLB
		return SYM__LOR

	#multi-character symbol: starting with '-'
	elif c1 == '-':
		tmpZCI.inc()
		if tmpZCI.get() == '>':
			if tmpZCI.inc():
				return SYM__BSU
			if tmpZCI.get() == '>':
				return SYM__LRR
		return SYM__BSU

	#multi-character symbol: starting with '<'
	elif c1 == '<':
		if tmpZCI.inc():
			return SYM__CLT
		c2 = tmpZCI.get()
		if c2 == '=':
			return SYM__CLE
		elif c2 == '<':
			if tmpZCI.inc():
				return SYM__LLS
			if tmpZCI.get() == '-':
				return SYM__LLR
			return SYM__LLS
		return SYM__CLT

	#multi-character symbol: starting with '>'
	elif c1 == '>':
		if tmpZCI.inc():
			return SYM__CGT
		c2 = tmpZCI.get()
		if c2 == '=':
			return SYM__CGE
		elif c2 == '>':
			if tmpZCI.inc():
				return SYM__LRS
			if tmpZCI.get() == '|':
				return SYM__LRB
			return SYM__LRS
		return SYM__CGT

	#multi-character symbol: starting with '='
	elif c1 == '=':
		if tmpZCI.inc():
			return SYM__ASG
		if tmpZCI.get() == '=':
			return SYM__CEQ
		return SYM__ASG

	#multi-character symbol: starting with '?'
	elif c1 == '?':
		return SYM__IAM

	#no match
	return SYM__NOT_FOUND



#read a name according to the given charset (either blacklist or whitelist)
# IMPORTANT : Reading ZCI ctx from its CURRENT position and move it right AFTER the extracted result
#also, blacklist is prioritary : if null => use whitelist, else, use it (no matter whitelist value)
#
# /!\ This method must be included in STDZ into ^Parsing.ctx whithout the module prefix part.
#     Must also include the first 2 lines of comment over it
#
def readName(ZCI,
	missingFieldIfErr, #null means "don't raise error if empty"
	blacklist=None, whitelist=DEFAULT_NAME_CHARSET,
	dblUnderscores=False,
	parseModPfxes=False
):
	ZCIDeepDbg(ZCI, "Reading name.")
	if parseModPfxes:
		dblUnderscores = True #doesn't make sens to double underscores in module prefixes but not in the name => force it

	#read until given blacklist/whitelist no longer matches
	modPfx   = "G"
	rawName  = ""
	firstChr = True
	while True:
		if not firstChr: #skip ZCI.inc() for first character only
			if ZCI.inc():
				break
		c = ZCI.get()



		# I] MODULE PREFIX PARSING

		#module prefix detection
		if parseModPfxes and c == '^':
			modPfx     = "" #no longer out-of-mod
			mods       = []
			curModName = ""

			#only allowing it as name header
			if not firstChr:
				if missingFieldIfErr is None:
					return ("", "")
				ZCIErr(ZCI, "Module prefixes only allowed at beginning of name here, in " + missingFieldIfErr)



			# I.1) EXTRACTING MODULE NAMES

			#read module names until the end
			while not ZCI.inc():
				c = ZCI.get() #always using the same 'c'

				#end of cur module name
				if c == '.':
					mods.append(curModName)
					curModName = ""

					#can't continue ? => ending ZCI text without giving the module element to target
					if ZCI.inc():
						if missingFieldIfErr is None:
							return ("", "")
						ZCIErr(ZCI, "Missing an element name to target inside that module (reached end of ZCI), in " + missingFieldIfErr)

					#chaining with another module name (potentially) => continue in the same loop, else => break here, we reached our next "name" character
					c = ZCI.get()
					if c == '^':
						continue
					else:
						break

				#doubling underscores
				if c == '_':
					curModName += '_'

				#not part of module name => break here, that one is the next "name" character actually
				if c not in DEFAULT_NAME_CHARSET:
					break

				#part of module name
				curModName += c



			# I.2) SOLVE THEM

			#unfinished module name access
			if len(curModName) != 0:
				if missingFieldIfErr is None:
					return ("", "")
				ZCIErr(ZCI, "Missing ending dot delimiter '.' when targetting something from module, in " + missingFieldIfErr)

			#there was no module names actually, it was just a lonely '^' => do as nothing happened
			if len(mods) == 0:
				modPfx   = "G"
				rawName += '^'

			#at least one module name => add it/them to name
			else:
				for m in range(len(mods)):

					#no module name given => resolve implicit naming
					if len(mods[m]) == 0:
						if len(ZCI.modPfx) == 0:
							if missingFieldIfErr is None:
								return ("", "")
							ZCIErr(ZCI, "Can't resolve implicit module prefix, we are outside of any module, in " + missingFieldIfErr)
						modPfx += ZCI.modPfx

					#prefixing them eitherway
					else:
						modPfx += 'M' + mods[m] + '_'

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
		rawName += c
		if dblUnderscores and c == '_':
			rawName += '_'

		#no longer in first character (maybe, getting rid of the "if" and keeping only the assignment would be more optimized ?)
		if firstChr:
			firstChr = False
	ZCIDeepDbg(ZCI, "Ended reading name.")

	#missing raw name field
	if len(rawName) == 0:
		if missingFieldIfErr is None:
			return ("", "")
		ZCIErr(ZCI, "Missing or invalid name, in " + missingFieldIfErr)

	#return result
	return (modPfx, rawName)



def lookForFieldsAccessInDatItm(ZCI, di): #basically, for FFA application
	if di is None:
		return None

	#as long as we try to access fields
	while ZCI.get() == '.':
		fieldName = readName(ZCI, "Field from data item " + unpfx(di.name))[1]

		#found a field with that name in our dataItem
		fieldFound = None
		for f in di.fields:
			if f.name == fieldName:
				fieldFound = f
				break
		if fieldFound is None:
			ZCIErr(ZCI, "Data item " + di.name + " has no field " + fieldName)

		#update result (field access)
		di = fieldFound

	#return result (whenever it has changed or not)
	return di
