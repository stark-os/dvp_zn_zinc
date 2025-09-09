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
		sbj.modPrefixes = None #lst[str]
		sbj.types       = None #lst[typ]
		sbj.gblScp      = None
		sbj.fcts        = None #lst[fct]
		sbj.linkedLibs  = None #lst[]

		#program concrete elements
		#sbj.dataRes = None <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
		sbj.txtRes  = ""

def newCplDat(options, rootTypes):
	res      = cplDat()
	res.opts = options

	#z abstract elements
	res.modPrefixes = [] #lst[str]
	res.types       = [ newTyp("GUtyp") ] #virtual type "typ" (keyword) at index 0
	res.types      += lst_copy(rootTypes) #lst[typ]
	res.gblScp      = newScp()
	res.fcts        = [] #lst[fct]
	res.linkedLibs  = [] #lst[]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return res



#imp zctx






