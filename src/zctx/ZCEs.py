# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ZCEs.py

# -------- SEMANTIC --------

#ZCI
class zci:
	def __init__(sbj, zCtx):
		sbj.zCtx      = zCtx
		sbj.subCtxs   = None
		sbj.ctx       = None
		sbj.pairs     = None
		sbj.modPrefix = None
		sbj.startIdx  = None
		sbj.stopIdx   = None
		sbj.txt       = ""

	def updateText(sbj):
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
		copy          = newZCI(sbj.zCtx, lst_copy(sbj.subCtxs), modPrefix=sbj.modPrefix, pairs=sbj.pairs)
		copy.startIdx = sbj.startIdx
		copy.stopIdx  = sbj.stopIdx
		copy.txt      = sbj.txt
		copy.resetCtx(ctxCopy) #we copy ctx & subctxs so that we can TEMPORARILY work on that ZCI without affecting it really
		return copy

	#WARNING! Must be used with ctx.icontent.idx at startIdx position !
	#ctx will be forwarded if necessary (beginning strip).
	def strip(sbj):
		sbj.updateText()

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
	def textFormat(sbj):
		return sbj.txt.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")

	def toStr(sbj):
		return \
			"{mod:\"" + sbj.modPrefix + \
			"\",ctx:\"" + sbj.ctx.toStr() + \
			"\",ctx.icontent.idx:" + str(sbj.ctx.icontent.idx) + \
			",startIdx:" + str(sbj.startIdx) + \
			",stopIdx:" + str(sbj.stopIdx) + \
			",txt:\"" + sbj.textFormat() + \
			"\",pairs:\"" + str(sbj.pairs).replace(' ', '') + \
			"\"}"



	#type tools
	def getTypeInstanceFromID(sbj, id):
		return sbj.zCtx.getTypeInstanceFromID(id)

	def getTypeIDFromName(sbj, name):
		return sbj.zCtx.getTypeIDFromName(name)

	def getTypeNameFromID(sbj, id):
		return sbj.zCtx.getTypeNameFromID(id)

	def checkIDRecursivelyInType(sbj, tID, tgtID):
		return sbj.zCtx.checkIDRecursivelyInType(tID, tgtID)



	#std (generated at compile time in Z, normally under atm format with subatoms etc...)
	def toAtm(sbj):
		return {
			'mod': sbj.modPrefix,
			'ctx': sbj.ctx.toStr(),
			#'ctx.icontent.idx': sbj.ctx.icontent.idx,
			#'startIdx': sbj.startIdx,
			#'stopIdx': sbj.stopIdx,
			'txt': sbj.textFormat(),
			'pairs': str(sbj.pairs).replace(' ', '')
		}



def newZCI(zCtx, subCtxs, modPrefix=None, pairs=None):
	if modPrefix is None:
		modPrefix = ""
	if pairs is None:
		pairs = {}
	if lst_isEmpty(subCtxs):
		print("[INTERNAL] Cannot instantiate a ZCI with no subCtxs.")
		exit(1)
	res           = zci(zCtx)
	res.subCtxs   = subCtxs
	res.ctx       = subCtxs[-1]
	res.pairs     = pairs
	res.modPrefix = modPrefix
	res.startIdx  = res.ctx.icontent.idx #current position is where our ZCI starts
	res.stopIdx   = res.startIdx
	return res

def dumpZCIs(ZCIs, filename, oneLine=True):
	if oneLine:
		output = "[\n"
		for ZCI in ZCIs:
			output += "\t" + ZCI.toStr() + ",\n"
		output += "]"
	else:
		outputLst = []
		for ZCI in ZCIs:
			outputLst.append(ZCI.toAtm())
		output = dreamlands.toText(outputLst)
	writeFile(filename, output)



#types
class typ_dcnCommon: #common data among every declination of a type
	def __init__(sbj, dcnDeg, size=0):
		sbj.parent = None
		sbj.size   = size
		sbj.dcnDeg = dcnDeg

		#stc related
		sbj.nature  = NATURE__PRM
		sbj.fields  = None #lst[dataItem]
		sbj.stcSize = 0

