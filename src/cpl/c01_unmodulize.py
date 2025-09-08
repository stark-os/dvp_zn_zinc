#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#check & turn raw Module name into prefix
# HERE, we consider our ZCI to be at position right after reading the given moduleName
def formatModuleName(zCtx, ZCI, moduleName):

	#charset check
	checkedModuleName = ""
	backShift         = len(moduleName)
	for c in moduleName:
		if c not in DEFAULT_NAME_CHARSET: #this "backshift" strategy for targetting something that has ALREADY been read only works because no tab or line feed is allowed in our charset.
			ZCI.ctx.icontent.index -= backShift #target exact position of invalid character
			ZCI.ctx.colmNbr        -= backShift
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
	zCtx.debug("\n\n\n\n")
	zCtx.debug("============================================================================")
	zCtx.debug("======================== C01 UNMODULIZE : beginning ========================")
	zCtx.debug("============================================================================\n\n\n\n")
	zCtx.deepDebugPause()

	#for each precompiled ZCI
	z = 0
	_ZCIsLen = len(zCtx.ZCIs) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only exists here in python, won't be useful in Z (we got .length)
	while z < _ZCIsLen:
		ZCI = zCtx.ZCIs[z]
		zCtx.ZCIDeepDebug(ZCI, "Treating ZCI " + ZCI.textFormat(), printSubCtxs=True)

		#too short => skip it
		if len(ZCI.text) < 5:
			zCtx.deepDebug("Too short => Skipping ZCI.")
			z += 1
			continue

		#found module declaration (DCL_MOD)
		if ZCI.text.startswith("mod") and ZCI.text[3] in BLANKS:
			zCtx.ZCIDebug(ZCI, "Found module declaration.")
			ZCI.forward(3)



			# I] MODULE NAME

			#read next word
			zCtx.jumpBlankZone(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")
			moduleName = zCtx.readName(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")

			#combine with current module (we can be in another module => this allows submodularization)
			modulePrefix = ZCI.modulePrefix + formatModuleName(zCtx, ZCI, moduleName)

			# I.1) module addition
			if moduleName == "add":
				zCtx.debug("Detected addition to existing module.")

				#read one more name
				zCtx.jumpBlankZone(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				modulePrefix = ZCI.modulePrefix + formatModuleName(
					zCtx, ZCI,
					zCtx.readName(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				)

				#adding to inexisting module
				if modulePrefix not in zCtx.cpl.modulePrefixes:
					zCtx.debugModules()
					zCtx.ZCIError(ZCI, "No module " + unprefixizeModule(modulePrefix) + " declared yet, can't add to it.")

			# I.2) new module
			else:
				zCtx.debug("Detected new module creation \"" + modulePrefix + "\".")

				#already declared the same exact module
				if modulePrefix in zCtx.cpl.modulePrefixes:
					zCtx.debugModules()
					zCtx.ZCIError(ZCI, "Module " + unprefixizeModule(modulePrefix) + " already declared, you may consider \"adding\" to it.")

				#avoid re-declaration
				zCtx.cpl.modulePrefixes.append(modulePrefix)
				zCtx.debug("Added module \"" + modulePrefix + "\" to compiler context.")
			zCtx.ZCIDebug(ZCI, "Full module name read \"" + modulePrefix + "\" (based on prefix \"" + ZCI.modulePrefix + "\").")



			# II] MODULE CONTENT

			#looking for starting point of module content
			zCtx.optionnalBlanks(ZCI, "Module content after name (braces includer).")
			if ZCI.get() != '{':
				zCtx.ZCIError(ZCI, "Expected module content after name (braces includer).")

			#get module content boundaries
			moduleContent_startIndex = ZCI.ctx.icontent.index
			if moduleContent_startIndex not in ZCI.pairs.keys():
				zCtx.ZCIInternal(ZCI, "Missing pair information for current includer.")
			moduleContent_stopIndex = ZCI.pairs[moduleContent_startIndex]

			#shift 1st character '{'
			ZCI.inc()

			#extract ZCIs from content
			zCtx.debug("Extracting ZCIs from module content.")
			moduleZCIs = extractZCIsFromCtx(zCtx,
				ZCI.ctx,
				subCtxs = ZCI.subCtxs,
				global_ = True,
				modulePrefix = modulePrefix,
				maximumIndexAllowed = moduleContent_stopIndex-1 #actually, we must skip the real moduleContent_stopIndex, it refers to the ending includer of module content (=> not interesting).
			)

			#remove current ZCI in general ZCtx
			zCtx.debug("Replacing module declaration ZCI by global unmodularized ZCIs.")
			zCtx.ZCIs = lst_remove(zCtx.ZCIs, z)

			#complete general ZCI list
			if z == 0:
				previousZCIs = []
			else:
				previousZCIs = lst_sub(zCtx.ZCIs, stop=z-1)
			nextZCIs  = lst_sub(zCtx.ZCIs, start=z)
			zCtx.ZCIs = previousZCIs + moduleZCIs + nextZCIs

			#shift current ZCI index because we removed it
			z -= 1

			_ZCIsLen = len(zCtx.ZCIs) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python, not required in Z (.length field)

		#next ZCI
		z += 1

	#debug
	zCtx.debug("\n\n\n\n")
	zCtx.debug("======================================================================")
	zCtx.debug("======================== C01 UNMODULIZE : end ========================")
	zCtx.debug("======================================================================\n\n\n\n")
	zCtx.deepDebugPause()

	#debug output file
	zCtx.cplStep_debugZCIs("01")
