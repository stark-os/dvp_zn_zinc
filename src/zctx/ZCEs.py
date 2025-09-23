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
		copy          = newZCI(sbj.zCtx, lst_copy(sbj.subCtxs), modPfx=sbj.modPfx, pairs=sbj.pairs)
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
			"{mod:\"" + sbj.modPfx + \
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

	def listAllOperatorAlternatives(sbj, opeTrigram):
		return sbj.zCtx.listAllOperatorAlternatives(opeTrigram)



	#std (generated at compile time in Z, normally under atm format with subatoms etc...)
	def toAtm(sbj):
		return {
			'mod': sbj.modPfx,
			'ctx': sbj.ctx.toStr(),
			#'ctx.icontent.idx': sbj.ctx.icontent.idx,
			#'startIdx': sbj.startIdx,
			#'stopIdx': sbj.stopIdx,
			'txt': sbj.textFormat(),
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
		output = "[\n"
		for ZCI in ZCIs:
			output += TERM__OUTPUT_TAB + ZCI.toStr() + ",\n"
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
	def __init__(sbj):
		sbj.name      = None
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

	def toStr(sbj, ZCI, depth=0):
		depthSpace = TERM__OUTPUT_TAB * depth
		dataStr  = "SCOPE{\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "exes:[\n"
		for e in sbj.exes:
			if e.id == ATM__CALL:
				dataStr += depthSpace + TERM__OUTPUT_TAB + e.toStr(ZCI, depth=depth+1) + ",\n"
			elif e.id == ATM__ASG:
				dataStr += depthSpace + TERM__OUTPUT_TAB + e.toStr(ZCI, depth=depth+1) + ",\n"
#			elif e.id == ATM__STM: <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
#				dataStr += depthSpace + TERM__OUTPUT_TAB + e.toStr(ZCI) + ",\n"
			else:
				ZCIInternal(ZCI, "Got invalid atom ID in scope exes [" + str(e.id) + "].")
		dataStr += depthSpace + TERM__OUTPUT_TAB + "],\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "dataItems:[\n"
		for di in sbj.dataItems:
			dataStr += depthSpace + TERM__OUTPUT_TAB + TERM__OUTPUT_TAB + di.toStr(ZCI) + ",\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "],\n"
		dataStr += depthSpace + "}"
		return dataStr

def newScp(parent=None):
	res           = scp()
	res.exes      = [] #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
	res.dataItems = [] #lst[dataItem]
	res.parent    = parent
	return res






# -------- VAP RELATED --------

#value
class value:
	def __init__(sbj, Type, vdata, Cst):
		sbj.Type  = Type
		sbj.vdata = vdata  #atm #can be either a root type (literal), str (name) or call.
		sbj.Cst   = Cst

	def toStr(sbj, ZCI, depth=0): #I know, having a ZCI is sad here, makes not very much sens... but we need type instances (through ZCI.zCtx.cpl) to display type NAME (more readable than the ID)
		depthSpace = TERM__OUTPUT_TAB * depth
		if sbj.vdata.id == ATM__BOO:
			dataStr = "false"
			if sbj.vdata:
				dataStr = "true"

		#numerical
		elif sbj.vdata.id == ATM__S8:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 2)
		elif sbj.vdata.id == ATM__U8:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 2)
		elif sbj.vdata.id == ATM__S16:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 4)
		elif sbj.vdata.id == ATM__U16:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 4)
		elif sbj.vdata.id == ATM__S32:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 8)
		elif sbj.vdata.id == ATM__U32:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 8)
		elif sbj.vdata.id == ATM__S64:
			dataStr = 'S' + hexOnN(sbj.vdata.data, 16)
		elif sbj.vdata.id == ATM__U64:
			dataStr = 'U' + hexOnN(sbj.vdata.data, 16)
		elif sbj.vdata.id == ATM__CHR:
			dataStr = '\'' + sbj.vdata.data + '\''
		elif sbj.vdata.id == ATM__STR: #this case covers both literal string & name. In all cases, toStr() will output a double-quoted result.
			dataStr = '\"' + sbj.vdata.data + '\"'

		#common data structures (all stored as lst)
		elif sbj.vdata.id == ATM__LST_VALUE:
			dataStr = "[\n"
			for e in sbj.vdata.data:
				dataStr += depthSpace + TERM__OUTPUT_TAB + e.toStr(ZCI) + ",\n"
			dataStr += depthSpace + "]"

		#temporary storage format of FFA chain <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TEMPORARY
		elif sbj.vdata.id == ATM__LST_ATM:
			dataStr = "[\n"
			for e in sbj.vdata.data:
				if e.id == ATM__CALL:
					dataStr += depthSpace + TERM__OUTPUT_TAB + e.data.toStr(ZCI, depth=depth+1) + ",\n"
				elif e.id == ATM__STR:
					dataStr += depthSpace + TERM__OUTPUT_TAB + "\"" + e.data + "\",\n"
				else:
					ZCIInternal(ZCI, "Got an value.vdata of type lst[atm], but one of these atoms has unexpected ID [" + str(e.id) + "].")
			dataStr += depthSpace + "]"

		#calls
		elif sbj.vdata.id == ATM__CALL:
			dataStr = sbj.vdata.data.toStr(ZCI, depth=depth)

		#data items
		elif sbj.vdata.id == ATM__DATAITEM:
			dataStr = sbj.vdata.data.toStr(ZCI)

		#structure definition (fields)
		elif sbj.vdata.id == ATM__FMAP_STR_VALUE:
			dataStr = "\"fmap[str][value]{\n"
			for k in sbj.vdata.data.keys():
				dataStr += depthSpace + TERM__OUTPUT_TAB + '\"' + k + "\": " + sbj.vdata.data[k].toStr(ZCI, depth+1) + ',\n' #recursive call
			dataStr += depthSpace + '}'

		#invalid
		else:
			ZCIInternal(ZCI, "Invalid vdata stored inside value (id:" + str(sbj.vdata.id) + ").")
		return "VALUE{type:\"" + ZCI.getTypeNameFromID(sbj.Type) + "\",cst:" + str(sbj.Cst) + ",data:" + dataStr + "}"