class typ:
	def __init__(sbj, size):
		sbj.name      = None
		sbj.methods   = None #lst[fct]
		sbj.dcns      = None #tab[typ]
		sbj.dcnCommon = None #typ_dcnCommon

	def computeStcSize(sbj, types):
		if sbj.dcnCommon.nature != NATURE__PRM:
			for f in sbj.dcnCommon.fields: #NOTE THAT HERE, WE DO SUM SIZES AND NOT STC-SIZES ! Structures contained inside another structure are always considered as pointers.
				sbj.dcnCommon.stcSize += types[f.Type].dcnCommon.size

#scope
class scp:
	def __init__(sbj):
		sbj.exes      = None #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
		sbj.dataItems = None #lst[dataItem]
		sbj.parent    = None #scp

def newScp(parent=None):
	res           = scp()
	res.exes      = [] #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
	res.dataItems = [] #lst[dataItem]
	res.parent    = parent
	return res






# -------- VAP RELATED --------

#value
class value:
	def __init__(sbj, Type, vdata, Cst=False):
		sbj.Type  = Type
		sbj.vdata = vdata  #atm #can be either a root type (literal), str (name) or call.
		sbj.Cst   = Cst

	def toStr(sbj, depth=0):
		depthSpace = '\t' * depth
		if sbj.vdata.id == ATM__BOO: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< I know, this seems weird in Python but it makes sens in Z (will have to be a swi btw)
			dataStr = "false"
			if sbj.vdata:
				dataStr = "true"

		#numerical
		elif sbj.vdata.id == ATM__S1:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 2)
		elif sbj.vdata.id == ATM__U1:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 2)
		elif sbj.vdata.id == ATM__S2:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 4)
		elif sbj.vdata.id == ATM__U2:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 4)
		elif sbj.vdata.id == ATM__S4:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 8)
		elif sbj.vdata.id == ATM__U4:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 8)
		elif sbj.vdata.id == ATM__S8:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 16)
		elif sbj.vdata.id == ATM__U8:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 16)
		elif sbj.vdata.id == ATM__CHR:
			dataStr = '\'' + sbj.vdata.data + '\''
		elif sbj.vdata.id == ATM__STR: #this case covers both literal string & name. In all cases, toStr() will output a double-quoted result.
			dataStr = '\"' + sbj.vdata.data + '\"'

		#common data structures (all stored as lst)
		elif sbj.vdata.id == ATM__LST:
			dataStr = '['
#			for e in sbj.vdata.data:
#				dataStr += e.toStr() + ',' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMPORARILY SWITCHING TO A MORE TOLERANT WAY
			for e in sbj.vdata.data:
				if isinstance(e, atm):
					dataStr += e.data.toStr() + ','
				else:
					dataStr += e.toStr() + ','
			dataStr += ']'

		#calls
		elif sbj.vdata.id == ATM__CALL:
			dataStr  = "\"call " + sbj.vdata.data.name + "(\n"
			for p in sbj.vdata.data.params:
				dataStr += depthSpace + '\t' + p.toStr(depth+1) + ',\n' #recursive call
			dataStr += depthSpace + ")->[" + str(sbj.vdata.data.retType) + ']'

		#structure definition (fields)
		elif sbj.vdata.id == ATM__FMAP_STR_VALUE:
			dataStr  = "\"fmap[str][value]{\n"
			for k in sbj.vdata.data.keys():
				dataStr += depthSpace + '\t' + k + ": " + sbj.vdata.data[k].toStr(depth+1) + ',\n' #recursive call
			dataStr += depthSpace + '}'

		#invalid
		else:
			print("[INTERNAL] Invalid data stored inside value (can only be literal, name or call).")
			exit(1)
		return "{type:\"" + str(sbj.Type) + "\",cst:" + str(sbj.Cst) + ",data:" + dataStr + "}"



#calls
class call:
	def __init__(sbj, name, params, retType):
		sbj.name    = name
		sbj.params  = params #lst[value]
		sbj.retType = retType

