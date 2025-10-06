# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl1.py

# -------- PRECOMPILATION --------

#pcpl data
class pcplDat:
	def __init__(sbj, cfgs, itms):
		sbj.inCodeItms = {}   #loaded in user code
		sbj.inCfgItms  = itms #loaded in cfg/pcpl_itms.cfg
		sbj.cfgs       = cfgs

		#max complexity allowed in directives
		sbj.directivesMaxComplexity = PCPL__DIRECTIVES_MAX_COMPLEXITY

		#cur nbr of failures found in one try of parsing
		sbj.failures = 0

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

		#program concrete elements
		#sbj.dataRes = None <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
		sbj.txtRes  = ""

	def newTyp(sbj, name, dcnDeg=0, size=0, dcns=None, dcnCommon=None):
		if dcnCommon is None:
			dcnCommon = typ_dcnCommon(dcnDeg, size=size) #create a new dcnCommon by default (new type => new dcnCommon)
		if dcns is None:
			dcns = []
		res           = typ()
		res.name      = name
		res.methods   = []   #lst[fct]
		res.dcns      = dcns #tab[typ]
		res.dcnCommon = dcnCommon #typ_dcnCommon

		#add type to CPL data
		typeIdx = len(sbj.types)
		sbj.types.append(res)
		return typeIdx

def newCplDat(opts):
	res      = cplDat()
	res.opts = opts

	#z abstract elements
	res.modPfxes = [] #lst[str]
	res.types    = []
	res.gblScp   = newScp()
	res.fcts     = [] #lst[fct]
	res.lnkLibs  = [] #lst[str]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return res



#create a fake ZCI with targetted type as text to be read, and then read that type
def createFakeZCIAndReadCommonType(oriZCI, commonTypeFullName, ZCIKindIfErr):
	fakeZCI              = oriZCI.copy()
	fakeZCI.ctx.icontent = istr(commonTypeFullName)
	fakeZCI.startIdx     = 0
	fakeZCI.stopIdx      = len(commonTypeFullName)-1
	fakeZCI.updateTxt()

	#try to find out a type
	return readType(fakeZCI, ZCIKindIfErr)











#imp zctx
