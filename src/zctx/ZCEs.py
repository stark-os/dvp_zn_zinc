# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ZCEs.py

# -------- SEMANTIC --------

#ZCI
class zci:
	def __init__(sbj, zCtx):
		sbj.zCtx     = zCtx
		sbj.subCtxs  = None
		sbj.ctx      = None
		sbj.pairs    = None
		sbj.modPfx   = None
		sbj.startIdx = None
		sbj.stopIdx  = None
		sbj.txt      = ""

	def updateTxt(sbj):
		startIdx = sbj.startIdx
		if startIdx == -1:
			startIdx = 0
		sbj.txt = str_sub(sbj.ctx.icontent.s, startIdx, sbj.stopIdx)



	#forwarding
	def get(sbj):
		return sbj.ctx.get()

	def forward(sbj, step):
		return sbj.ctx.forward(step)

	def forwardUntil(sbj, tgtIdx):
		return sbj.ctx.forwardUntil(tgtIdx)

	def forwardAlike(sbj, otherZCI):
		return sbj.ctx.forwardAlike(otherZCI.ctx)

	def inc(sbj):
		return sbj.ctx.inc() or sbj.ctx.icontent.idx > sbj.stopIdx #additionnal stopping reason => end of ZCI

	def reachedEnd(sbj):
		return sbj.ctx.icontent.idx > sbj.stopIdx



	#ctx related
	def resetCtx(sbj, newCtx):
		sbj.ctx         = newCtx
		sbj.subCtxs[-1] = newCtx #a ZCI must have at least 1 subCtx

	def copy(sbj, ctxCopy=None): #this copy mainly affects ZCI ctx rather than the other fields
		if ctxCopy is None:
			ctxCopy   = sbj.ctx.copy()
		copy          = newZCI(sbj.zCtx, lst_copy(sbj.subCtxs), modPfx=sbj.modPfx, pairs=sbj.pairs)
		copy.startIdx = sbj.startIdx
		copy.stopIdx  = sbj.stopIdx
		copy.txt      = sbj.txt
		copy.resetCtx(ctxCopy) #we copy ctx & subctxs so that we can TEMPORARILY work on that ZCI without affecting it really
		return copy

	#WARNING! Must be used with ctx.icontent.idx at startIdx position !
	#ctx will be forwarded if necessary (beginning strip).
	def strip(sbj):
		sbj.updateTxt()

		#strip beginning
		beginningShift = str_getBeginningStripIndex(sbj.txt, charset=BLANKS_EXTENDED)
		if beginningShift != 0:
			sbj.forward(beginningShift)
			sbj.txt      = str_sub(sbj.txt, start=beginningShift)
			sbj.startIdx = sbj.ctx.icontent.idx

		#strip end
		endingIdx = str_getEndStripIndex(sbj.txt, charset=BLANKS_EXTENDED)
		if endingIdx != -1 and endingIdx != len(sbj.txt)-1:
			textLengthBefore = len(sbj.txt)
			sbj.txt         = str_sub(sbj.txt, stop=endingIdx) #strip end of sbj.txt
			sbj.stopIdx    -= textLengthBefore - len(sbj.txt)    #shift stopIdx the same amount



	#debug output
	def txtFormat(sbj):
		return sbj.txt.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"zci\"\n"
		res += d + "modPfx:\"" + sbj.modPfx + "\"\n"
		res += d + "ctx:\"" + sbj.ctx.toStr() + "\"\n"
		res += d + "ctx.icontent.idx:" + str(sbj.ctx.icontent.idx) + "\n"
		res += d + "startIdx:" + str(sbj.startIdx) + "\n"
		res += d + "stopIdx:" + str(sbj.stopIdx) + "\n"
		res += d + "txt:\"" + sbj.txtFormat() + "\"\n"
		res += d + "pairs:" + str(sbj.pairs).replace(' ', '')
		return res



	#type tools
	def getTypeInstanceFromID(sbj, id):
		return sbj.zCtx.getTypeInstanceFromID(id)

	def getTypeIDFromName(sbj, name):
		return sbj.zCtx.getTypeIDFromName(name)

	def getTypeNameFromID(sbj, id):
		return sbj.zCtx.getTypeNameFromID(id)

	def checkIDRecursivelyInType(sbj, tID, tgtID):
		return sbj.zCtx.checkIDRecursivelyInType(tID, tgtID)

	def listAllOperatorAlternatives(sbj, opeTrigram):
		return sbj.zCtx.listAllOperatorAlternatives(opeTrigram)

	def deepDbgPause(sbj):
		return sbj.zCtx.deepDbgPause()



	#std (generated at compile time in Z, normally under atm format with subatoms etc...)
	def toAtm(sbj):
		return {
			'mod': sbj.modPfx,
			'ctx': sbj.ctx.toStr(),
			'txt': sbj.txtFormat(),
			'pairs': str(sbj.pairs).replace(' ', '')
		}



