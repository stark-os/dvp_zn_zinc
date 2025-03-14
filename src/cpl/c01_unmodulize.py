#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#check & turn raw Module name into prefix
def formatModuleName(zCtx, ZCI, moduleName):

	#charset check
	checkedModuleName = ""
	backShift         = len(moduleName)
	for c in moduleName:
		if c not in VAR_NAME_CHARSET:
			ZCI.ctx.icontent.index -= backShift #target exact position of invalid character
			ZCI.ctx.columnNbr      -= backShift
			zCtx.ZCIError(ZCI, "Character not allowed in module name.")
		checkedModuleName += c

		#doubling underscores
		if c == '_':
			checkedModuleName += '_'
		backShift -= 1

	#final module prefix
	return "M" + checkedModuleName + "_"






# -------- EXECUTION --------

#compilation
def c01_unmodulize(zCtx):

	#for each precompiled ZCI
	z = 0
	_ZCIsLen = len(zCtx.ZCIs) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only exists here in python, won't be useful in Z (we got .length)
	while z < _ZCIsLen:
		ZCI     = zCtx.ZCIs[z]
		ZCIText = ZCI.ctx.icontent.s

		#too short => skip it
		if len(ZCIText) < 5:
			continue

		#found module declaration (DCL_MOD)
		if ZCIText.startswith("mod") and ZCIText[3] in BLANKS:
			ZCI.ctx.forward(4)

			#ZCI ctx will start from index -1 (istr initial position) but its columnNbr IS CORRECT => ctx.inc() will correspond to correct location => shift columnNbr to compensate
			ZCI.ctx.columnNbr -= 1

			#read next word
			zCtx.jumpBlankZone(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")
			moduleName = zCtx.readName(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")

			#combine with current module (we can be in another module => this allow submodularization)
			modulePrefix = ZCI.modulePrefix + formatModuleName(zCtx, ZCI, moduleName)

			#CASE 1 - ADD TO MODULE
			if moduleName == "add":

				#read one more name
				zCtx.jumpBlankZone(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				modulePrefix = ZCI.modulePrefix + formatModuleName(
					zCtx, ZCI,
					zCtx.readName(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				)

				#adding to inexistent module
				if modulePrefix not in zCtx.cpl.modulePrefixes:
					zCtx.debugModules()
					zCtx.ZCIError(ZCI, "No module " + unprefixizeModule(modulePrefix) + " declared yet, can't add to it.")

			#CASE 2 - NEW MODULE
			else:

				#already declared the same exact module
				if modulePrefix in zCtx.cpl.modulePrefixes:
					zCtx.debugModules()
					zCtx.ZCIError(ZCI, "Module " + unprefixizeModule(modulePrefix) + " already declared, you may consider \"adding\" to it.")

				#avoid re-declaration
				zCtx.cpl.modulePrefixes.append(modulePrefix)

			#looking for starting point of module content #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 1st IF CONCERNS OPTIONAL BLANK, CAN BE USEFUL !
			if ZCI.ctx.get() in BLANKS:
				zCtx.jumpBlankZone(ZCI, "Module content after name (braces includer).")
			if ZCI.ctx.get() != '{':
				zCtx.ZCIError(ZCI, "Expected module content after name (braces includer).")

			#get module content boundaries
			moduleContent_startIndex = ZCI.ctx.icontent.index
			if moduleContent_startIndex not in ZCI.pairs.keys():
				zCtx.ZCIInternal(ZCI, "Missing pair information for current includer.")
			moduleContent_stopIndex  = ZCI.pairs[moduleContent_startIndex]

			#shift 1st character '{'
			moduleContent_startIndex += 1
			ZCI.ctx.inc()

			#extract ZCIs from content
			moduleContent                = ZCI.ctx.copy()
			moduleContent.icontent.s     = str_sub(ZCI.ctx.icontent.s, moduleContent_startIndex, moduleContent_stopIndex-1)
			moduleContent.icontent.index = -1
			moduleContent.columnNbr     -=  1 #shift to compensate the -1 set as index
			moduleZCIs                   = extractZCIsFromCtx(zCtx, moduleContent, global_=True, subCtxs=ZCI.subCtxs, modulePrefix=modulePrefix)

			#remove current ZCI in general ZCtx
			zCtx.ZCIs = lst_remove(zCtx.ZCIs, z)
			z -= 1

			#complete general ZCI list
			previousZCIs = lst_sub(zCtx.ZCIs, stop=z)
			nextZCIs     = lst_sub(zCtx.ZCIs, start=z+1)
			zCtx.ZCIs    = previousZCIs + moduleZCIs + nextZCIs

			#for deep debugging, just in case
			#debugOutput = "[\n"
			#for ZCI in zCtx.ZCIs:
			#	content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
			#	debugOutput += "{module:\"" + ZCI.modulePrefix + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
			#debugOutput += "]"
			#print(debugOutput)

			_ZCIsLen = len(zCtx.ZCIs) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python, not required in Z (.length field)

		#next ZCI
		z += 1
