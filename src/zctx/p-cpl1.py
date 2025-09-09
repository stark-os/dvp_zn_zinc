# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl1.py

# -------- PRECOMPILATION --------

#pcpl data
class pcplDat:
	def __init__(sbj, cfgs, itms):
		sbj.itms = itms
		sbj.cfgs = cfgs

def newPcplDat(cfgs, itms):
	formatted_cfgs = {}
	for c in cfgs.keys():
		v = cfgs[c]
		if v == "ON":
			formatted_cfgs[c] = True
		elif v == "OFF":
			formatted_cfgs[c] = False
		else:
			raise ValueError("Invalid value \"" + v + "\" given to precompiler configuration \"" + c + "\".")
	return pcplDat(formatted_cfgs, itms)






# -------- COMPILATION --------

#compiler data
class cplDat:
	def __init__(sbj):
		sbj.opts = None

		#z abstract elements
		sbj.modPrefixes   = None #lst[str]
		sbj.types         = None #lst[int]
		sbj.unsolvedTypes = None #lst[ZCI] #temporarily keep each ZCI corresponding to an unsolved type aside. We solve types in 2 steps
		sbj.gblScp        = None
		sbj.fcts          = None #lst[fct]
		sbj.linkedLibs    = None #lst[]

		#program concrete elements
		#sbj.dataRes = None <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
		sbj.txtRes  = ""

	def addUnsolvedType(sbj, ZCI):
		sbj.unsolvedTypes.append(ZCI.copy())
		return -len(sbj.unsolvedTypes) #negative index as type ID means "unsolved"

	def newTyp(sbj, name, dcnDeg=0, size=0, dcns=None, commonDcnData=None):
		if commonDcnData is None:
			commonDcnData = typ_commonDcnData(dcnDeg, size=size) #create a new commonDcnData by default (new type => new commonDcnData)
		res               = typ(size)
		res.name          = name
		res.methods       = []   #lst[fct]
		res.dcns          = dcns #tab[typ]
		res.commonDcnData = commonDcnData #typ_commonDcnData

		#add type to CPL data
		typeIdx = len(sbj.types)
		sbj.types.append(res)
		return typeIdx

def newCplDat(opts):
	res      = cplDat()
	res.opts = opts

	#z abstract elements
	res.modPrefixes   = [] #lst[str]
	res.types         = [typ(0)] #index 0 == TYPE_ID__NOT_FOUND, must corresponds to nothing useful.
	res.unsolvedTypes = []
	res.gblScp        = newScp()
	res.fcts          = [] #lst[fct]
	res.linkedLibs    = [] #lst[]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return res



#create a fake ZCI with targetted type as text to be read, and then read that type (can be "unsolved")
def createFakeZCIAndTryReadingCommonType(originalZCI, commonTypeFullName, ZCIKindIfError):
	fakeZCI              = originalZCI.copy()
	fakeZCI.ctx.icontent = istr(commonTypeFullName)
	fakeZCI.startIdx     = 0
	fakeZCI.stopIdx      = len(commonTypeFullName)-1
	fakeZCI.updateText()

	#try to find out a type
	return readType(fakeZCI, ZCIKindIfError, allowUnsolved=True)











#imp zctx
