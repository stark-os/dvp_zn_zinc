#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#check & turn raw Module name into prefix
# HERE, we consider our ZCI to be at position right after reading the given moduleName
def formatModName(ZCI, modName):

	#charset check
	checkedModName = ""
	backShift      = len(modName)
	for c in modName:
		if c not in DEFAULT_NAME_CHARSET: #this "backshift" strategy for targetting something that has ALREADY been read only works because no tab or line feed is allowed in our charset.
			ZCI.ctx.icontent.idx -= backShift #target exact position of invalid character
			ZCI.ctx.colmNbr      -= backShift
			ZCIError(ZCI, "Character not allowed in module name.")
		checkedModName += c

		#doubling underscores
		if c == '_':
			checkedModName += '_'
		backShift -= 1

	#final module prefix
	return "M" + checkedModName + "_"






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
		ZCIDeepDebug(ZCI, "Treating ZCI \"" + ZCI.textFormat() + '\"', printSubCtxs=True)

		#too short => skip it
		if len(ZCI.txt) < 5:
			zCtx.deepDebug("Too short => Skipping ZCI.")
			z += 1
			continue

		#found module declaration (DCL_MOD)
		if ZCI.txt.startswith("mod") and ZCI.txt[3] in BLANKS:
			ZCIDebug(ZCI, "Found module declaration.")
			ZCI.forward(3)



			# I] MODULE NAME

			#read next word
			jumpBlankZone(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")
			modName = readName(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")

			#combine with current module (we can be in another module => this allows submodularization)
			modPrefix = ZCI.modPrefix + formatModName(ZCI, modName)

			# I.1) module addition
			if modName == "add":
				zCtx.debug("Detected addition to existing module.")

				#read one more name
				jumpBlankZone(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				modPrefix = ZCI.modPrefix + formatModName(ZCI, readName(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD)."))

				#adding to inexisting module
				if modPrefix not in zCtx.cpl.modPrefixes:
					zCtx__debugMods(zCtx)
					ZCIError(ZCI, "No module " + unprefixizeMod(modPrefix) + " declared yet, can't add to it.")

			# I.2) new module
			else:
				zCtx.debug("Detected new module creation \"" + modPrefix + "\".")

				#already declared the same exact module
				if modPrefix in zCtx.cpl.modPrefixes:
					zCtx__debugMods(zCtx)
					ZCIError(ZCI, "Module " + unprefixizeMod(modPrefix) + " already declared, you may consider \"adding\" to it.")

				#avoid re-declaration
				zCtx.cpl.modPrefixes.append(modPrefix)
				zCtx.debug("Added module \"" + modPrefix + "\" to compiler context.")
			ZCIDebug(ZCI, "Full module name read \"" + modPrefix + "\" (based on prefix \"" + ZCI.modPrefix + "\").")



			# II] MODULE CONTENT

			#looking for starting point of module content
			optionalBlanks(ZCI, "Module content after name (braces includer).")
			if ZCI.get() != '{':
				ZCIError(ZCI, "Expected module content after name (braces includer).")

			#get module content boundaries
			modContent_startIdx = ZCI.ctx.icontent.idx
			if modContent_startIdx not in ZCI.pairs.keys():
				ZCIInternal(ZCI, "Missing pair information for current includer.")
			modContent_stopIdx = ZCI.pairs[modContent_startIdx]

			#shift 1st character '{'
			ZCI.inc()

			#extract ZCIs from content
			zCtx.debug("Extracting ZCIs from module content.")
			modZCIs = extractZCIsFromCtx(
				zCtx,
				ZCI.ctx, subCtxs=ZCI.subCtxs,
				gbl           = True,
				modPrefix     = modPrefix,
				maxIdxAllowed = modContent_stopIdx-1 #actually, we must skip the real modContent_stopIdx, it refers to the ending includer of module content (=> not interesting).
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
			zCtx.ZCIs = previousZCIs + modZCIs + nextZCIs

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
	zCtx__cplStep_debugZCIs(zCtx, "01")
