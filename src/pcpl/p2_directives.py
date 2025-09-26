#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.string import *
from std.path   import *

#internal
from pcpl.arithmetic import *
from pcpl.parsing    import *
from zctx import *






# -------- DIRECTIVES --------

#SET
def PCPL__processSET(zCtx):
	PCPL__jumpBlankZone(zCtx, "SET")

	#read & check name given
	name = PCPL__readUntil(zCtx, BLANKS)
	PCPL__checkNameCharset(zCtx, name)
	if PCPL__getItemText(zCtx, name) is not None:
		zCtx.err("Already have precompiler item with name \"" + name + "\".")

	#read associated value
	PCPL__jumpBlankZone(zCtx, "SET")
	valueText = PCPL__readItemValue(zCtx)

	#value could not be solved yet => cancel directive
	if valueText is None:
		return None

	#else, add pcpl item (success)
	zCtx.dbg("Adding PCPL item \"" + name + "\" with value \"" + valueText + "\".")
	zCtx.pcpl.inCodeItms[name] = valueText

	#success => should return empty text BUT HERE, current zCtx.ctx is right AFTER value text (+1), and next step in main parsing loop will be to inc() => we will lose that character (which can only be a BLANK btw) => add it manually
	return zCtx__get(zCtx)



#!SET
def PCPL__processUnSET(zCtx):
	PCPL__jumpBlankZone(zCtx, "!SET")

	#read & check name given
	name = PCPL__readUntil(zCtx, BLANKS_EXTENDED) #1st and only field => must allow line feeds
	PCPL__checkNameCharset(zCtx, name)

	#must not affect items from cfg file
	if name in zCtx.pcpl.inCfgItms.keys():
		zCtx.err("Trying to modify precompiler item that has been defined in local cfg/pcpl_itms.cfg => FORBIDDEN.")

	#not even in the previously declared ones
	if name not in zCtx.pcpl.inCodeItms.keys():
		zCtx.err("No precompiler item with name \"" + name + "\" allowing to be unset.")

	#else, remove item
	zCtx.dbg("Removing PCPL item \"" + name + "\".")
	zCtx.pcpl.inCodeItms.pop(name)

	#success => should return empty text BUT HERE, current zCtx.ctx is right AFTER name (+1), and next step in main parsing loop will be to inc() => we will lose that character (which can only be a BLANK btw) => add it manually
	return zCtx__get(zCtx)



#CFG & !CFG (can't return null btw)
def PCPL__processCFG(zCtx, negation):
	PCPL__jumpBlankZone(zCtx, "CFG")

	#read & check cfg name given
	cfgName = PCPL__readUntil(zCtx, BLANKS)
	PCPL__checkNameCharset(zCtx, cfgName)

	#not even in cfgs
	if cfgName not in zCtx.pcpl.cfgs.keys():
		zCtx.err("No precompiler configuration with name \"" + name + "\" (in cfg/pcpl_cfgs.cfg).")

	#then, get concerned zone as 2nd argument
	PCPL__jumpBlankZone(zCtx, "CFG")
	if zCtx__get(zCtx) != '{':
		zCtx.err("Expecting a braces includer here to define targetted zone of precompiler CFG directive.")
	block = PCPL__readIncluderBlock(zCtx)

	#apply negation
	applyCfg = zCtx.pcpl.cfgs[cfgName]
	if negation:
		applyCfg = not applyCfg

	#cfg active => enable block in code
	if applyCfg:
		return block

	#cfg inactive => skip it (respecting line nbr by giving the same amount of line feeds)
	return '\n' * block.count('\n')



#FOR
def PCPL__processFOR(zCtx):
	PCPL__jumpBlankZone(zCtx, "FOR")

	#read iter var name given
	iterVarName = PCPL__readUntil(zCtx, BLANKS)
	PCPL__checkNameCharset(zCtx, iterVarName)

	#name already used in items
	if PCPL__getItemText(zCtx, iterVarName) is not None:
		zCtx.err("Already have precompiler item with name \"" + name + "\", can't use the same name as iteration variable in FOR precompiler directive.")

	#read iter range
	PCPL__jumpBlankZone(zCtx, "FOR")
	if zCtx__get(zCtx) != '{':
		zCtx.err("Expecting a braces includer here to define iteration range of precompiler FOR directive.")
	iterRange = PCPL__readIncluderBlock(zCtx)

	#read each value given in iter range
	textValues  = []
	curIdx      = -1
	iIterRange  = istr(iterRange)
	afterBlanks = True
	while not iIterRange.inc():
		c = iIterRange.get()

		#skip blanks
		if c in BLANKS_EXTENDED:
			afterBlanks = True
			continue

		#add new text value
		if afterBlanks:
			textValues.append("")
			curIdx += 1
			afterBlanks = False

		#add cur chr to cur textValue
		textValues[curIdx] += c

	#take a look at each textValue
	for tv in range(len(textValues)):
		solvedTextValue = PCPL__ATH__solveArithmetic(zCtx, textValues[tv]) #try to solve arithmetically

		#unsolvable => invalid
		if solvedTextValue is None:
			return None
		textValues[tv]  = solvedTextValue

		#sub-directive => stop here then, we must have 0 complexity
		if tv[0] == '#':
			zCtx.dbg("Found a sub-directive in FOR range values => stop here, it must be solved first.")
			return None

	#finally, get concerned zone
	zCtx__inc(zCtx) #move right after closing includer of iter range
	PCPL__jumpBlankZone(zCtx, "FOR")
	if zCtx__get(zCtx) != '{':
		zCtx.err("Expecting a braces includer here to define iteration range of precompiler FOR directive.")
	block = PCPL__readIncluderBlock(zCtx)

	#proceed to code duplication for each iteration
	res = ""
	for tv in textValues:
		res += "#SET " + iterVarName + " " + tv + " " #define iter var just during for each iteration
		res += block
		res += "#!SET " + iterVarName + " "
	return res






