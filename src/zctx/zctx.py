# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/zctx.py

# ---------------- Z CONTEXT ----------------

#z code context
def newZCtx(
	filepath,
	pcpl_cfg, pcpl_itm,
	cpl_opt,  cpl_info,
	log_lvls=None, stepByStep=False
):
	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Pythonic
	if log_lvls is None:
		log_lvls = (LOG__LVL_ERR,) * 7 #len(enm STEP)

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< real init
	res      = zctx()
	res.step = STEP.INIT

	#debug
	res.log_lvls   = log_lvls
	res.stepByStep = stepByStep

	#every imported context & the current one
	res.initialCtx   = ParsingCtx(filepath, readFile(filepath))
	res.ctx          = res.initialCtx
	res.imported     = [] #history of every filename imported
	res.subCtxs      = [] #subcontexts currently in use
	res.subCtxs.append(res.initialCtx)

	#actual data holders
	res.ZCIs = None
	res.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	res.cpl  = newCplDat(cpl_opt, cpl_info)

	#check PCPL cfgs & CPL opts
	res.checkPcplCfg(res.pcpl)
	res.checkCplOpt(cpl_opt)

	#pub by default
	res.pubByDefault = (cpl_opt["DEFAULT_ACCESS_PUB"] == "ON")

	#create a list to hold root types. This is purely a simplification tool in zCtx.
	res.rootTypes = [0,0,0,0, 0,0,0,0, 0,0,0,0] #<-- fixed-size table

	#boolean
	res.rootTypes[RT__BOL] = res.cpl.newTyp("GUbol", size=res.SIZE__U8)

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

		#max prm
		res.smaxType = res.cpl.newTyp("GUsmax", size=res.SIZE__U64)
		res.smaxSize = res.SIZE__U64
		res.smaxZero = val(res.smaxType, atm(ATM__S64, 0), True)
		res.smaxOne  = val(res.smaxType, atm(ATM__S64, 1), True)

		#set also as smax parent
		smaxInst = res.getTypeInstanceFromID(res.smaxType)
		smaxInst.dcnCommon.parent = res.rootTypes[RT__S64]

	#32bits
	else:

		#max prm
		res.smaxPrmType = res.rootTypes[RT__S32]
		res.smaxPrmSize = res.SIZE__U32
		res.smaxPrmZero = val(res.smaxPrmType, atm(ATM__S32, 0), True)
		res.smaxPrmOne  = val(res.smaxPrmType, atm(ATM__S32, 1), True)

		#set also as smax parent
		smaxInst = res.getTypeInstanceFromID(res.smaxType)
		smaxInst.dcnCommon.parent = res.rootTypes[RT__S32]

	#refs
	res.refType = res.cpl.newTyp("GUref", dcnDeg=1, size=res.smaxSize)

	#raw
	res.rawType = res.cpl.newTyp("GUraw")
	rawTypeInst = res.getTypeInstanceFromID(res.rawType)
	rawTypeInst.dcnCommon.nature = NATURE__STC
	rawTypeInst.dcnCommon.fields = [
		datItm(res.smaxType, "len", False, None),
		datItm(res.smaxType, "dat", False, None)
	]
	rawTypeInst.computeStcSize(res.cpl)
	rawTypeInst.dcnCommon.isPub = False

	#stc type
	#res.stcType = res.cpl.newTyp("GUstc", size=res.smaxSize)

	#init root stcs
	#res.rootStcTypes = zCtx__addRootStcs(res) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< let's say they must be given by user

	#atm type
	res.atmType = TYPE_ID__UNKNOWN
	if cpl_info | CPL__MODE_MASK == CPL__MODE_Z and cpl_opt['ATM_GENERATED_CONTENT'] == "ON":
		res.atmType                  = res.cpl.newTyp("GUatm")
		atmTypeInst                  = res.getTypeInstanceFromID(res.atmType)
		atmTypeInst.dcnCommon.nature = NATURE__STC
		atmTypeInst.dcnCommon.fields = [
			datItm(res.smaxType, "id", False, None),
			datItm(res.refType, "dat", False, None)
		]
		atmTypeInst.computeStcSize(res.cpl)
		atmTypeInst.dcnCommon.isPub = False

	#dcn related
	res.dcnDegMax   = int(cpl_opt["DCN_NBR_MAX"])
	res.gncDcnType  = res.cpl.newTyp("GUdcn")
	res.spcDcnTypes = []
	for d in range(res.dcnDegMax):
		res.spcDcnTypes.append( res.cpl.newTyp("GUdcn" + str(d)) )
	return res



class zctx:
	def __init__(sbj):

		#log
		sbj.log_lvls = None

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
		sbj.smaxType = 0
		sbj.smaxSize = 0
		sbj.smaxZero = None
		sbj.smaxOne  = None

		#types
		sbj.rootTypes    = None
		sbj.refType      = 0
		sbj.rawType      = 0
		#sbj.stcType      = None
		#sbj.rootStcTypes = None <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< let's say they must be given by user
		sbj.atmType      = 0

		#dcn related
		sbj.gncDcnType  = 0
		sbj.spcDcnTypes = None
		sbj.dcnDegMax   = 0

		#data
		sbj.ZCIs = None
		sbj.pcpl = None
		sbj.cpl  = None

		#other
		sbj.pubByDefault = True
