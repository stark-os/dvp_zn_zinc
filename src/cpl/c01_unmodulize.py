#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






# -------- EXECUTION --------

#compilation
def c01_unmodulize(zCtx):

	#current module construction (can have module inside module inside module...)
	#currentModule = Stack()

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

			#read next word
			zCtx.jumpBlankZone(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")
			moduleName = zCtx.readName(ZCI, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")

			#addition to an already existing module
			if moduleName == "add":
				zCtx.jumpBlankZone(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				moduleName = zCtx.readName(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				if moduleName not in zCtx.cpl.modules:
					#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< print the list of the available modules ? debug mode only ?
					zCtx.error("No module " + moduleName + " declared yet, can't add to it.")

			#add module declaration
			zCtx.cpl.modules.append(moduleName)

			#looking for starting point of module content
			zCtx.jumpBlankZone(ZCI, "Module content between braces includer.")
			if ZCI.ctx.get() != '{':
				zCtx.error("Expected module content between braces includer.")

			#get module content boundaries
			moduleContent_startIndex = ZCI.ctx.icontent.index
			if moduleContent_startIndex not in ZCI.pairs.keys():
				zCtx.internal("Missing pair information for current includer.")
			moduleContent_stopIndex  = ZCI.pairs[moduleContent_startIndex]

			#shift 1st character '{'
			moduleContent_startIndex += 1
			ZCI.ctx.inc()

			#extract ZCIs from content
			moduleContent            = ZCI.ctx.copy()
			moduleContent.icontent.s = str_sub(ZCI.ctx.icontent.s, moduleContent_startIndex, moduleContent_stopIndex-1)
			moduleZCIs               = extractZCIsFromCtx(zCtx, moduleContent, True, module=moduleName)

			#remove current ZCI in general ZCtx
			lst_remove(zCtx.ZCIs, z)
			z -= 1

			#complete general ZCI list
			previousZCIs = lst_sub(zCtx.ZCIs, stop=z)
			nextZCIs     = lst_sub(zCtx.ZCIs, start=z+1)
			zCtx.ZCIs    = previousZCIs + moduleZCIs + nextZCIs
			_ZCIsLen = len(zCtx.ZCIs) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python, not required in Z (.length field)

		#next ZCI
		z += 1