#"potential operator call" Same things as a call except we store only 2 params and under atm types.
#                          We expect to have only zci or POCall types for these atoms.
#                          This allows us to work with operator calls while parameters are not analyzed yet during progressive priorizing.
class POCall:
	def __init__(sbj, firstOperand, secondOperand):
		sbj.name          = None          #str, makes no sens to give a correct value on stc creation because we will set it depending on whether a next operand exists (so we don't know at creation time)
		sbj.operatorIdx   = 0             #same thing
		sbj.firstOperand  = firstOperand  #atm
		sbj.secondOperand = secondOperand #atm

	def toStr(sbj, depth=0):
		depthSpacing = '\t' * depth

		#name
		nameStr = "null"
		if sbj.name is not None:
			nameStr = '"' + sbj.name + '"'

		#1st operand
		firstOperandText = "null"
		if sbj.firstOperand is not None:
			if sbj.firstOperand.id == ATM__ZCI:
				firstOperandText = '\"' + sbj.firstOperand.data.textFormat() + '\"'
			elif sbj.firstOperand.id == ATM__POCALL:
				firstOperandText = sbj.firstOperand.data.toStr(depth+1)

		#2nd operand
		secondOperandText = "null"
		if sbj.secondOperand is not None:
			if sbj.secondOperand.id == ATM__ZCI:
				secondOperandText = '\"' + sbj.secondOperand.data.textFormat() + '\"'
			elif sbj.secondOperand.id == ATM__POCALL:
				secondOperandText = sbj.secondOperand.data.toStr(depth+1)

		#final string
		return "{\n" + depthSpacing + "\tname:" + nameStr + ",\n" + depthSpacing + "\tfirstOperand:" + firstOperandText + ",\n" + depthSpacing + "\tsecondOperand:" + secondOperandText + "\n" + depthSpacing + "}"

class ODPRes:
	def __init__(sbj, maxStopIdx, mainPOCall):
		sbj.maxStopIdx = maxStopIdx
		sbj.mainPOCall = mainPOCall

class opSeq:
	def __init__(sbj, stopIdx, operands, operators, operatorIdxes):
		sbj.stopIdx       = stopIdx
		sbj.operands      = operands  #lst[zci]
		sbj.operators     = operators #lst (lst[ubyt] cause enm will be stored)
		sbj.operatorIdxes = operatorIdxes

	def toStr(sbj):
		operandsText = ""
		for a in sbj.operands:
			operandsText += '\"' + a.textFormat() + ",\""
		operatorsText = ""
		for o in sbj.operators:
			operatorsText += OPERATOR_NAMES[o] + ','
		return "{stopIdx:" + str(sbj.stopIdx) + ",operands:[" + operandsText + "],operators:[" + operatorsText + "]}"



#type for holding some VAP 2nd analysis information
class vap2:
	def __init__(sbj, ZCIKindIfError, scope, cstOnly):
		sbj.ZCIKindIfError = ZCIKindIfError
		sbj.scope          = scope
		sbj.cstOnly        = cstOnly



#dataItem
class dataItem:
	def __init__(sbj, Type, name, initialized, initialValue, Cst=False, fields=None):
		sbj.Type         = Type
		sbj.name         = name
		sbj.initialized  = initialized
		sbj.initialValue = initialValue #value
		sbj.Cst          = Cst
		sbj.fields       = fields #lst[dataItem]

	def toStr(sbj):
		initialValueStr = "null"
		if sbj.initialValue is not None:
			initialValueStr = sbj.initialValue.toStr()
		fieldsText = "null"
		if sbj.fields is not None:
			fieldsText = "[\n"
			for f in sbj.fields:
				fieldsText += "\t" + f.toStr() + ",\n"
			fieldsText += "]"
		return "{type:" + str(sbj.Type) + ",name:\"" + sbj.name + "\",initialized:" + str(sbj.initialized) + ",initialValue:" + initialValueStr + ",Cst:" + str(sbj.Cst) + ",fields:" + fieldsText + "}"






# -------- EXES --------

#assignment
class asg:
	def __init__(sbj, dst, src):
		sbj.dst = dst #dataItem
		sbj.src = src #value



#statements
class stm:
	def __init__(sbj):
		sbj.kind  = None
		sbj.scope = None

def newStm(kind, parentScp):
	res       = stm()
	res.kind  = kind
	res.scope = newScp(parent=parentScp)
	return res

class fct:
	def __init__(sbj):
		sbj.name    = None
		sbj.retType = 0
		sbj.params  = None #lst[dataItem]
		sbj.scope   = None
		sbj.content = None #lst[ZCI]

def newFct(name, retType, params, gblScp, content): #global scope must be given to create its own scopes as children
	res         = fct()
	res.name    = name
	res.retType = retType
	res.params  = params
	res.scope   = newScp(parent=gblScp) #create its own independant scope which holds a link to the parent one (that must be "global" btw)
	res.content = content
	return res










