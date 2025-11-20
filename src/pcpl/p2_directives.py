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
	zCtx.dbg0("Processing PCPL directive \"SET\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "SET")
	initCtx = zCtx.ctx.copy()

	#read name given
	name = PCPL__readUntil(zCtx, BLANKS)
	if '#' in name:
		zCtx.dbg1("Found PCPL sub directive in SET item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures.append(PCPL_failure(
			initCtx, "Found precompiler sub directive in SET item name, unparseable yet."
		))
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
		zCtx.dbg1("Precompiler item \"" + name + "\" has unreadable value yet.")
		zCtx.pcpl.failures.append(PCPL_failure(
			initCtx, "Precompiler item \"" + name + "\" has unreadable value yet."
		))
		return None

	#else, add pcpl item (success)
	zCtx.dbg0("Adding PCPL item \"" + name + "\" with value \"" + valueText + "\".")
	zCtx.pcpl.inCodeItms[name] = valueText

	#success
	zCtx.dbg0("Processed PCPL directive \"SET\" => SUCCESS")
	return ""



#!SET
def PCPL__processUnSET(zCtx):
	zCtx.dbg0("Processing PCPL directive \"!SET\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "!SET")
	initCtx = zCtx.ctx.copy()

	#read name given
	name = PCPL__readUntil(zCtx, BLANKS_EXTENDED) #1st and only field => must allow line feeds
	if '#' in name:
		zCtx.dbg1("Found PCPL sub directive in !SET item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures.append(PCPL_failure(
			initCtx, "Found precompiler sub directive in !SET item name, unparseable yet."
		))
		return None

	#check name charset
	PCPL__checkNameCharset(zCtx, name)

	#must not affect items from cfg file
	if name in zCtx.pcpl.inCfgItms.keys():
		zCtx.err("Trying to modify precompiler item that has been defined in local cfg/pcpl_itms.cfg => FORBIDDEN.")

	#not even in the previously declared ones
	if name not in zCtx.pcpl.inCodeItms.keys():
		zCtx.dbg0("No precompiler item with name \"" + name + "\" allowing to be unset => FAILURE.")
		zCtx.pcpl.failures += 1
		return None

	#else, remove item
	zCtx.dbg0("Removing PCPL item \"" + name + "\".")
	zCtx.pcpl.inCodeItms.pop(name)

	#success
	zCtx.dbg0("Processed PCPL directive \"!SET\" => SUCCESS")
	return ""



#CFG & !CFG (can't return null btw)
def PCPL__processCFG(zCtx, negation):
	zCtx.dbg0("Processing PCPL directive \"(!)CFG\".", prtLine=True)
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
		zCtx.dbg1("Processed PCPL directive \"CFG\" => SUCCESS")
		return block

	#cfg inactive => skip it (respecting line nbr by giving the same amount of line feeds)
	zCtx.dbg0("Processed PCPL directive \"!CFG\" => SUCCESS")
	return '\n' * block.count('\n')



