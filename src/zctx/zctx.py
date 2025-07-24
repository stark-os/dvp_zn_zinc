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

	#real memory items (64bits adjustment)
	if cpl_opt["ARCH"] == "64":
		result.SIZE__LNG = 8

	#init root types locally (to be given to cpl data)
	result.rootTypes = [None,None,None, None,None,None, None,None,None, None,None,None] #can be already declared as a fixed-size table (length: 12)

	#boolean
	result.rootTypes[RT__BOO]      = newTyp("GUboo")
	result.rootTypes[RT__BOO].size = result.SIZE__BYT

	#bytes
	result.rootTypes[RT__BYT]       = newTyp("GUbyt")
	result.rootTypes[RT__BYT].size  = result.SIZE__BYT
	result.rootTypes[RT__UBYT]      = newTyp("GUubyt")
	result.rootTypes[RT__UBYT].size = result.SIZE__BYT

	#shorts
	result.rootTypes[RT__SHR]       = newTyp("GUshr")
	result.rootTypes[RT__SHR].size  = result.SIZE__SHR
	result.rootTypes[RT__USHR]      = newTyp("GUushr")
	result.rootTypes[RT__USHR].size = result.SIZE__SHR

	#integers
	result.rootTypes[RT__INT]       = newTyp("GUint")
	result.rootTypes[RT__INT].size  = result.SIZE__INT
	result.rootTypes[RT__UINT]      = newTyp("GUuint")
	result.rootTypes[RT__UINT].size = result.SIZE__INT

	#longs
	result.rootTypes[RT__LNG]       = newTyp("GUlng")
	result.rootTypes[RT__LNG].size  = result.SIZE__LNG
	result.rootTypes[RT__ULNG]      = newTyp("GUulng")
	result.rootTypes[RT__ULNG].size = result.SIZE__LNG

	#floating point
	result.rootTypes[RT__FLT]      = newTyp("GUflt")
	result.rootTypes[RT__FLT].size = result.SIZE__INT
	result.rootTypes[RT__DBL]      = newTyp("GUdbl")
	result.rootTypes[RT__DBL].size = result.SIZE__LNG

	#pointer
	result.rootTypes[RT__PTR]      = newTyp("GUptr", 1)
	result.rootTypes[RT__PTR].size = result.SIZE__LNG

	#data
	result.ZCIs = None
	result.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	result.cpl  = newCplDat(cpl_opt, result.rootTypes)

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMPORARY FOR VAP TESTING
	result.cpl.functions = [
		result.newFct("sin", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None)]),
		result.newFct("sno", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None)]),
		result.newFct("dan", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("dor", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("amu", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("adi", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("amo", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("apo", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("bad", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("bsu", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lan", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lor", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lxo", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lls", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lrs", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("llb", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lrb", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("llr", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("lrr", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("ceq", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("cne", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("clt", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("cgt", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("cle", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("cge", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("iam", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("ina", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("fsz", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None)]),
		result.newFct("frf", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None)]),
		result.newFct("fca", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)]),
		result.newFct("ffa", result.rootTypes[RT__ULNG], [dataItem(result.rootTypes[RT__ULNG], "a", None, None), dataItem(result.rootTypes[RT__ULNG], "b", None, None)])
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
		self.SIZE__BYT = 1
		self.SIZE__SHR = 2
		self.SIZE__INT = 4
		self.SIZE__LNG = 4

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







