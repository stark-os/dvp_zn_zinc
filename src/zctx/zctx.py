# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/zctx.py

# ---------------- Z CONTEXT ----------------

#z code context
def newZCtx(
	filepath,
	pcpl_cfg, pcpl_itm,
	cpl_opt,  cpl_mode,
	dbgMode=None, deepDbgMode=None, stepByStep=False
):
	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Pythonic
	if dbgMode is None:
		dbgMode = (False,) * 6 #len(enm DBG)
	if deepDbgMode is None:
		deepDbgMode = (False,) * 6

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< real init
	res      = zctx()
	res.step = STEP.INIT

	#debug
	res.dbgMode      = dbgMode
	res.deepDbgMode  = deepDbgMode
	res.stepByStep   = stepByStep

	#every imported context & the current one
	res.initialCtx   = ParsingCtx(filepath, readFile(filepath))
	res.ctx          = res.initialCtx
	res.imported     = [] #history of every filename imported
	res.subCtxs      = [] #subcontexts currently in use
	res.subCtxs.append(res.initialCtx)

	#actual data holders
	res.ZCIs = None
	res.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	res.cpl  = newCplDat(cpl_opt, cpl_mode)

	#check PCPL cfgs & CPL opts
	res.checkPcplCfg(res.pcpl)
	res.checkCplOpt(cpl_opt)

	#pub by default
	res.pubByDefault = (cpl_opt["DEFAULT_ACCESS_PUB"] == "ON")

	#create a list to hold root types. This is purely a simplification tool in zCtx.
	res.rootTypes = [0,0,0,0, 0,0,0,0, 0,0,0,0] #<-- fixed-size table

	#boolean
	res.rootTypes[RT__BOO] = res.cpl.newTyp("GUboo", size=res.SIZE__U8)

	#8bits
	res.rootTypes[RT__S8] = res.cpl.newTyp("GUs8", size=res.SIZE__U8)
	res.rootTypes[RT__U8] = res.cpl.newTyp("GUu8", size=res.SIZE__U8)

	#16bits
	res.rootTypes[RT__S16] = res.cpl.newTyp("GUs16", size=res.SIZE__U16)
	res.rootTypes[RT__U16] = res.cpl.newTyp("GUu16", size=res.SIZE__U16)

	#32bits
	res.rootTypes[RT__S32] = res.cpl.newTyp("GUs32", size=res.SIZE__U32)
	res.rootTypes[RT__U32] = res.cpl.newTyp("GUu32", size=res.SIZE__U32)
	res.rootTypes[RT__F32] = res.cpl.newTyp("GUf32", size=res.SIZE__U32)

	#64bits
	if cpl_opt["ARCH"] == "64":

		#8 bytes integer
		res.rootTypes[RT__S64] = res.cpl.newTyp("GUs64", size=res.SIZE__U64)
		res.rootTypes[RT__U64] = res.cpl.newTyp("GUu64", size=res.SIZE__U64)

		#8 bytes floating point
		res.rootTypes[RT__F64] = res.cpl.newTyp("GUf64", size=res.SIZE__U64)

		#pointer (8 bytes for 64b arch)
		res.rootTypes[RT__REF] = res.cpl.newTyp("GUref", dcnDeg=1, size=res.SIZE__U64)

		#max prm
		res.maxPrmType = res.rootTypes[RT__U64]
		res.maxPrmSize = res.SIZE__U64
		res.maxPrmZero = val(res.maxPrmType, atm(ATM__U64, 0), True)
		res.maxPrmOne  = val(res.maxPrmType, atm(ATM__U64, 1), True)

		#stc type
		#res.stcType = res.cpl.newTyp("GUstc", size=res.SIZE__U32)

	#reference (4 bytes for 32b arch)
	else:
		res.refSize            = res.SIZE__U32
		res.rootTypes[RT__REF] = res.cpl.newTyp("GUref", dcnDeg=1, size=res.SIZE__U32)

		#max prm
		res.maxPrmType = res.rootTypes[RT__U32]
		res.maxPrmSize = res.SIZE__U32
		res.maxPrmZero = val(res.maxPrmType, atm(ATM__U32, 0), True)
		res.maxPrmOne  = val(res.maxPrmType, atm(ATM__U32, 1), True)

		#stc type
		#res.stcType = res.cpl.newTyp("GUstc", size=res.SIZE__U32)

	#init root stcs
	res.rootStcTypes = zCtx__addRootStcs(res)

	#dcn related
	res.dcnDegMax   = int(cpl_opt["DCN_NBR_MAX"])
	res.gncDcnType  = res.cpl.newTyp("GUdcn")
	res.spcDcnTypes = []
	for d in range(res.dcnDegMax):
		res.spcDcnTypes.append( res.cpl.newTyp("GUdcn" + str(d)) )

	#init LLI fcts
	res.cpl.fcts = []
	res.loadLLIFcts()
	return res



