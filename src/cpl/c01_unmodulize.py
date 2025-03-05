#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






# -------- EXECUTION --------

#compilation
def c01_unmodulize(zCtx):
	PZCIs = zCtx.pcpl.ZCIs

	#current module construction (can have module inside module inside module...)
	currentModule = Stack()

	#for each precompiled ZCI
	declaredModules = [] #lst[str]
	for z in range(len(zCtx.pcpl.ZCIs)):
		PZCI     = PZCIs[z]
		PZCIText = PZCI.ctx.icontent.s

		#too short => skip it
		if len(PZCIText) < 5:
			continue

		#found module declaration (DCL_MOD)
		if PZCIText.startswith("mod") and PZCIText[3] in BLANKS:
			PZCI.ctx.forward(4)

			#read next word
			zCtx.jumpBlankZone(PZCI.ctx, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")
			moduleName = zCtx.readName(PZCI.ctx, "\"add\" keyword or module name in module declaration ZCI (DCL_MOD).")

			#addition to an already existing module
			if moduleName == "add":
				zCtx.jumpBlankZone(PZCI.ctx, "Module name in addition to module declaration ZCI (DCL_MOD).")
				moduleName = zCtx.readName(PZCI.ctx, "Module name in addition to module declaration ZCI (DCL_MOD).")
				if moduleName not in declaredModules:
					zCtx.error("No module " + moduleName + " declared yet, can't add to it.")

			#update current module
			#if moduleName in currentModule.data:
			#	zCtx.error("Already in module " + moduleName + ", either directly or by submodule (^" + ".^".join(currentModule) + ").")
			#currentModule.push(moduleName)

			#add module declaration
			declaredModules.append(moduleName)
			
