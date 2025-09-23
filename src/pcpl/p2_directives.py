#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.string import *
from std.path   import *

#internal
from zctx import *






# -------- EXECUTION --------

#parse straightforward over cur context, trying to solve things out, as much as possible
def tryParseDirectives(zCtx):
	unparseableDirectives = [] #lst[parsingCtx]
	output                = ""

	#parsing states
	OUTSIDE       = 0
	BEFORE_NAME   = 1
	IN_NAME       = 2
	BEFORE_ZONE   = 3
	IN_ZONE       = 4
	parsingState  = OUTSIDE

	#parsing temporary vars
	hasNegation   = False
	directiveName = ""
	peerIdx       = 0
	zoneContent   = ""
	zoneLineFeeds = ""

	#all configs
	CFGKeys = zCtx.pcpl.cfgs.keys()

	#parsing byte per byte
	curText  = zCtx.ctx.icontent.s
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)



		#1) before config name
		if parsingState == BEFORE_NAME:
			if c not in BLANKS: #no more blank found => turn into "in name" mode
				CFGName      = ""
				parsingState = IN_NAME
			else: #blanks => skip them
 				continue



		#2) reading config name
		if parsingState == IN_NAME:
			if c not in DEFAULT_NAME_CHARSET: #end of config name => turn into "before zone" mode (can be empty)

				#unknown CFG name
				if CFGName not in CFGKeys:
					zCtx.err("Unknown precompiler configuration \"" + CFGName + "\".")
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
					zCtx.err("Invalid zone delimiter for precompiler configuration \"" + CFGName + "\" (must start with '{').")

				#as we said, no more blank found => turn into "in zone" mode
				zoneContent   = ""
				zoneLineFeeds = ""
				parsingState = IN_ZONE

				#get pairs until end of zone. Here, we don't care about other includers, only braces are taken into account
				curPairs = zCtx.ctx.getPairsUntilCorrespondingPeer(allowedPairs={'{':'}'})

				#error cases, limited : only 1 includer type taken into account => cannot have inconsistency
				if curPairs == PARSING_CTX__PEER_NOT_FOUND:
					zCtx.err("Missing end delimiter for precompiler configuration \"" + CFGName + "\" (corresponding '}' expected).")
				peerIdx = curPairs[zCtx.ctx.icontent.idx]
			continue



		#4) inside zone to consider
		if parsingState == IN_ZONE:
			if zCtx.ctx.icontent.idx == peerIdx:
				if zCtx.pcpl.cfgs[CFGName] != hasNegation: #apply configuration
					output += zoneContent
				else:
					output += zoneLineFeeds
				parsingState = OUTSIDE
				continue

			#just storing content elsewhere
			zoneContent += c
			if c == '\n':
				zoneLineFeeds += '\n' #keep valid line number in any case
			continue



		#5) outside anything
		if parsingState == OUTSIDE:
			curIdx = zCtx.ctx.icontent.idx

			# #CFG field detection
			if str_subEqual(curText, "#CFG", 4, first_from=curIdx):
				parsingState = BEFORE_NAME
				hasNegation  = False
				zCtx.ctx.forward(3) #jump after expression
				continue

			# #!CFG field detection
			if str_subEqual(curText, "#!CFG", 5, first_from=curIdx):
				parsingState = BEFORE_NAME
				hasNegation  = True
				zCtx__forward(zCtx, 4) #jump after expression
				continue

			#regular code
			output += c

	#write out result in given context
	zCtx__reset(zCtx, newText=output)

	#finished one-time parsing
	return unparseableDirectives



#apply precompiler configurations (environment-related modifications in code)
def p2_directives(zCtx):
	zCtx.step = STEP.P2
	zCtx.dbgSepLine()
	zCtx.dbg("============================================================================")
	zCtx.dbg("========================= P2 DIRECTIVES : beginning ========================")
	zCtx.dbg("============================================================================")
	zCtx.dbg("FILE: " + zCtx.ctx.filepath)
	zCtx.deepDbgPause()

	#parse once straightforward
	unparseableDirectives = tryParseDirectives(zCtx) #includes zCtx.reset() at the end

	#remaining directives to be resolved
	retry = 0
	while len(unparseableDirectives) != 0:

		#allowed
		if retry >= zCtx.pcpl.directivesMaxComplexity:
			zCtx.err("Unable to solve complexity of precompiler directives, can be cyclic dependencies or requireing more that the cur number of retries allowed:" + str(zCtx.pcpl.directivesMaxComplexity))

		#try again from the beginning (previous resolutions could have unlocked some other directives)
		unparseableDirectives = tryParseDirectives(zCtx)

	#debug
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p2.z", output)

	#debug
	zCtx.dbg("============================================================================")
	zCtx.dbg("============================ P2 DIRECTIVES : end ===========================")
	zCtx.dbg("============================================================================")
	zCtx.dbg("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgSepLine()
	zCtx.deepDbgPause()

	#debug
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p2.z", zCtx.ctx.icontent.s)

'''
# -------- EXECUTION --------

#module
def p1_commentsPItemsText(zCtx):

	# PREPARE FOR DETECTION

	#fields detection
	inPcplItm      = False
	pcplItmName    = ""

	#useful for multi-line comments only : we don't really care about its value, must only be != '*'
	prevC = '_'

	#ANALYSIS

	#parsing byte per byte
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)



		# IN FIELD : pcplItem

		#in pcplItm => store its name / replace it if we have the whole name
		if inPcplItm:

			#end detected
			if c == '>':
				inPcplItm = False

				#case 1 : empty name "<>" (not a pcplItem)
				if len(pcplItmName) == 0:
					output += "<>"

				#case 2 : anything else
				else:
					piNotFound = True
					for pi in zCtx.pcpl.itms.keys():

						#found a definition => replace it
						if pcplItmName == pi:
							output     += zCtx.pcpl.itms[pi]
							piNotFound  = False
							break

					#item not found => WARNING (text will be kept AS IS)
					if piNotFound:
						zCtx.warn("Precompiler item \"" + pcplItmName + "\" not found (in \"" + str(zCtx.pcpl.itms) + "\").")
				continue

			#valid content => fill variable name
			if c in DEFAULT_NAME_CHARSET: # = PCPL name charset
				pcplItmName += c
				continue

			#invalid content => cancel operation : that wasn't a Pcpl item
			else:
				output += '<' + pcplItmName
				inPcplItm = False #do NOT use "continue", cur character could be a beginning-of-string or anything



		# OUT OF FIELD (non-text, non-comment, non-potential-comment & non-pcplItem)

		#precompiler item
		if c == '<':
			pcplItmName = ""
			inPcplItm   = True
			continue

		#nothing to detect => regular code
		output += c



	# END OF PARSING

	#incomplete definition
	if inPcplItm:
		zCtx.err("Missing ending delimiter for precompilation variable (end of file reached too early).")
'''
