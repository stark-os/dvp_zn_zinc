#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.path import *

#internal
from zctx              import *
from pcpl.byteNotation import *






# -------- EXECUTION --------

#module
def p1_CommentsPItemsText(zCtx):
	output = ""
	if zCtx.inc():
		return output



	# PREPARE FOR DETECTION

	#literal strings replacement
	currentString_length = 0
	currentString_data   = ""

	#fields detection
	inChr               = False
	inStr               = False
	inPotentialComment  = False
	commentBeginningCtx = [None] #will only contain 1 element, this is to be used as "subCtxs" in zctx.overwriteSubCtxs()
	inSingleCom         = False
	inMultiCom          = False
	inPcplItem          = False
	pcplItem_name       = ""

	#useful for multi-line comments only : we don't really care about its value, must only be != '*'
	prevC = '_'

	#text special behavior
	isChrSet = False
	escaping = False

	#first character
	c = zCtx.get()
	if c == '\'':
		inChr = True
	elif c == '"':
		inStr = True
	elif c == '/':
		inPotentialComment = True
	else:
		output += c



	#ANALYSIS

	#parsing byte per byte
	while not zCtx.inc():
		c = zCtx.get()



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
						zCtx.error("Character definition requires at leat 1 element (empty character found).")
					inChr = False
					continue

				#special case : starting escape sequence
				if c == '\\':
					escaping = True
					continue

			#turn back into regular mode
			else:
				escaping = False

			#escaping or not => set character
			output += BN_fromChr(zCtx, c, escaping=escaping)

			#check character length
			if isChrSet:
				zCtx.error("Character definition allows only 1 element (at least 2 found).")
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

			#turn back to regular character mode
			else:
				escaping = False

			#escaping or not => set character
			currentString_data   += BN_fromChr(zCtx, c, escaping=escaping)
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
					for pi in zCtx.pcpl.items.keys():

						#found a definition => replace it
						if pcplItem_name == pi:
							output     += zCtx.pcpl.items[pi]
							piNotFound  = False
							break

					#item not found => WARNING (text will be kept AS IS)
					if piNotFound:
						zCtx.warning("Precompiler item \"" + pcplItem_name + "\" not found (in \"" + str(zCtx.pcpl.items) + "\").")
				continue

			#valid content => fill variable name
			if c in DEFAULT_NAME_CHARSET: # = PCPL name charset
				pcplItem_name += c
				continue

			#invalid content => cancel operation : that wasn't a Pcpl item
			else:
				output += '<' + pcplItem_name
				inPcplItem = False #do NOT use "continue", current character could be a beginning-of-string or anything



		# IN FIELD : Potential comment

		#potential comment detection
		if inPotentialComment:
			inPotentialComment     = False

			#single-line comment detection
			if c == '/':
				inSingleCom = True
				continue

			#multi-line comment detection
			if c == '*':
				commentBeginningCtx[0] = zCtx.ctx.copy(copyContent=False) #keep track of comment beginning
				prevC                  = '_' #does'nt really matter what that prevC is defined with. It must only be != '*'
				inMultiCom             = True
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
		zCtx.overwriteSubCtxs(commentBeginningCtx)
		zCtx.error("Missing ending delimiter for multi-line comment (end of file reached too early).")
	if inChr:
		zCtx.error("Missing ending delimiter for character (end of file reached too early).")
	if inStr:
		zCtx.error("Missing ending delimiter for string (end of file reached too early).")
	if inPcplItem:
		zCtx.error("Missing ending delimiter for precompilation variable (end of file reached too early).")

	#debug
	if zCtx.debugMode:
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p1.z", output)

	#output now replaces previous file content : original => p1 version stored in memory (for further steps)
	zCtx.ctx.reset(newText=output)
