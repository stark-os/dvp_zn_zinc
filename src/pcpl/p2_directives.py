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
	zCtx.dbg("Processing PCPL directive \"SET\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "SET")

	#read name given
	name = PCPL__readUntil(zCtx, BLANKS)
	if '#' in name:
		zCtx.deepDbg("Found PCPL sub directive in item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures += 1
		return None

	#check name charset
	PCPL__checkNameCharset(zCtx, name)
	if PCPL__getItemText(zCtx, name) is not None:
		zCtx.err("Already have precompiler item with name \"" + name + "\".")

	#read associated value
	PCPL__jumpBlankZone(zCtx, "SET")
	valueText = PCPL__readItemValue(zCtx)

	#value could not be solved yet => cancel directive
	if valueText is None:
		zCtx.pcpl.failures += 1
		return None

	#else, add pcpl item (success)
	zCtx.dbg("Adding PCPL item \"" + name + "\" with value \"" + valueText + "\".")
	zCtx.pcpl.inCodeItms[name] = valueText

	#success
	zCtx.dbg("Processed PCPL directive \"SET\" => SUCCESS")
	return ""



#!SET
def PCPL__processUnSET(zCtx):
	zCtx.dbg("Processing PCPL directive \"!SET\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "!SET")

	#read name given
	name = PCPL__readUntil(zCtx, BLANKS_EXTENDED) #1st and only field => must allow line feeds
	if '#' in name:
		zCtx.deepDbg("Found PCPL sub directive in item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures += 1
		return None

	#check name charset
	PCPL__checkNameCharset(zCtx, name)

	#must not affect items from cfg file
	if name in zCtx.pcpl.inCfgItms.keys():
		zCtx.err("Trying to modify precompiler item that has been defined in local cfg/pcpl_itms.cfg => FORBIDDEN.")

	#not even in the previously declared ones
	if name not in zCtx.pcpl.inCodeItms.keys():
		zCtx.dbg("No precompiler item with name \"" + name + "\" allowing to be unset => FAILURE.")
		zCtx.pcpl.failures += 1
		return None

	#else, remove item
	zCtx.dbg("Removing PCPL item \"" + name + "\".")
	zCtx.pcpl.inCodeItms.pop(name)

	#success
	zCtx.dbg("Processed PCPL directive \"!SET\" => SUCCESS")
	return ""



#CFG & !CFG (can't return null btw)
def PCPL__processCFG(zCtx, negation):
	zCtx.dbg("Processing PCPL directive \"(!)CFG\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "CFG")

	#read & check cfg name given
	cfgName = PCPL__readUntil(zCtx, BLANKS+('{',))
	PCPL__checkNameCharset(zCtx, cfgName)

	#not even in cfgs
	if cfgName not in zCtx.pcpl.cfgs.keys():
		zCtx.err("No precompiler configuration with name \"" + cfgName + "\" (in cfg/pcpl_cfgs.cfg).")

	#then, get concerned zone as 2nd argument
	if zCtx__get(zCtx) in BLANKS:
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
		zCtx.deepDbg("Processed PCPL directive \"CFG\" => SUCCESS")
		return block

	#cfg inactive => skip it (respecting line nbr by giving the same amount of line feeds)
	zCtx.dbg("Processed PCPL directive \"!CFG\" => SUCCESS")
	return '\n' * block.count('\n')



#FOR
def PCPL__processFOR(zCtx):
	zCtx.dbg("Processing PCPL directive \"FOR\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "FOR")

	#read iter var name given
	iterVarName = PCPL__readUntil(zCtx, BLANKS)
	if '#' in iterVarName:
		zCtx.deepDbg("Found PCPL sub directive in item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures += 1
		return None

	#check name charset
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
	txtValues  = []
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
			txtValues.append("")
			curIdx += 1
			afterBlanks = False

		#add cur chr to cur txtValue
		txtValues[curIdx] += c

	#take a look at each txtValue
	for tv in range(len(txtValues)):

		#sub-directive => stop here then, we must have 0 complexity
		if txtValues[tv][0] == '#':
			zCtx.dbg("Found a sub-directive in FOR range values => stop here, it must be solved first.")
			zCtx.pcpl.failures += 1
			return None

	#finally, get concerned zone
	PCPL__jumpBlankZone(zCtx, "FOR")
	if zCtx__get(zCtx) != '{':
		zCtx.err("Expecting a braces includer here to define iteration range of precompiler FOR directive.")
	block = PCPL__readIncluderBlock(zCtx)

	#proceed to code duplication for each iteration
	res = ""
	for tv in txtValues:
		res += "#SET " + iterVarName + " " + tv + " " #define iter var just during for each iteration
		res += block
		res += "#!SET " + iterVarName + " "
	zCtx.dbg("Processed PCPL directive \"FOR\" => SUCCESS")
	return res






# -------- EXECUTION --------

#specific directive redirection
def getDirectiveText(zCtx):

	#read 1st following chr
	if zCtx__inc(zCtx):
		return None
	c = zCtx__get(zCtx) #str = chr


	#lonely hash => cancel (not a directive at all)
	if c in BLANKS:
		return None

	#2 hashes in a row => consider having an directive inside another => unparseable yet => FAILURE
	elif c == '#':
		zCtx.dbg("Got 2 '#' in a row, maybe it is a directive inside another => FAILURE.")
		zCtx.pcpl.failures += 1
		return None



	#CASE 1: ITEM NAME

	#braces includer directly => targetting a PCPL item
	if c == '{':
		zCtx.deepDbg("Looking for a PCPL item name.")
		name = PCPL__readIncluderBlock(zCtx)

		#sub directive => unparseable yet => cancel
		if '#' in name:
			zCtx.dbg("Got sub directive in PCPL name, unparseable yet => FAILURE.")
			zCtx.pcpl.failures += 1
			return None

		#get corresponding value
		PCPL__checkNameCharset(zCtx, name) #MUST be a valid name
		tgtText = PCPL__getItemText(zCtx, name)
		zCtx.dbg("Targetting a PCPL item with name \"" + name + "\".", prtLine=True)

		#unknown item => cancel
		if tgtText is None:
			zCtx.dbg("Unable to find precompiler item with name \"" + name + "\" => FAILURE.")
			zCtx.pcpl.failures += 1
			return None

		#replace PCPL instruction
		zCtx.dbg("PCPL item found and replaced => SUCCESS", prtLine=True)
		return tgtText



	#CASE 2: ARITHMETIC EXPRESSION

	#parentheses includer directly => targetting an arithmetic expression
	if c == '(':
		zCtx.deepDbg("Looking for a PCPL arithmetic expression.")
		expression = PCPL__readIncluderBlock(zCtx, opening='(')

		#sub directive => unparseable yet => cancel
		if '#' in expression:
			zCtx.dbg("Got sub directive in PCPL arithmetic expression, unparseable yet => FAILURE.")
			zCtx.pcpl.failures += 1
			return None

		#solve expression
		tgtText = PCPL__ATH__solveArithmetic(zCtx, expression)

		#unknown item => FAILURE
		if tgtText is None:
			zCtx.dbg("Unable to find precompiler item with name \"" + name + "\" => FAILURE.")
			zCtx.pcpl.failures += 1
			return None

		#replace PCPL directive
		zCtx.dbg("PCPL arithmetic expression replaced => SUCCESS", prtLine=True)
		return tgtText



	#CASE 4: KEYWORD DIRECTIVE (trigrams)

	#store directive name
	directiveKw = c #str = chr

	#found a negation => read one more
	if c == '!':
		if zCtx__inc(zCtx):
			zCtx.pcpl.failures += 1
			return None
		directiveKw += zCtx__get(zCtx)

	#read 2nd chr of directive name
	if zCtx__inc(zCtx):
		zCtx.pcpl.failures += 1
		return None
	directiveKw += zCtx__get(zCtx)

	#3rd and last one
	if zCtx__inc(zCtx):
		zCtx.pcpl.failures += 1
		return None
	directiveKw += zCtx__get(zCtx) #got full directive keyword, now time to analyze it

	#CFG
	if directiveKw == "CFG":
		zCtx__inc(zCtx)
		return PCPL__processCFG(zCtx, False)

	#!CFG
	if directiveKw == "!CFG":
		zCtx__inc(zCtx)
		return PCPL__processCFG(zCtx, True)

	#SET
	if directiveKw == "SET":
		zCtx__inc(zCtx)
		return PCPL__processSET(zCtx)

	#!SET
	if directiveKw == "!SET":
		zCtx__inc(zCtx)
		return PCPL__processUnSET(zCtx)

	#FOR
	if directiveKw == "FOR":
		zCtx__inc(zCtx)
		return PCPL__processFOR(zCtx)

	#no directive matching => cancel without failure
	return None



#parse straightforward over cur context, trying to solve things out, as much as possible
def tryParseDirectives(zCtx):
	zCtx.pcpl.failures = 0 #reset failure nbr

	#read chr per chr
	output  = ""
	skipInc = False
	while True:

		#mechanism to allow skipping just one chr dynamically
		if skipInc:
			skipInc = False
		elif zCtx__inc(zCtx):
			break
		c = zCtx__get(zCtx)

		#potentially found PCPL instruction => SPECIFIC BEHAVIOR
		if c == '#':
			initialCtx = zCtx.ctx.copy()
			res        = getDirectiveText(zCtx)

			#FAILURE or not-a-directive => reset ctx
			if res is None:
				zCtx.dbg("Character '#' does not target a PCPL directive or resulted in FAILURE => canceling operation.", prtLine=True)
				zCtx__resetCtx(zCtx, initialCtx)

			#SUCCESS => add replacement text instead + skip next inc
			else:

				#resolution may include other directives in res => maintain same failure nbr in that case
				if '#' in res:
					zCtx.pcpl.failures += 1

				#go on
				output += res
				skipInc = True #skipping next inc because PCPL success makes zCtx move until next chr to parse => we don't want to miss it ! (especially if ti is another PCPL directive following)
				continue

		#regular code (unchanged)
		output += c

	#write out result in given context
	zCtx__reset(zCtx, newText=output)



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
	tryParseDirectives(zCtx) #includes zCtx.reset() at the end

	#deep debug
	if zCtx.deepDbgMode[zCtx.step]:
		prepareDbgDir()
		writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p2.1stTry.z", zCtx.ctx.icontent.s)

	#remaining directives to be solved
	retry = 0
	while zCtx.pcpl.failures != 0:

		#maximum retries reached
		if retry >= zCtx.pcpl.directivesMaxComplexity:
			zCtx.err("Unable to solve complexity of precompiler directives, can be cyclic dependencies or requiring more that the cur number of retries allowed:" + str(zCtx.pcpl.directivesMaxComplexity))

		#try again from the beginning (previous resolutions could have unlocked some other directives)
		zCtx.dbg("Retry parsing PCPL directives: " + str(retry))
		tryParseDirectives(zCtx)
		retry += 1

		#deep debug
		if zCtx.deepDbgMode[zCtx.step]:
			prepareDbgDir()
			writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p2.retry" + str(retry) + ".z", zCtx.ctx.icontent.s)

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
		writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p2.z", zCtx.ctx.icontent.s)
