#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_ZCSAndImp import *






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
			ZCIErr(ZCI, "Character not allowed in module name.")
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
	zCtx.updateLogLvl(STEP.C01)
	zCtx.dbgSepLine()
	zCtx.dbg0("============================================================================")
	zCtx.dbg0("======================== C01 UNMODULIZE : beginning ========================")
	zCtx.dbg0("============================================================================")
	zCtx.dbgPause()

	#for each precompiled ZCI
	z = 0
	_ZCIsLen = len(zCtx.ZCIs) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only exists here in python, won't be useful in Z (we got .length)
	while z < _ZCIsLen:
		ZCI = zCtx.ZCIs[z]
		ZCIDbg1(ZCI, "Treating global ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=True)

		#too short => skip it
		if len(ZCI.txt) < 5:
			zCtx.dbg1("Too short => Skipping ZCI.")
			z += 1
			continue

		#found module declaration (DCL_MOD)
		if ZCI.txt.startswith("mod") and ZCI.txt[3] in BLANKS:
			ZCIDbg0(ZCI, "Found module declaration.")
			ZCI.forward(3)



			# I] MODULE NAME

			#look for module addition symbol
			jumpBlankZone(ZCI, "module name in module declaration ZCI (DCL_MOD).")
			modAdd = (ZCI.get() == '+')
			if modAdd:
				ZCI.inc()

			#read module name
			modName = readName(ZCI, "\'+\' keyword or module name in module declaration ZCI (DCL_MOD).")[1]

			#combine with cur module (we can be in another module => this allows submodularization)
			modPfx = ZCI.modPfx + formatModName(ZCI, modName)

			#special case: "Atm" forbidden
			if modPfx == "MAtm_":
				ZCIErr(ZCI, "Can't declare a global module \"Atm\", forbidden.")

			# I.1) module addition
			if modAdd:
				zCtx.dbg("Detected addition to existing module \"" + unpfxMod(modPfx) + "\".")

				#adding to inexisting module
				if modPfx not in zCtx.cpl.modPfxes:
					zCtx__dbgMods(zCtx)
					ZCIErr(ZCI, "No module " + unpfxMod(modPfx) + " declared yet, can't add to it.")

			# I.2) new module
			else:
				zCtx.dbg0("Detected new module creation \"" + unpfxMod(modPfx) + "\".")

				#already declared the same exact module
				if modPfx in zCtx.cpl.modPfxes:
					zCtx__dbgMods(zCtx)
					ZCIErr(ZCI, "Module " + unpfxMod(modPfx) + " already declared, you may consider \"adding\" to it.")

				#avoid re-declaration
				zCtx.cpl.modPfxes.append(modPfx)
				zCtx.dbg0("Added module \"" + modPfx + "\" to compiler context.")
			ZCIDbg0(ZCI, "Full module name read \"" + modPfx + "\" (based on prefix \"" + ZCI.modPfx + "\").")



			# II] MODULE CONTENT

			#looking for starting point of module content
			optionalBlanks(ZCI, "Module content after name (braces includer).")
			if ZCI.get() != '{':
				ZCIErr(ZCI, "Expected module content after name (braces includer).")

			#get module content boundaries
			modContent_startIdx = ZCI.ctx.icontent.idx
			if modContent_startIdx not in ZCI.pairs.keys():
				ZCIInt(ZCI, "Missing pair information for cur includer.")
			modContent_stopIdx = ZCI.pairs[modContent_startIdx]

			#shift 1st character '{'
			ZCI.inc()

			#extract ZCIs from content
			zCtx.dbg0("Extracting ZCIs from module content.")
			modZCIs = extractZCIsFromCtx(
				zCtx,
				ZCI.ctx, subCtxs=ZCI.subCtxs,
				gbl     = True,
				modPfx  = modPfx,
				wallIdx = modContent_stopIdx
			)

			#remove cur ZCI in general ZCtx
			zCtx.dbg0("Replacing module declaration ZCI by global unmodularized ZCIs.")
			zCtx.ZCIs = lst_remove(zCtx.ZCIs, z)

			#complete general ZCI list
			if z == 0:
				previousZCIs = []
			else:
				previousZCIs = lst_sub(zCtx.ZCIs, stop=z-1)
			nextZCIs  = lst_sub(zCtx.ZCIs, start=z)
			zCtx.ZCIs = previousZCIs + modZCIs + nextZCIs

			#shift cur ZCI index because we removed it
			z -= 1
			zCtx.dbg1("Module declaration processed.")
			zCtx.dbgPause()

			_ZCIsLen = len(zCtx.ZCIs) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python, not required in Z (.length field)

		#next ZCI
		z += 1

	#debug
	zCtx.dbg0("======================================================================")
	zCtx.dbg0("======================== C01 UNMODULIZE : end ========================")
	zCtx.dbg0("======================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()
		dumpZCIs(zCtx.ZCIs, "dbg/" + path_name(zCtx.initialCtx.filename) + ".c01.dl", oneLine=False)
