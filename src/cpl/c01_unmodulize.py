#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.p3_splitZCIsAndImport import *






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

			#addition to an already existing module
			if moduleName == "add":
				zCtx.jumpBlankZone(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				moduleName = zCtx.readName(ZCI, "Module name in addition to module declaration ZCI (DCL_MOD).")
				if moduleName not in zCtx.cpl.modules:
					#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< print the list of the available modules ? debug mode only ?
					zCtx.subCtxs = ZCI.subCtxs
					zCtx.error("No module " + moduleName + " declared yet, can't add to it.")

			#already in a submodule <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
			#if moduleName in ZCI.modules:
			#	zCtx.subCtxs = ZCI.subCtxs
			#	zCtx.error("Already inside module " + moduleName + ", could not declare it inside itself.")

			#add module declaration
			zCtx.cpl.modules.append(moduleName)

			#looking for starting point of module content
			zCtx.jumpBlankZone(ZCI, "Module content between braces includer.")
			if ZCI.ctx.get() != '{':
				zCtx.subCtxs = ZCI.subCtxs
				zCtx.error("Expected module content between braces includer.")

			#get module content boundaries
			moduleContent_startIndex = ZCI.ctx.icontent.index
			if moduleContent_startIndex not in ZCI.pairs.keys():
				zCtx.subCtxs = ZCI.subCtxs
				zCtx.internal("Missing pair information for current includer.")
			moduleContent_stopIndex  = ZCI.pairs[moduleContent_startIndex]
			print("start/stop Index ["+str(moduleContent_startIndex)+"]["+str(moduleContent_stopIndex)+"]")
			print("MODULE 1ST BRACE ["+ZCI.ctx.toStr()+"]["+ZCI.ctx.icontent.s[moduleContent_startIndex:]+"]")
			print("MODULE LAST BRACE ["+ZCI.ctx.toStr()+"]["+ZCI.ctx.icontent.s[moduleContent_stopIndex:]+"]")

			#shift 1st character '{'
			moduleContent_startIndex += 1
			ZCI.ctx.inc()

			#extract ZCIs from content
			moduleContent                = ZCI.ctx.copy()
			moduleContent.icontent.s     = str_sub(ZCI.ctx.icontent.s, moduleContent_startIndex, moduleContent_stopIndex-1)
			moduleContent.icontent.index = -1
			moduleContent.columnNbr     -=  1 #shift to compensate the -1 set as index
			moduleZCIs                   = extractZCIsFromCtx(zCtx, moduleContent, global_=True, subCtxs=ZCI.subCtxs, module=moduleName)
			print("CONTENT READy FOR EXTRACTION["+moduleContent.toStr()+"]["+moduleContent.icontent.s+"]")

			#remove current ZCI in general ZCtx
			print("\n\n\n\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ALPHA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
			debugOutput = "[\n"
			for ZCI in zCtx.ZCIs:
				content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
				debugOutput += "{module:\"" + ZCI.module + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content[:30] + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
			debugOutput += "]"
			print(debugOutput)
			zCtx.ZCIs = lst_remove(zCtx.ZCIs, z)
			z -= 1
			print("\n\n\n\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< BETA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
			debugOutput = "[\n"
			for ZCI in zCtx.ZCIs:
				content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
				debugOutput += "{module:\"" + ZCI.module + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content[:30] + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
			debugOutput += "]"
			print(debugOutput)

			#complete general ZCI list
			previousZCIs = lst_sub(zCtx.ZCIs, stop=z)
			nextZCIs     = lst_sub(zCtx.ZCIs, start=z+1)
			zCtx.ZCIs    = previousZCIs + moduleZCIs + nextZCIs
			print("\n\n\n\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< GAMMA <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
			debugOutput = "[\n"
			for ZCI in zCtx.ZCIs:
				content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
				debugOutput += "{module:\"" + ZCI.module + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content[:30] + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
			debugOutput += "]"
			print(debugOutput)

			_ZCIsLen = len(zCtx.ZCIs) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python, not required in Z (.length field)

		#next ZCI
		z += 1
