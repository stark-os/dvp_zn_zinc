#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx              import *
from pcpl.byteNotation import *






# -------- EXECUTION --------

#module
def p1_CommentsPItemText(zctx):
	output = ""
	if zctx.inc():
		return output



	# PREPARE FOR DETECTION

	#literal strings replacement
	currentString_length = 0
	currentString_data   = ""

	#fields detection
	inChr              = False
	inStr              = False
	inPotentialComment = False
	inSingleCom        = False
	inMultiCom         = False
	inPcplItem         = False
	pcplItem_name      = ""

	#useful for multi-line comments only : we don't really care about its value, must only be != '*'
	prevC = '_'

	#text special behavior
	isChrSet = False
	escaping = False

	#first character
	c = zctx.get()
	if c == '\'':
		inChr = True
	if c == '"':
		inStr = True
	if c == '/':
		inPotentialComment = True



	#ANALYSIS

	#parsing byte per byte
	while not zctx.inc():
		c = zctx.get()



		# IN FIELD : comment

		#in single-line comment => skip all
		if inSingleCom:
			if c == '\n':
				inSingleCom = False
				output += '\n'
			continue

		#in multi-line comment => skip all
		if inMultiCom:

			#must keep the same line number (for further pcpl steps)
			if c == '\n':
				output += '\n'

			#end of comment
			if (prevC == '*') and (c == '/'):
				inMultiCom = False
			prevC = c #store current character for next check
			continue



		# IN FIELD : chr

		#in character => translate it into byte notation
		if inChr:
			if not escaping:

				#end sequence
				if c == '\'':

					#too early : no character has been set yet
					if not isChrSet:
						zctx.error("Character definition requires at leat 1 element (empty character found).")
					inChr = False
					continue

				#special case : starting escape sequence
				if c == '\\':
					escaping = True
					continue

			#escaping or not => set character
			output += BN_fromChr(zctx, c, escaping=escaping)

			#check character length
			if isChrSet:
				zctx.error("Character definition allows only 1 element (at least 2 found).")
			isChrSet = True
			continue



		# IN FIELD : str

		#in string => translate it into multi-byte notation
		if inStr:
			if not escaping:

				#end sequence
				if c == '"':

					#write length
					output += "str{" + str(currentString_length) + "l,"

					#case 1: empty string (null data)
					if currentString_length == 0:
						output += "0l}"

					#case 2: anything else (multi-byte notation)
					else:
						output += BN_PREFIX + BN_PREFIX + currentString_data + '}'
					inStr = False
					continue

				#special case : starting escape sequence
				if c == '\\':
					escaping = True
					continue

			#escaping or not => set character
			currentString_data   += BN_fromChr(zctx, c, escaping=escaping)
			currentString_length += 1
			continue



		# IN FIELD : pcplItem

		#in pcplItem => store its name / replace it if we have the whole name
		if inPcplItem:

			#end detected
			if c == '>':
				inPcplItem = False

				#case 1 : empty name "<>" (not a pcplItem)
				if len(pcplItem_name) == 0:
					output += "<>"

				#case 2 : anything else
				else:
					piNotFound = True
					for pi in zctx.pcpl.items.keys():

						#found a definition => replace it
						if pcplItem_name == pi:
							output     += zctx.pcpl.items[pi]
							piNotFound  = False
							break

					#item not found => WARNING (text will be kept AS IS)
					if piNotFound:
						zctx.warning("Precompiler item \"" + pcplItem_name + "\" not found (in \"" + str(zctx.pcpl.items) + "\").")
				continue

			#valid content => fill variable name
			if c in PCPL_VAR_NAME_CHARSET:
				pcplItem_name += c
				continue

			#invalid content => cancel operation : that wasn't a Pcpl item
			else:
				output += '<' + pcplItem_name
				inPcplItem = False #do NOT use "continue", current character could be a beginning-of-string or anything



		# IN FIELD : Potential comment

		#potential comment detection
		if inPotentialComment:
			inPotentialComment = False

			#single-line comment detection
			if c == '/':
				inSingleCom = True
				continue

			#multi-line comment detection
			if c == '*':
				prevC      = '_' #does'nt really matter what that prevC is defined with. It must only be != '*'
				inMultiCom = True
				continue

			#that was'nt a comment => store previous slash before continuing in regular case
			output += '/'

		#potential comment found
		elif c == '/':
			inPotentialComment = True
			continue



		# OUT OF FIELD (non-text, non-comment, non-potential-comment & non-pcplItem)

		#characters detection
		if c == '\'':
			inChr    = True
			isChrSet = False
			continue

		#strings detection
		if c == '"':
			currentString_length = 0
			currentString_data   = ""
			inStr                = True
			continue

		#precompiler item
		if c == '<':
			pcplItem_name = ""
			inPcplItem    = True
			continue

		#nothing to detect => regular code
		output += c



	# END OF PARSING

	#incomplete definition
	if inMultiCom:
		zctx.error("Missing ending delimiter for multi-line comment (end of file reached too early).")
	if inChr:
		zctx.error("Missing ending delimiter for character (end of file reached too early).")
	if inStr:
		zctx.error("Missing ending delimiter for string (end of file reached too early).")
	if inPcplItem:
		zctx.error("Missing ending delimiter for precompilation variable (end of file reached too early).")

	#debug
	if zctx.debugMode:
		writeFile(zctx.ctx.filename + ".p1.z", output)

	#output now replaces previous file content : original => p1 version stored in memory (for further steps)
	zctx.ctx.reset(newText=output)