def newZCI(zCtx, subCtxs, modPfx=None, pairs=None):
	if modPfx is None:
		modPfx = ""
	if pairs is None:
		pairs = {}
	if lst_isEmpty(subCtxs):
		print("[INTERNAL] Cannot instantiate a ZCI with no subCtxs.")
		exit(1)
	res          = zci(zCtx)
	res.subCtxs  = subCtxs
	res.ctx      = subCtxs[-1]
	res.pairs    = pairs
	res.modPfx   = modPfx
	res.startIdx = res.ctx.icontent.idx #current position is where our ZCI starts
	res.stopIdx  = res.startIdx
	return res

def dumpZCIs(ZCIs, filename, oneLine=True):
	if oneLine:
		output = '['
		for ZCI in ZCIs:
			output += TERM__OUTPUT_TAB + ZCI.toStr() + ","
		output += ']'
	else:
		outputLst = []
		for ZCI in ZCIs:
			outputLst.append(ZCI.toAtm())
		output = dreamlands.toText(outputLst)
	writeFile(filename, output)



#types
class typ_dcnCommon: #common data among every declination of a type
	def __init__(sbj, dcnDeg, isPub, size=0):
		sbj.isPub  = isPub
		sbj.parent = None
		sbj.size   = size
		sbj.dcnDeg = dcnDeg
		sbj.nature = NATURE__PRM
		sbj.fields = None #lst[datItm]

class typ:
	def __init__(sbj):
		sbj.name      = None
		sbj.dcns      = None #tab[typ]
		sbj.dcnCommon = None #typ_dcnCommon

	def computeStcSize(sbj, types):
		if sbj.dcnCommon.nature != NATURE__PRM:
			sbj.dcnCommon.size = 0
			for f in sbj.dcnCommon.fields: #NOTE THAT HERE, WE DO SUM SIZES AND NOT STC-SIZES ! Structures contained inside another structure are always considered as pointers.
				sbj.dcnCommon.size += types[f.Type].dcnCommon.size

#scope
class scp:
	def __init__(sbj):
		sbj.exes    = None #lst[atm] #can have either asg, jmp, call (=vfc) or stm inside, all mixed of course.
		sbj.datItms = None #lst[datItm]
		sbj.parent  = None #scp

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"scp\"\n"
		res += d + "exes:["
		for e in sbj.exes:
			res += e.toStr(depth=depth+1) + ","
		res += '\n' + d + "]\n"
		res += d + "datItms:["
		for di in sbj.datItms:
			res += di.toStr(depth=depth+1) + ","
		res += '\n' + d + ']'
		return res

def newScp(parent=None):
	res         = scp()
	res.exes    = [] #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
	res.datItms = [] #lst[dataItem]
	res.parent  = parent
	return res






# -------- VAP RELATED --------

#value
class val:
	def __init__(sbj, Type, vdat, Cst):
		sbj.Type = Type
		sbj.vdat = vdat  #atm #can be either a root type (literal), str (name) or call.
		sbj.Cst  = Cst

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"val\"\n"
		res += d + "cst:" + str(sbj.Cst) + "\n"
		res += d + "type:" + str(sbj.Type) + "\n"
		res += d + "vdat:" + sbj.vdat.toStr(depth=depth+1)
		return res



#calls
class call:
	def __init__(sbj, name, paramVals, retType):
		sbj.name      = name
		sbj.paramVals = paramVals #lst[val]
		sbj.retType   = retType

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"call\"\n"
		res += d + "name:\"" + sbj.name + "\"\n"
		res += d + "retType:" + str(sbj.retType) + "\n"
		res += d + "paramVals:["
		for p in sbj.paramVals:
			res += p.toStr(depth=depth+1) + ","
		res += '\n' + d + ']'
		return res

