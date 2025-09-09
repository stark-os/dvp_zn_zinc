# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/zctx.py

# -------- Z CONTEXT --------

#z code context
def newZCtx(
	filepath, LLI,
	pcpl_cfg, pcpl_itm,
	cpl_opt,  debugMode=False, deepDebugMode=False
):
	res               = zctx()
	res.LLI           = {}
	res.debugMode     = debugMode
	res.deepDebugMode = deepDebugMode

	#every imported context & the current one
	res.initialCtx   = ParsingCtx(filepath, readFile(filepath))
	res.ctx          = res.initialCtx
	res.imported     = [] #history of every filename imported
	res.subCtxs      = [] #subcontexts currently in use
	res.subCtxs.append(res.initialCtx)

	#check CPL options
	res.checkCplOpt(cpl_opt)

	#init root types locally (to be given to cpl data)
	res.rootTypes = [None,None,None, None,None,None, None,None,None, None,None,None] #can be already declared as a fixed-size table (length: 12)

	#boolean
	res.rootTypes[RT__BOO]      = newTyp("GUboo")
	res.rootTypes[RT__BOO].size = res.SIZE__U1

	#1 byte
	res.rootTypes[RT__S1]      = newTyp("GUs1")
	res.rootTypes[RT__S1].size = res.SIZE__U1
	res.rootTypes[RT__U1]      = newTyp("GUu1")
	res.rootTypes[RT__U1].size = res.SIZE__U1

	#2 bytes
	res.rootTypes[RT__S2]      = newTyp("GUs2")
	res.rootTypes[RT__S2].size = res.SIZE__U2
	res.rootTypes[RT__U2]      = newTyp("GUu2")
	res.rootTypes[RT__U2].size = res.SIZE__U2

	#4 bytes
	res.rootTypes[RT__S4]      = newTyp("GUs4")
	res.rootTypes[RT__S4].size = res.SIZE__U4
	res.rootTypes[RT__U4]      = newTyp("GUu4")
	res.rootTypes[RT__U4].size = res.SIZE__U4

	#4 bytes floating point
	res.rootTypes[RT__F4]      = newTyp("GUf4")
	res.rootTypes[RT__F4].size = res.SIZE__U4

	#8 bytes
	if cpl_opt["ARCH"] == "64":

		#8 bytes integer
		res.rootTypes[RT__S8]      = newTyp("GUs8")
		res.rootTypes[RT__S8].size = res.SIZE__U8
		res.rootTypes[RT__U8]      = newTyp("GUu8")
		res.rootTypes[RT__U8].size = res.SIZE__U8

		#8 bytes floating point
		res.rootTypes[RT__F8]      = newTyp("GUf8")
		res.rootTypes[RT__F8].size = res.SIZE__U8

		#pointer (8 bytes for 64b arch)
		res.rootTypes[RT__PTR]      = newTyp("GUptr", 1)
		res.rootTypes[RT__PTR].size = res.SIZE__U8

	#pointer (4 bytes for 32b arch)
	else:
		res.rootTypes[RT__PTR]      = newTyp("GUptr", 1)
		res.rootTypes[RT__PTR].size = res.SIZE__U4

	#data
	res.ZCIs = None
	res.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	res.cpl  = newCplDat(cpl_opt, res.rootTypes)

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMPORARY FOR VAP TESTING
	res.cpl.fcts = []
	'''
		res.newFct("sin", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None)]),
		res.newFct("sno", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None)]),
		res.newFct("dan", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("dor", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("amu", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("adi", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("amo", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("apo", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("bad", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("bsu", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lan", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lor", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lxo", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lls", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lrs", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("llb", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lrb", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("llr", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("lrr", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("ceq", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("cne", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("clt", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("cgt", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("cle", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("cge", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("iam", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("ina", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("fsz", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None)]),
		res.newFct("frf", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None)]),
		res.newFct("fca", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)]),
		res.newFct("ffa", res.rootTypes[RT__U8], [dataItem(res.rootTypes[RT__U8], "a", None, None), dataItem(res.rootTypes[RT__U8], "b", None, None)])
	]
	'''
	return res

class zctx:
	def __init__(sbj):
		sbj.LLI           = None
		sbj.debugMode     = None
		sbj.deepDebugMode = None

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

		#init root types locally (to be given to cpl data)
		sbj.rootTypes = None

		#data
		sbj.ZCIs = None
		sbj.pcpl = None
		sbj.cpl  = None

	def getType(sbj, name):
		for t in sbj.cpl.types:
			if t.name == name:
				return t
		return None







