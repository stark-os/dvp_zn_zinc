# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/zctx.py

# -------- Z CONTEXT --------

#z code context
def newZCtx(
	filepath, LLIInvFilepath,
	pcpl_cfg, pcpl_itm,
	cpl_opt,  dbgMode=False, deepDbgMode=False
):
	res                = zctx()
	res.LLIInvFilepath = LLIInvFilepath
	res.debugMode      = dbgMode
	res.deepDebugMode  = deepDbgMode

	#every imported context & the current one
	res.initialCtx   = ParsingCtx(filepath, readFile(filepath))
	res.ctx          = res.initialCtx
	res.imported     = [] #history of every filename imported
	res.subCtxs      = [] #subcontexts currently in use
	res.subCtxs.append(res.initialCtx)

	#check CPL options
	res.checkCplOpt(cpl_opt)

	#data
	res.ZCIs = None
	res.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	res.cpl  = newCplDat(cpl_opt)

	#"typ" keyword: virtual type that seems to work like a regular one for the moment
	res.typKeyword = res.cpl.newTyp("GUtyp")

	#"fly" virtual type that also seems to work like a regular one for the moment
	res.flyType    = res.cpl.newTyp("GUfly")

	#create a list to hold root types. This is purely a simplification tool in zCtx.
	res.rootTypes = [0,0,0, 0,0,0, 0,0,0, 0,0,0] #can be already declared as a fixed-size table (length: 12)

	#boolean
	res.rootTypes[RT__BOO] = res.cpl.newTyp("GUboo", size=res.SIZE__U1)

	#1 byte
	res.rootTypes[RT__S1] = res.cpl.newTyp("GUs1", size=res.SIZE__U1)
	res.rootTypes[RT__U1] = res.cpl.newTyp("GUu1", size=res.SIZE__U1)

	#2 bytes
	res.rootTypes[RT__S2] = res.cpl.newTyp("GUs2", size=res.SIZE__U2)
	res.rootTypes[RT__U2] = res.cpl.newTyp("GUu2", size=res.SIZE__U2)

	#4 bytes
	res.rootTypes[RT__S4] = res.cpl.newTyp("GUs4", size=res.SIZE__U4)
	res.rootTypes[RT__U4] = res.cpl.newTyp("GUu4", size=res.SIZE__U4)

	#4 bytes floating point
	res.rootTypes[RT__F4] = res.cpl.newTyp("GUf4", size=res.SIZE__U4)

	#8 bytes
	if cpl_opt["ARCH"] == "64":
		res.ptrSize = res.SIZE__U8

		#8 bytes integer
		res.rootTypes[RT__S8] = res.cpl.newTyp("GUs8", size=res.SIZE__U8)
		res.rootTypes[RT__U8] = res.cpl.newTyp("GUu8", size=res.SIZE__U8)

		#8 bytes floating point
		res.rootTypes[RT__F8] = res.cpl.newTyp("GUf8", size=res.SIZE__U8)

		#pointer (8 bytes for 64b arch)
		res.rootTypes[RT__PTR] = res.cpl.newTyp("GUptr", dcnDeg=1, size=res.SIZE__U8)

	#pointer (4 bytes for 32b arch)
	else:
		res.ptrSize = res.SIZE__U4
		res.rootTypes[RT__PTR] = res.cpl.newTyp("GUptr", dcnDeg=1, size=res.SIZE__U4)

	#init functions
	res.cpl.fcts = []
	res.loadLLIFcts()
	return res

class zctx:
	def __init__(sbj):
		sbj.LLIInvFilepath = None
		sbj.debugMode      = None
		sbj.deepDebugMode  = None

		#every imported context & the current one
		sbj.initialCtx   = None
		sbj.ctx          = None
		sbj.imported     = None
		sbj.subCtxs      = None

		#real memory items <<<<<<<<<<<<<<<<<<<<<< to be stored into an enm
		sbj.SIZE__U1 = 1
		sbj.SIZE__U2 = 2
		sbj.SIZE__U4 = 4
		sbj.SIZE__U8 = 8

		#size of the biggest primitive
		sbj.ptrSize = 0

		#types
		sbj.typKeyword = 0
		sbj.flyType    = 1
		sbj.rootTypes  = None

		#data
		sbj.ZCIs = None
		sbj.pcpl = None
		sbj.cpl  = None



	#load LLI functions
	def loadLLIFcts(sbj):

		#read cfg
		try:
			LLICfg = config.read(sbj.LLIInvFilepath)
		except:
			sbj.error("Problem while extracting configuration from LLI inventory file " + sbj.LLIInvFilepath, printSubCtxs=False, printLine=False)

		#for each function given
		for fName in LLICfg.keys():
			paramsTexts = LLICfg[fName].split(',')

			#get type of each parameter
			retType = TYPE_ID__UNKNOWN
			params  = [] #lst[dataItem]
			for p in range(len(paramsTexts)):

				#get type ID (should be a root type if no other default type is loaded yet)
				tID = sbj.getTypeIDFromName(paramsTexts[p])

				#"void" keyword is allowed, but every other undefined type must raise an error
				if tID == TYPE_ID__UNKNOWN and paramsTexts[p] != "void":
					sbj.error("Undefined type " + paramsTexts[p] + " given as parameter for function " + fName + " in LLI configuration file " + sbj.LLIInvFilepath, printSubCtxs=False, printLine=False)

				#retType
				if p == 0:
					retType = tID

				#params
				else:
					if tID == TYPE_ID__UNKNOWN:
						sbj.error("Cannot have \"void\" as parameter type for function " + fName + " (only allowed in return type), in LLI configuration file " + sbj.LLIInvFilepath, printSubCtxs=False, printLine=False)
					params.append( dataItem(tID, str(DEFAULT_NAME_CHARSET[p]), False, None) )

			#add function
			sbj.cpl.fcts.append(
				newFct(fName, retType, params, sbj.cpl.gblScp, None) #null content means "Will be loaded at LLI bridging time"
			)









