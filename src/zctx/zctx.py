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

	#data
	res.ZCIs = None
	res.pcpl = newPcplDat(pcpl_cfg, pcpl_itm)
	res.cpl  = newCplDat(cpl_opt)

	#"typ" keyword: virtual type that seems to work like a regular one for the moment
	res.typKeyword = res.cpl.newTyp("GUtyp")

	#"fly" virtual type that also seems to work like a regular one for the moment
	res.flyType    = res.cpl.newTyp("GUfly")

	#create a list to hold root types. This is purely a simplification tool in zCtx.
	res.rootTypes = [0,0,0, 0,0,0, 0,0,0, 0,0,0] #can be already declared as a fixed-size table (length: 12)

	#boolean
	res.rootTypes[RT__BOO] = res.cpl.newTyp("GUboo", size=res.SIZE__U1)

	#1 byte
	res.rootTypes[RT__S1] = res.cpl.newTyp("GUs1", size=res.SIZE__U1)
	res.rootTypes[RT__U1] = res.cpl.newTyp("GUu1", size=res.SIZE__U1)

	#2 bytes
	res.rootTypes[RT__S2] = res.cpl.newTyp("GUs2", size=res.SIZE__U2)
	res.rootTypes[RT__U2] = res.cpl.newTyp("GUu2", size=res.SIZE__U2)

	#4 bytes
	res.rootTypes[RT__S4] = res.cpl.newTyp("GUs4", size=res.SIZE__U4)
	res.rootTypes[RT__U4] = res.cpl.newTyp("GUu4", size=res.SIZE__U4)

	#4 bytes floating point
	res.rootTypes[RT__F4] = res.cpl.newTyp("GUf4", size=res.SIZE__U4)

	#8 bytes
	if cpl_opt["ARCH"] == "64":
		res.ptrSize = res.SIZE__U8

		#8 bytes integer
		res.rootTypes[RT__S8] = res.cpl.newTyp("GUs8", size=res.SIZE__U8)
		res.rootTypes[RT__U8] = res.cpl.newTyp("GUu8", size=res.SIZE__U8)

		#8 bytes floating point
		res.rootTypes[RT__F8] = res.cpl.newTyp("GUf8", size=res.SIZE__U8)

		#pointer (8 bytes for 64b arch)
		res.rootTypes[RT__PTR] = res.cpl.newTyp("GUptr", dcnDeg=1, size=res.SIZE__U8)

	#pointer (4 bytes for 32b arch)
	else:
		res.ptrSize = res.SIZE__U4
		res.rootTypes[RT__PTR] = res.cpl.newTyp("GUptr", dcnDeg=1, size=res.SIZE__U4)

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

		#size of the biggest primitive
		sbj.ptrSize = 0

		#types
		sbj.typKeyword = 0
		sbj.flyType    = 1
		sbj.rootTypes  = None

		#data
		sbj.ZCIs = None
		sbj.pcpl = None
		sbj.cpl  = None

	def getTypeInstanceFromID(sbj, id):
		if id >= 0 and id < len(sbj.cpl.types):
			return sbj.cpl.types[id]
		return None

	def getTypeIDFromName(sbj, name):
		for t in range(len(sbj.cpl.types)):
			if sbj.cpl.types[t].name == name:
				return t
		return TYPE_ID__NOT_FOUND

	def getTypeNameFromID(sbj, id):
		i = sbj.getTypeInstanceFromID(id)
		if i is None:
			return "<void>"
		return i.name

	def checkIDRecursivelyInType(sbj, tID, tgtID):
		print("ID[" + str(tID) + "]     TARGET["+str(tgtID)+"]")
		if tID == tgtID:
			return True
		dcns = sbj.getTypeInstanceFromID(tID).dcns
		if dcns is not None:
			for d in dcns:
				if sbj.checkIDRecursivelyInType(d, tgtID):
					return True
		return False