# -------- EXECUTION --------

#react to directive execution result
def resumeAfterProcessingDirective(directiveResText, unparseableDirectives, initialCtx):
	if directiveResText is None:
		zCtx.ctx.resetCtx(initialCtx)
		unparseableDirectives.append(initialCtx)
		return '#'
	return directiveResText



#parse straightforward over cur context, trying to solve things out, as much as possible
def tryParseDirectives(zCtx):
	unparseableDirectives = [] #lst[parsingCtx]
	output                = ""

	#parsing temporary vars
	peerIdx       = 0
	zoneContent   = ""
	zoneLineFeeds = ""

	#all configs
	CFGKeys = zCtx.pcpl.cfgs.keys()

	#parsing byte per byte
	curText = zCtx.ctx.icontent.s
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)

		#potentially found PCPL instruction
		if c == '#':
			initialCtx = zCtx.ctx.copy()



			#CASE 1: LOOK FOR DIRECTIVE

			#read 1st chr
			if not zCtx__inc(zCtx):
				directiveName = zCtx__get(zCtx) #str = chr

				#found a negation => read one more
				if directiveName[0] == '!':
					if zCtx__inc(zCtx):
						zCtx.err("Seems to have a precompiler directive with negation here, but name is missing.")
					directiveName += zCtx__get(zCtx)

				#read the 2 remaining chr from directive name, else, do not considerate as a directive (can be a regular FSZ operator with following value)
				if not zCtx__inc(zCtx):
					directiveName += zCtx__get(zCtx)
					if not zCtx__inc(zCtx):
						directiveName += zCtx__get(zCtx) #got full directive name, now time to analyze it

						#CFG
						if directiveName == "CFG":
							output += resumeAfterProcessingDirective(
								PCPL__processCFG(zCtx, False),
								unparseableDirectives,
								initialCtx
							)
							continue

						#!CFG
						if directiveName == "!CFG":
							output += resumeAfterProcessingDirective(
								PCPL__processCFG(zCtx, True),
								unparseableDirectives,
								initialCtx
							)
							continue

						#SET
						elif directiveName == "SET":
							output += resumeAfterProcessingDirective(
								PCPL__processSET(zCtx),
								unparseableDirectives,
								initialCtx
							)
							continue

						#!SET
						elif directiveName == "!SET":
							output += resumeAfterProcessingDirective(
								PCPL__processUnSET(zCtx),
								unparseableDirectives,
								initialCtx
							)
							continue

						#FOR
						elif directiveName == "FOR":
							output += resumeAfterProcessingDirective(
								PCPL__processFOR(zCtx),
								unparseableDirectives,
								initialCtx
							)
							unparseableDirectives.append(initialCtx) #add unparseable directive in all cases because FOR resolution produces
							continue

			#any other case that could not be processed entierly => cancel parsing
			zCtx.ctx.resetCtx(initialCtx)



			#CASE 2: LOOK FOR ITEM NAME

			#only consider if there is at least one more chr to read
			if not zCtx__inc(zCtx):
				c = zCtx__get(zCtx)

				#2 hashes in a row => consider having an directive inside another => unparseable yet => cancel
				if c == '#':
					zCtx.dbg("Got 2 '#' in a row, maybe it is a directive inside another => FAILURE.")
					output += resumeAfterProcessingDirective(None, unparseableDirectives, initialCtx)
					continue

				#lonely hash => cancel (not a directive at all)
				if c in BLANKS:
					zCtx.dbg("Got lonely '#' => not even a PCPL directive.")
					output += "#" + c
					continue

				#read name or expression
				name = PCPL__readUntil(zCtx, BLANKS+"#")
				if zCtx__reachedEnd(zCtx):
					c = ""
				else:
					c = zCtx__get(zCtx)

				#case 1: arithmetic expression
				if PCPL__ATH__containsOperator(name):
					tgtText = PCPL__ATH__solveArithmetic(zCtx, name)

				#case 2: item name
				else:
					PCPL__checkNameCharset(zCtx, name) #MUST be a valid name
					tgtText = PCPL__getItemText(zCtx, name)

				#unparseable yet => add to list and then cancel
				if tgtText is None:
					output += resumeAfterProcessingDirective(None, unparseableDirectives, initialCtx)
					continue

				#parseable => replace PCPL instruction
				else:
					output += tgtText

		#regular code (unchanged)
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
	zCtx.dbg("1st try for parsing PCPL directives.")
	unparseableDirectives = tryParseDirectives(zCtx) #includes zCtx.reset() at the end

	#remaining directives to be resolved
	retry = 0
	while len(unparseableDirectives) != 0:

		#macimum retries reached
		if retry >= zCtx.pcpl.directivesMaxComplexity:
			zCtx.err("Unable to solve complexity of precompiler directives, can be cyclic dependencies or requireing more that the cur number of retries allowed:" + str(zCtx.pcpl.directivesMaxComplexity))

		#try again from the beginning (previous resolutions could have unlocked some other directives)
		zCtx.dbg("Retry parsing PCPL directives: " + str(retry))
		unparseableDirectives = tryParseDirectives(zCtx)
		retry += 1

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