#"potential operator call" Same things as a call except we store only 2 params and under atm types (and we don't care about retType).
#                          We expect to have only zci or POCall types for these atoms.
#                          This allows us to work with operator calls while parameters are not analyzed yet during progressive priorizing.
class POCall:
	def __init__(sbj, opand1, opand2):
		sbj.name   = None   #str, makes no sens to give a correct value on stc creation because we will set it depending on whether a next operand exists (so we don't know at creation time)
		sbj.opeIdx = 0      #same thing
		sbj.opand1 = opand1 #atm
		sbj.opand2 = opand2 #atm

	def toStr(sbj, depth=0):

		#null name
		str_name = "null"
		if sbj.name is not None:
			str_name = '\"' + sbj.name + '\"'

		#null 1st operand
		str_opand1 = "null"
		if sbj.opand1 is not None:
			str_opand1 = sbj.opand1.toStr(depth=depth+1)

		#null 2nd operand
		str_opand2 = "null"
		if sbj.opand2 is not None:
			str_opand2 = sbj.opand2.toStr(depth=depth+1)

		#toStr
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"POCall\"\n"
		res += d + "name:\"" + str_name + "\"\n"
		res += d + "opand1:" + str_opand1 + "\n"
		res += d + "opand2:" + str_opand2
		return res

class ODPRes:
	def __init__(sbj, maxStopIdx, mainPOCall):
		sbj.maxStopIdx = maxStopIdx
		sbj.mainPOCall = mainPOCall

class opSeq:
	def __init__(sbj, stopIdx, opands, opes, opeIdxes):
		sbj.stopIdx  = stopIdx
		sbj.opands   = opands  #lst[zci]
		sbj.opes     = opes    #lst (lst[ubyt] cause enm will be stored)
		sbj.opeIdxes = opeIdxes

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		d1   = d  + TERM__OUTPUT_TAB
		res  = "\n" + d + "_:\"opSeq\"\n"
		res += d + "stopIdx:" + str(sbj.stopIdx) + "\n"
		res += d + "opands:["
		for a in sbj.opands:
			res += '\n' + d1 + '\"' + a.txtFormat() + "\","
		res += '\n' + d + "]\n"
		res += d + "opes:["
		for o in sbj.opes:
			res += '\"' + OPERATOR_NAMES[o] + "\","
		res += ']'
		return res



#type for holding some VAP 2nd analysis information
class vap2info:
	def __init__(sbj, ZCIKindIfErr, scope, cstOnly):
		sbj.ZCIKindIfErr = ZCIKindIfErr
		sbj.ZCIKindIfErr_ending = "."
		if ZCIKindIfErr is not None:
			sbj.ZCIKindIfErr_ending = ", in " + ZCIKindIfErr
		sbj.scope        = scope
		sbj.cstOnly      = cstOnly



#dataItem
class datItm:
	def __init__(sbj, Type, name, inited, initVal, Cst=False, fields=None, isPub=False):
		sbj.isPub   = isPub
		sbj.Type    = Type
		sbj.name    = name
		sbj.inited  = inited
		sbj.initVal = initVal #val
		sbj.Cst     = Cst
		sbj.fields  = fields #lst[datItm]

	def toStr(sbj, depth=0):
		d = TERM__OUTPUT_TAB * depth
		d1 = d + TERM__OUTPUT_TAB

		#null init val
		str_initVal = "null"
		if sbj.initVal is not None:
			str_initVal = sbj.initVal.toStr(depth=depth+1)

		#null fields
		str_fields = "null"
		if sbj.fields is not None:
			str_fields = '['
			for f in sbj.fields:
				str_fields += f.toStr(depth=depth+1) + ','
			str_fields += '\n' + d + ']'

		#toStr
		res  = "\n" + d + "_:\"datItm\"\n"
		res += d + "pub:" + str(sbj.isPub) + "\n"
		res += d + "type:" + str(sbj.Type) + "\n"
		res += d + "name:\"" + str(sbj.name) + "\"\n"
		res += d + "inited:" + str(sbj.inited) + "\n"
		res += d + "initVal:" + str_initVal + "\n"
		res += d + "fields:" + str_fields
		return res






# -------- EXES --------

#assignment
class asg:
	def __init__(sbj, dst, src):
		sbj.dst = dst #datItm
		sbj.src = src #val

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"asg\"\n"
		res += d + "dst:" + sbj.dst.toStr(depth=depth+1) + "\n"
		res += d + "src:" + sbj.src.toStr(depth=depth+1)
		return res



