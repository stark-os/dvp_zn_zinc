# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl1.py

# -------- PRECOMPILATION --------

#pcpl data
class pcplDat:
	def __init__(sbj, cfgs, itms):
		sbj.inCodeItms = {}   #loaded in user code
		sbj.inCfgItms  = itms #loaded in cfg/pcpl_itms.cfg
		sbj.cfgs       = cfgs

		#literal str
		sbj.litStrIdx = -1
		sbj.litStr    = []

		#max complexity allowed in directives
		sbj.directivesMaxComplexity = PCPL__DIRECTIVES_MAX_COMPLEXITY

		#indicator to know whether a PCPL directive has affected code text or not
		sbj.failures   = [] #lst[PCPL_failure]
		sbj.gotChanges = False

	def nextLitStrDIName(sbj):
		sbj.litStrIdx += 1
		return "_" + str(sbj.litStrIdx)

def newPcplDat(cfgs, itms):
	formattedCfgs = {}
	for c in cfgs.keys():
		v = cfgs[c]
		if v == "ON":
			formattedCfgs[c] = True
		elif v == "OFF":
			formattedCfgs[c] = False
		else:
			raise ValueError("Invalid value \"" + v + "\" given to precompiler configuration \"" + c + "\".")
	return pcplDat(formattedCfgs, itms)

class PCPL_failure:
	def __init__(sbj, ctx, msg):
		sbj.ctx = ctx
		sbj.msg = msg






# -------- COMPILATION --------

#compiler data
class cplDat:
	def __init__(sbj):
		sbj.opts = None

		#z abstract elements
		sbj.modPfxes = None #lst[str]
		sbj.types    = None #lst[int]
		sbj.gblScp   = None
		sbj.fcts     = None #lst[fct]
		sbj.lnkLibs  = None #lst[]

		#general info
		sbj.mode         = 0
		sbj.forbidUseRef = 0

		#ffa
		sbj.ffa_fieldTypeIDs = []

		#program concrete elements
		sbj.resC    = ""
		sbj.resFP   = ""
		sbj.resFP_C = "" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TMP

	def newTyp(sbj, name, dcnDeg=0, size=0, dcns=None, dcnCommon=None, isPub=False):
		if dcnCommon is None:
			dcnCommon = typ_dcnCommon(dcnDeg, isPub, size=size) #create a new dcnCommon by default (new type => new dcnCommon)
		if dcns is None:
			dcns = []
		res           = typ()
		res.name      = name
		res.methods   = []   #lst[fct]
		res.dcns      = dcns #tab[typ]
		res.dcnCommon = dcnCommon #typ_dcnCommon

		#external
		res.ext = False

		#add type to CPL data
		typeIdx = len(sbj.types)
		sbj.types.append(res)
		return typeIdx

def newCplDat(opts, info):
	res              = cplDat()
	res.opts         = opts
	res.mode         = info & CPL__MODE_MASK
	res.forbidUseRef = info & CPL__USE_REF_MASK

	#z abstract elements
	res.modPfxes = [] #lst[str]
	res.types    = []
	res.gblScp   = newScp()
	res.fcts     = [] #lst[fct]
	res.lnkLibs  = [] #lst[str]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return res











#imp zctx