class zctx:
	def __init__(sbj):

		#debug
		sbj.dbgMode     = None
		sbj.deepDbgMode = None

		#every imported context & the current one
		sbj.initialCtx = None
		sbj.ctx        = None
		sbj.imported   = None
		sbj.subCtxs    = None

		#real memory items <<<<<<<<<<<<<<<<<<<<<< to be stored into an enm
		sbj.SIZE__U8  = 1
		sbj.SIZE__U16 = 2
		sbj.SIZE__U32 = 4
		sbj.SIZE__U64 = 8

		#biggest prm
		sbj.maxPrmType = 0
		sbj.maxPrmSize = 0
		sbj.maxPrmZero = None
		sbj.maxPrmOne  = None

		#types
		sbj.rootTypes    = None
		#sbj.stcType    = None
		sbj.rootStcTypes = None
		sbj.rawTypeNames = {} #mmap[str,ulng]
		sbj.gncDcnType   = 0
		sbj.spcDcnTypes  = None
		sbj.dcnDegMax    = 0

		#data
		sbj.ZCIs = None
		sbj.pcpl = None
		sbj.cpl  = None

		#other
		sbj.pubByDefault = True



	#load LLI functions
	def loadLLIFcts(sbj):
		LLIInvFilePath = sbj.cpl.opts['DEFAULT_LLI_INV_PATH']

		#read cfg
		try:
			LLICfg = config.read(LLIInvFilePath)
		except:
			sbj.err("Problem while extracting configuration from LLI inventory file " + LLIInvFilePath, prtSubCtxs=False, prtLine=False)

		#for each function given
		for fName in LLICfg.keys():
			paramsTxts = LLICfg[fName].split(',')

			#get type of each parameter
			retType = TYPE_ID__UNKNOWN
			params  = [] #lst[datItm]
			for p in range(len(paramsTxts)):

				#get type ID (should be a root type if no other default type is loaded yet)
				tID = sbj.getTypeIDFromName(paramsTxts[p])

				#"void" keyword is allowed, but every other undefined type must raise an error
				if tID == TYPE_ID__UNKNOWN and paramsTxts[p] != "void":
					sbj.err("Undefined type " + paramsTxts[p] + " given as parameter for function " + fName + " in LLI configuration file " + LLIInvFilePath, prtSubCtxs=False, prtLine=False)

				#retType
				if p == 0:
					retType = tID

				#params
				else:
					if tID == TYPE_ID__UNKNOWN:
						sbj.err("Cannot have \"void\" as parameter type for function " + fName + " (only allowed in return type), in LLI configuration file " + LLIInvFilePath, prtSubCtxs=False, prtLine=False)
					params.append( datItm(tID, str(DEFAULT_NAME_CHARSET[p]), False, None) )

			#special behavior: root types fcts => REMOVE LAST PARAM FOR COMPILATION (will be added at compile time) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
			#if fName.startswith("GFtab_") or fName.startswith("GFlst_") or fName.startswith("GFdlt_"):
			#	params = params[:-1]

			#add function, null content means "Will be loaded at LLI bridging time"
			sbj.cpl.fcts.append( newFct(fName, retType, params, sbj.cpl.gblScp) )