#calls
class call:
	def __init__(sbj, name, params, retType):
		sbj.name    = name
		sbj.params  = params #lst[value]
		sbj.retType = retType

	def toStr(sbj, ZCI, depth=0): #same reason as for values, ZCI is required...
		depthSpace = TERM__OUTPUT_TAB * depth
		dataStr  = "\"CALL " + sbj.name + "(\n"
		for p in sbj.params:
			dataStr += depthSpace + TERM__OUTPUT_TAB + p.toStr(ZCI) + ',\n'
		dataStr += depthSpace + ")->[" + ZCI.getTypeNameFromID(sbj.retType) + ']'
		return dataStr

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
		depthSpacing = TERM__OUTPUT_TAB * depth

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
		return "{\n" + \
			depthSpacing + TERM__OUTPUT_TAB + "name:" + nameStr + ",\n" + \
			depthSpacing + TERM__OUTPUT_TAB + "firstOperand:" + firstOperandText + ",\n" + \
			depthSpacing + TERM__OUTPUT_TAB + "secondOperand:" + secondOperandText + "\n" + \
			depthSpacing + "}"

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
			operandsText += '\"' + a.textFormat() + "\","
		operatorsText = ""
		for o in sbj.operators:
			operatorsText += OPERATOR_NAMES[o] + ','
		return "{stopIdx:" + str(sbj.stopIdx) + ",operands:[" + operandsText + "],operators:[" + operatorsText + "]}"



#type for holding some VAP 2nd analysis information
class vap2:
	def __init__(sbj, ZCIKindIfErr, scope, cstOnly):
		sbj.ZCIKindIfErr = ZCIKindIfErr
		sbj.scope        = scope
		sbj.cstOnly      = cstOnly



#dataItem
class dataItem:
	def __init__(sbj, Type, name, initialized, initialValue, Cst=False, fields=None):
		sbj.Type         = Type
		sbj.name         = name
		sbj.initialized  = initialized
		sbj.initialValue = initialValue #value
		sbj.Cst          = Cst
		sbj.fields       = fields #lst[dataItem]

	def toStr(sbj, ZCI): #same reason as for values, we need a ZCI...
		initialValueStr = "null"
		if sbj.initialValue is not None:
			initialValueStr = sbj.initialValue.toStr(ZCI)
		fieldsText = "null"
		if sbj.fields is not None:
			fieldsText = "[\n"
			for f in sbj.fields:
				fieldsText += TERM__OUTPUT_TAB + f.toStr(ZCI) + ",\n"
			fieldsText += "]"
		return "DATAITEM{type:\"" + ZCI.getTypeNameFromID(sbj.Type) + "\",name:\"" + sbj.name + "\",initialized:" + str(sbj.initialized) + ",initialValue:" + initialValueStr + ",Cst:" + str(sbj.Cst) + ",fields:" + fieldsText + "}"






# -------- EXES --------

#assignment
class asg:
	def __init__(sbj, dst, src):
		sbj.dst = dst #dataItem
		sbj.src = src #value

	def toStr(sbj, ZCI, depth=0):
		return "ASG{dst:" + sbj.dst.toStr(ZCI) + ",src:" + sbj.src.toStr(ZCI, depth=depth+1) + "}"



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

	def toStr(sbj, ZCI, depth=0):
		depthSpace = TERM__OUTPUT_TAB * depth
		dataStr  = "FCT{\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "name:" + sbj.name + ",\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "retType:" + ZCI.getTypeNameFromID(sbj.retType) + ",\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "params:[\n"
		for p in sbj.params:
			dataStr += depthSpace + TERM__OUTPUT_TAB + TERM__OUTPUT_TAB + p.toStr(ZCI) + ",\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "],\n"
		dataStr += depthSpace + TERM__OUTPUT_TAB + "scope:" + sbj.scope.toStr(ZCI, depth=depth+1) + ",\n"
		dataStr += depthSpace + "}"
		return dataStr

def newFct(name, retType, params, gblScp, content): #global scope must be given to create its own scopes as children
	res         = fct()
	res.name    = name
	res.retType = retType
	res.params  = params
	res.scope   = newScp(parent=gblScp) #create its own independant scope which holds a link to the parent one (that must be "global" btw)
	res.content = content
	return res










