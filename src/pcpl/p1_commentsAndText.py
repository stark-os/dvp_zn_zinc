#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.path import *

#internal
from zctx              import *
from pcpl.byteNotation import *






# -------- EXECUTION --------

#module
def p1_commentsAndText(zCtx):
	zCtx.updateLogLvl(STEP.P1)
	zCtx.dbgSepLine()
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("===================== P1 COMMENTS AND TEXT : beginning =====================")
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgPause()

	#empty file
	if zCtx__inc(zCtx):
		zCtx.err("Empty file given, nothing to compile.")



	# PREPARE FOR DETECTION

	#literal strings replacement
	curStrDat = ""

	#fields detection
	inChr          = False
	inStr          = False
	inPotentialCom = False
	comBegCtx      = [None] #will only contain 1 element, this is to be used as "subCtxs" in zctx.overwriteSubCtxs()
	inSingleCom    = False
	inMultiCom     = False

	#useful for multi-line comments only : we don't really care about its value, must only be != '*'
	prevC = '_'

	#text special behavior
	isChrSet = False
	escaping = False

	#first character
	output = ""
	c      = zCtx__get(zCtx)
	if c == '\'':
		inChr = True
	elif c == '"':
		inStr = True
	elif c == '/':
		inPotentialCom = True
	else:
		output += c



	#ANALYSIS

	#parsing byte per byte
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)



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
						zCtx.err("Character definition requires at leat 1 element (empty character found).")
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
			output += '(' + BN_PFX + BN_fromChr(zCtx, c, escaping=escaping) + "$chr)" #parentheses should not be mandatory because casht must be prioritary in any way (safety)

			#check character length
			if isChrSet:
				zCtx.err("Character definition allows only 1 element (at least 2 found).")
			isChrSet = True
			continue



		# IN FIELD : str

		#in string => translate it into multi-byte notation
		if inStr:
			if not escaping:

				#end sequence
				if c == '"':

					#store aside for further treatment (multi-byte notation)
					zCtx.pcpl.litStr.append(curStrDat)

					#set corresponding data item instead
					output += zCtx.pcpl.nextLitStrDIName() + ".dat"
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
			curStrDat += BN_fromChr(zCtx, c, escaping=escaping)
			continue



		# IN FIELD : Potential comment

		#potential comment detection
		if inPotentialCom:
			inPotentialCom = False

			#single-line comment detection
			if c == '/':
				inSingleCom = True
				continue

			#multi-line comment detection
			if c == '*':
				comBegCtx[0] = zCtx.ctx.copy() #keep track of comment beginning
				prevC        = '_' #does'nt really matter what that prevC is defined with. It must only be != '*'
				inMultiCom   = True
				continue

			#that was'nt a comment => store previous slash before continuing in regular case
			output += '/'

		#potential comment found
		elif c == '/':
			inPotentialCom = True
			continue



		# OUT OF FIELD (non-text, non-comment, non-potential-comment)

		#characters detection
		if c == '\'':
			inChr    = True
			isChrSet = False
			continue

		#strings detection
		if c == '"':
			curStrDat = ""
			inStr     = True
			continue

		#nothing to detect => regular code
		output += c



	# END OF PARSING

	#incomplete definition
	if inMultiCom:
		zCtx__overwriteSubCtxs(zCtx, comBegCtx)
		zCtx.err("Missing ending delimiter for multi-line comment (end of file reached too early).")
	if inChr:
		zCtx.err("Missing ending delimiter for character (end of file reached too early).")
	if inStr:
		zCtx.err("Missing ending delimiter for string (end of file reached too early).")

	#debug
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("======================== P1 COMMENTS AND TEXT : end ========================")
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()
		writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p1.z", output)

	#output now replaces previous file content : original => p1 version stored in memory (for further steps)
	zCtx__reset(zCtx, newText=output)
