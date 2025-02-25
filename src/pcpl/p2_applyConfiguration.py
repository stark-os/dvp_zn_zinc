#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.string import *
from std.path   import *

#internal
from zctx import *






# -------- EXECUTION --------

#apply precompiler configurations (environment-related modifications in code)
def p2_applyConfiguration(zCtx):
	output = ""

	#parsing states
	OUTSIDE       = 0
	BEFORE_NAME   = 1
	IN_NAME       = 2
	BEFORE_ZONE   = 3
	IN_ZONE       = 4
	parsingState  = OUTSIDE

	#parsing temporary vars
	hasNegation   = False
	CFGName       = ""
	peerIndex     = 0
	zoneContent   = ""
	zoneLineFeeds = ""

	#all configs
	CFGKeys = zCtx.pcpl.configs.keys()

	#parsing byte per byte
	currentText  = zCtx.ctx.icontent.s
	while not zCtx.inc():
		c = zCtx.get()



		#1) before config name
		if parsingState == BEFORE_NAME:
			if c not in BLANKS: #no more blank found => turn into "in name" mode
				CFGName      = ""
				parsingState = IN_NAME
			else: #do not forward if still in blanks
 				continue



		#2) reading config name
		if parsingState == IN_NAME:
			if c not in PCPL_VAR_NAME_CHARSET: #end of config name => turn into "before zone" mode (can be empty)

				#unknown CFG name
				if CFGName not in CFGKeys:
					zCtx.error("Unknown precompiler configuration \"" + CFGName + "\".")
				parsingState = BEFORE_ZONE

			#storing config name
			else:
				CFGName += c
				continue



		#3) before zone delimiters
		if parsingState == BEFORE_ZONE:
			if c not in BLANKS: #end of "before zone" => getting "in zone" mode

				#error case
				if c != '{':
					zCtx.error("Invalid zone delimiter for precompiler configuration \"" + CFGName + "\" (must start with '{').")

				#as we said, no more blank found => turn into "in zone" mode
				zoneContent   = ""
				zoneLineFeeds = ""
				parsingState = IN_ZONE

				#get index of its peer (end of zone). Here, we don't care about other includers,
				peerIndex = zCtx.ctx.getCorrespondingPeerIndex(peers={'{':'}'}) #only braces are taken into account

				#error cases: -1 must never occur (c == '{'), neither -2 (only 1 includer type taken into account => cannot have inconsistency)
				if peerIndex == -3:
					zCtx.error("Missing end delimiter for precompiler configuration \"" + CFGName + "\" (corresponding '}' expected).")
				if peerIndex < 0:
					zCtx.internal("Negative peerIndex found in PCPL CFG parsing.")
				continue
			continue



		#4) inside zone to consider
		if parsingState == IN_ZONE:
			if zCtx.ctx.icontent.index == peerIndex:
				if zCtx.pcpl.configs[CFGName] != hasNegation: #apply configuration
					output += zoneContent
				else:
					output += zoneLineFeeds
				parsingState = OUTSIDE

			#just storing content elsewhere
			zoneContent += c
			if c == '\n':
				zoneLineFeeds += '\n' #keep valid line number in any case
			continue



		#5) outside anything
		if parsingState == OUTSIDE:
			currentIndex = zCtx.ctx.icontent.index

			# #CFG field detection
			if str_subEqual(currentText, "#CFG", 4, first_from=currentIndex):
				parsingState = BEFORE_NAME
				hasNegation  = False
				zCtx.ctx.forward(3) #jump after expression
				continue

			# #!CFG field detection
			if str_subEqual(currentText, "#!CFG", 5, first_from=currentIndex):
				parsingState = BEFORE_NAME
				hasNegation  = True
				zCtx.ctx.forward(4) #jump after expression
				continue

			#regular code
			output += c

	#debug
	if zCtx.debugMode:
		writeFile(path_name(zCtx.ctx.filename) + ".p2.z", output)

	#output now replaces previous ctx content : p1 version => p2 version stored in memory (for further steps)
	zCtx.ctx.reset(newText=output)