#statements
class stm_if:
	def __init__(sbj):
		sbj.conds  = [] #lst[val]
		sbj.scopes = []

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"if\"\n"
		res += d + "conds:["
		for c in sbj.conds:
			res += c.toStr(depth=depth+1) + ","
		res += '\n' + d + "]\n"
		res += d + "scopes:["
		for s in sbj.scopes:
			res += s.toStr(depth=depth+1) + ","
		res += '\n' + d + ']'
		return res

class stm_for:
	def __init__(sbj):
		sbj.iterDatItm = None
		sbj.iterCond   = None #val
		sbj.iterExe    = None #exe
		sbj.scope      = None

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"for\"\n"
		res += d + "iterDatItm:" + sbj.iterDatItm.toStr(depth=depth+1) + "\n"
		res += d + "iterCond:" + sbj.iterCond.toStr(depth=depth+1) + "\n"
		res += d + "iterExe:" + sbj.iterExe.toStr(depth=depth+1) + "\n"
		res += d + "scope:" + sbj.iterDatItm.toStr(depth=depth+1)
		return res

class stm_whi:
	def __init__(sbj):
		sbj.iterCond = None #val
		sbj.scope    = None

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"whi\"\n"
		res += d + "iterCond:" + sbj.iterCond.toStr(depth=depth+1) + "\n"
		res += d + "scope:" + sbj.iterDatItm.toStr(depth=depth+1)
		return res

class stm_swi:
	def __init__(sbj):
		sbj.tgt    = None #val
		sbj.cases  = [] #lst[val]
		sbj.scopes = []

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"swi\"\n"
		res += d + "tgt:" + sbj.tgt.toStr(depth=depth+1) + "\n"
		res += d + "cases:["
		for c in sbj.cases:
			res += c.toStr(depth=depth+1) + ","
		res += '\n' + d + "]\n"
		res += d + "scopes:["
		for s in sbj.scopes:
			res += s.toStr(depth=depth+1) + ","
		res += '\n' + d + ']'
		return res



#jumps
class jmp:
	def __init__(sbj, kind, retVal=None):
		sbj.kind   = kind
		sbj.retVal = retVal #val

	def toStr(sbj, depth=0):

		#null retVal
		str_retVal = "null"
		if sbj.retVal is not None:
			str_retVal = sbj.retVal.toStr(depth=depth+1)

		#get kind
		str_kind = "UNDEFINED"
		if sbj.kind == JMP__BRK:
			str_kind = "\"brk\""
		elif sbj.kind == JMP__CTN:
			str_kind = "\"ctn\""
		elif sbj.kind == JMP__RET:
			str_kind = "\"ret\""

		#toStr
		d    = TERM__OUTPUT_TAB * depth
		res  = "\n" + d + "_:\"jmp\"\n"
		res += d + "kind:" + str_kind + "\n"
		res += d + "retVal:" + str_retVal
		return res



#functions
class fct:
	def __init__(sbj):
		sbj.isPub    = False
		sbj.name     = None
		sbj.retType  = 0
		sbj.params   = None #lst[datItm]
		sbj.scope    = None
		sbj.methodOf = 0
		sbj.content  = None #lst[ZCI]
		sbj.dcnDep   = False

	def toStr(sbj, depth=0):
		d    = TERM__OUTPUT_TAB * depth

		#null content
		str_content = "null"
		if sbj.content is not None:
			str_content = '['
			for c in sbj.content:
				str_content += c.toStr(depth=depth+1) + ','
			str_content += '\n' + d + ']'

		#toStr
		res  = '\n' + d + "_:\"fct\"\n"
		res += d + "pub:" + str(sbj.isPub) + "\n"
		res += d + "name:\"" + sbj.name + "\"\n"
		res += d + "retType:" + str(sbj.retType) + '\n'
		res += d + "methodOf:" + str(sbj.methodOf) + '\n'
		res += d + "params:["
		for p in sbj.params:
			res += p.toStr(depth=depth+1) + ','
		res += '\n' + d + "]\n"
		res += d + "content:" + str_content + '\n'
		res += d + "scope:" + sbj.scope.toStr(depth=depth+1)
		return res

def newFct(name, retType, params, gblScp, methodOf=TYPE_ID__UNKNOWN): #global scope must be given to create its own scopes as children
	res          = fct()
	res.name     = name
	res.retType  = retType
	res.params   = params
	res.scope    = newScp(parent=gblScp) #create its own independant scope which holds a link to the parent one (that must be "global" btw)
	res.methodOf = methodOf
	return res