#FOR
def PCPL__processFOR(zCtx):
	zCtx.dbg0("Processing PCPL directive \"FOR\".", prtLine=True)
	PCPL__jumpBlankZone(zCtx, "FOR")
	initCtx = zCtx.ctx.copy()

	#read iter var name given
	iterVarName = PCPL__readUntil(zCtx, BLANKS)
	if '#' in iterVarName:
		zCtx.dbg1("Found PCPL sub directive in FOR item name, unparseable yet => FAILURE")
		zCtx.pcpl.failures.append(PCPL_failure(
			initCtx, "Found precompiler sub directive in FOR item name, unparseable yet."
		))
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
			zCtx.dbg0("Found a sub-directive in FOR range values => stop here, it must be solved first.")
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
	zCtx.dbg0("Processed PCPL directive \"FOR\" => SUCCESS")
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
		zCtx.dbg0("Got 2 '#' in a row, maybe it is a directive inside another.")
		return None



	#CASE 1: ITEM NAME

	#braces includer directly => targetting a PCPL item
	if c == '{':
		zCtx.dbg1("Looking for a PCPL item name.")
		initCtx = zCtx.ctx.copy()
		name    = PCPL__readIncluderBlock(zCtx)

		#sub directive => unparseable yet => cancel
		if '#' in name:
			zCtx.dbg0("Got sub directive in PCPL name, unparseable yet => FAILURE.")
			zCtx.pcpl.failures.append(PCPL_failure(
				initCtx, "Got sub directive in precompiler name, unparseable yet."
			))
			return None

		#get corresponding value
		PCPL__checkNameCharset(zCtx, name) #MUST be a valid name
		tgtText = PCPL__getItemText(zCtx, name)
		zCtx.dbg0("Targetting a PCPL item with name \"" + name + "\".", prtLine=True)

		#unknown item => cancel
		if tgtText is None:
			zCtx.dbg0("Unable to find precompiler item with name \"" + name + "\" => FAILURE.")
			zCtx.pcpl.failures.append(PCPL_failure(
				initCtx, "Unable to find precompiler item with name \"" + name + "\"."
			))
			return None

		#replace PCPL instruction
		zCtx.dbg0("PCPL item found and replaced => SUCCESS")
		return tgtText



	#CASE 2: ARITHMETIC EXPRESSION

	#parentheses includer directly => targetting an arithmetic expression
	if c == '(':
		initCtx = zCtx.ctx.copy()
		zCtx.dbg1("Looking for a PCPL arithmetic expression.")
		expression = PCPL__readIncluderBlock(zCtx, opening='(')

		#sub directive => unparseable yet => cancel
		if '#' in expression:
			zCtx.dbg0("Got sub directive in PCPL arithmetic expression, unparseable yet => FAILURE.")
			zCtx.pcpl.failures.append(PCPL_failure(
				initCtx, "Got sub directive in precompiler arithmetic expression, unparseable yet."
			))
			return None

		#solve expression
		tgtText = PCPL__ATH__solveArithmetic(zCtx, expression)

		#unsolvable => FAILURE
		if tgtText is None:
			zCtx.dbg0("Unable to solve PCPL expression \"" + expression + "\" => FAILURE.")
			zCtx.pcpl.failures.append(PCPL_failure(
				initCtx, "Unable to solve precompiler arithmetic expression \"" + expression + "\"."
			))
			return None

		#replace PCPL directive
		zCtx.dbg0("PCPL arithmetic expression replaced => SUCCESS")
		return tgtText



	#CASE 4: KEYWORD DIRECTIVE (trigrams)

	#store directive name
	directiveKw = c #str = chr

	#found a negation => read one more
	if c == '!':
		if zCtx__inc(zCtx):
			return None
		directiveKw += zCtx__get(zCtx)

	#read 2nd chr of directive name
	if zCtx__inc(zCtx):
		return None
	directiveKw += zCtx__get(zCtx)

	#3rd and last one
	if zCtx__inc(zCtx):
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
	zCtx.pcpl.gotChanges = False
	retry                = 0



	#PARSING WHOLE FILE

	#as long as we find it necessary to parse the file
	while True:
		zCtx.pcpl.failures = [] #lst[PCPL_failure]

		#read chr per chr
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
				initCtx       = zCtx.ctx.copy()
				res           = getDirectiveText(zCtx)
				idxAfterBlock = zCtx.ctx.icontent.idx

				#reset ctx before directive in all cases (fail => ignore, success => parse new block)
				zCtx__resetCtx(zCtx, initCtx)

				#FAILURE or not-a-directive => do nothing
				if res is None:
					zCtx.dbg0("Character '#' does not target a PCPL directive or resulted in FAILURE => ignoring for the moment.", prtLine=True)

				#SUCCESS => add replacement text in ctx + skip next inc
				else:
					skipInc = True #skipping next inc because PCPL success makes zCtx move until next chr to parse => we don't want to miss it ! (especially if it is another PCPL directive following)

					#remove directive txt
					zCtx.ctx.icontent.s = str_truncate(zCtx.ctx.icontent.s, zCtx.ctx.icontent.idx, idxAfterBlock-1)

					#add replacement txt instead
					zCtx.ctx.insert(res)
					zCtx.dbg0("Replacement done, ready to parse block and further.", prtLine=True)

					#a block has been added => got changes then ! (potentially sub-directives inside)
					zCtx.pcpl.gotChanges = True
					zCtx.dbg0("Added block to output => CHANGES")
					continue



		#CONCLUSION

		#reset parsing head
		zCtx__reset(zCtx)

		#deep debug
		if log_lvl[0] >= LOG__LVL_DBG0:
			prepareDbgDir()
			writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p2.retry" + str(retry) + ".z", zCtx.ctx.icontent.s)

		#go again
		if zCtx.pcpl.gotChanges:
			zCtx.pcpl.gotChanges = False
			zCtx.dbg1("END OF PARSING, GOT CHANGES => Reseting cur ctx to the beginning, let's go parsing new content.", prtSubCtxs=False, prtLine=False)
			zCtx.dbgPause()

		#no need to go deeper
		else:
			zCtx.dbg1("END OF PARSING, NO CHANGES => stopping here.", prtSubCtxs=False, prtLine=False)
			break

		#too much retry => also stop
		retry += 1
		if retry >= zCtx.pcpl.directivesMaxComplexity:
			zCtx.pcpl.failures.append(PCPL_failure(
				zCtx.ctx, "Unable to solve complexity of precompiler directives, can be cyclic dependencies or requiring more that the cur number of retries allowed:" + str(zCtx.pcpl.directivesMaxComplexity)
			))
			break



#apply precompiler configurations (environment-related modifications in code)
def p2_directives(zCtx):
	zCtx.updateLogLvl(STEP.P2)
	zCtx.dbgSepLine()
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("========================= P2 DIRECTIVES : beginning ========================")
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgPause()

	#try parsing as long as we can/need
	tryParseDirectives(zCtx)

	#still having failures
	if len(zCtx.pcpl.failures) != 0:
		for f in zCtx.pcpl.failures:
			zCtx__resetCtx(zCtx, f.ctx)
			zCtx.err(f.msg, err=0)
		exit(1)

	#debug
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("============================ P2 DIRECTIVES : end ===========================")
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()
		writeFile("dbg/" + path_name(zCtx.ctx.filename) + ".p2.z", zCtx.ctx.icontent.s)
