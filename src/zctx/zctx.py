# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/zctx.py

# -------- Z CONTEXT --------

#z code context
def newZCtx(
	filepath, LLI,
	pcpl_cfg, pcpl_itm,
	cpl_opt,  debugMode=False, deepDebugMode=False
):
	result = zctx()
	result.LLI           = {}
	result.debugMode     = debugMode
	result.deepDebugMode = deepDebugMode

	#every imported context & the current one
	result.initialCtx   = ParsingCtx(filepath, readFile(filepath))
	result.ctx          = result.initialCtx
	result.imported     = [] #history of every filename imported
	result.subCtxs      = [] #subcontexts currently in use
	result.subCtxs.append(result.initialCtx)

	#check CPL options
	result.checkCplOpt(cpl_opt)

	#init root types locally (to be given to cpl data)
	result.rootTypes = [None,None,None, None,None,None, None,None,None, None,None,None] #can be already declared as a fixed-size table (length: 12)

	#boolean
	result.rootTypes[RT__BOO]      = newTyp("GUboo")
	result.rootTypes[RT__BOO].size = result.SIZE__U1

	#1 byte
	result.rootTypes[RT__S1]      = newTyp("GUs1")
	result.rootTypes[RT__S1].size = result.SIZE__U1
	result.rootTypes[RT__U1]      = newTyp("GUu1")
	result.rootTypes[RT__U1].size = result.SIZE__U1

	#2 bytes
	result.rootTypes[RT__S2]      = newTyp("GUs2")
	result.rootTypes[RT__S2].size = result.SIZE__U2
	result.rootTypes[RT__U2]      = newTyp("GUu2")
	result.rootTypes[RT__U2].size = result.SIZE__U2

	#4 bytes
	result.rootTypes[RT__S4]      = newTyp("GUs4")
	result.rootTypes[RT__S4].size = result.SIZE__U4
	result.rootTypes[RT__U4]      = newTyp("GUu4")
	result.rootTypes[RT__U4].size = result.SIZE__U4

	#4 bytes floating point
	result.rootTypes[RT__F4]      = newTyp("GUf4")
	result.rootTypes[RT__F4].size = result.SIZE__U4

	#8 bytes
	if cpl_opt["ARCH"] == "64":

		#8 bytes integer
		result.rootTypes[RT__S8]      = newTyp("GUs8")
		result.rootTypes[RT__S8].size = result.SIZE__U8
		result.rootTypes[RT__U8]      = newTyp("GUu8")
		result.rootTypes[RT__U8].size = result.SIZE__U8

		#8 bytes floating point
		result.rootTypes[RT__F8]      = newTyp("GUf8")
		result.rootTypes[RT__F8].size = result.SIZE__U8

		#pointer (8 bytes for 64b arch)
		result.rootTypes[RT__PTR]      = newTyp("GUptr", 1)
		result.rootTypes[RT__PTR].size = result.SIZE__U8

	#pointer (4 bytes for 32b arch)
	else:
		result.rootTypes[RT__PTR]      = newTyp("GUptr", 1)
		result.rootTypes[RT__PTR].size = result.SIZE__U4

	#data
	result.ZCIs = None
	result.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	result.cpl  = newCplDat(cpl_opt, result.rootTypes)

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMPORARY FOR VAP TESTING
	result.cpl.functions = [
		result.newFct("sin", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None)]),
		result.newFct("sno", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None)]),
		result.newFct("dan", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("dor", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("amu", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("adi", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("amo", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("apo", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("bad", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("bsu", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lan", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lor", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lxo", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lls", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lrs", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("llb", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lrb", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("llr", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("lrr", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("ceq", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("cne", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("clt", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("cgt", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("cle", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("cge", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("iam", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("ina", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("fsz", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None)]),
		result.newFct("frf", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None)]),
		result.newFct("fca", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)]),
		result.newFct("ffa", result.rootTypes[RT__U8], [dataItem(result.rootTypes[RT__U8], "a", None, None), dataItem(result.rootTypes[RT__U8], "b", None, None)])
	]
	return result

class zctx:
	def __init__(self):
		self.LLI           = None
		self.debugMode     = None
		self.deepDebugMode = None

		#every imported context & the current one
		self.initialCtx   = None
		self.ctx          = None
		self.imported     = None
		self.subCtxs      = None

		#real memory items <<<<<<<<<<<<<<<<<<<<<< to be stored into an enm
		self.SIZE__U1 = 1
		self.SIZE__U2 = 2
		self.SIZE__U4 = 4
		self.SIZE__U8 = 8

		#init root types locally (to be given to cpl data)
		self.rootTypes = None

		#data
		self.ZCIs = None
		self.pcpl = None
		self.cpl  = None

	def newFct(self, name, retType, params):
		result = fct()
		result.name    = name
		result.retType = retType
		result.params  = params
		result.scope   = newScp(parent=self.cpl.globalScope) #create its own independant scope which holds a link to the parent one (that must be "global" btw)
		return result

	def getType(self, name):
		for t in self.cpl.types:
			if t.name == name:
				return t
		return None







