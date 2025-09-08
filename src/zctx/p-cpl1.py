# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl1.py

# -------- PRECOMPILATION --------

#pcpl data
class pcplDat:
	def __init__(self, configs, items):
		self.items   = items
		self.configs = configs

def newPcplDat(configs, items):
	formatted_configs = {}
	for c in configs.keys():
		v = configs[c]
		if v == "ON":
			formatted_configs[c] = True
		elif v == "OFF":
			formatted_configs[c] = False
		else:
			raise ValueError("Invalid value \"" + v + "\" given to precompiler configuration \"" + c + "\".")
	return pcplDat(formatted_configs, items)






# -------- COMPILATION --------

#compiler data
class cplDat:
	def __init__(self):
		self.options = None

		#z abstract elements
		self.modulePrefixes = None #lst[str]
		self.types          = None #lst[typ]
		self.globalScope    = None
		self.functions      = None #lst[fct]
		self.linkedLibs     = None #lst[]

		#program concrete elements
		#self.dataResult = None <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
		self.txtResult  = ""

def newCplDat(options, rootTypes):
	result = cplDat()
	result.options = options

	#z abstract elements
	result.modulePrefixes = [] #lst[str]
	result.types          = [ newTyp("GUtyp") ] #virtual type "typ" (keyword) at index 0
	result.types          += lst_copy(rootTypes) #lst[typ]
	result.globalScope    = newScp()
	result.functions      = [] #lst[fct]
	result.linkedLibs     = [] #lst[]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return result



#imp zctx






