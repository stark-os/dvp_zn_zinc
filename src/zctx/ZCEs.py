# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ZCEs.py

# -------- SEMANTIC --------

#ZCI
class zci:
	def __init__(self):
		self.subCtxs      = None
		self.ctx          = None
		self.pairs        = None
		self.modulePrefix = None
		self.startIndex   = None
		self.stopIndex    = None
		self.text         = ""

	def updateText(self):
		startIndex = self.startIndex
		if startIndex == -1:
			startIndex = 0
		self.text = str_sub(self.ctx.icontent.s, startIndex, self.stopIndex)



	#forwarding
	def get(self):
		return self.ctx.get()

	def forward(self, step):
		return self.ctx.forward(step)

	def inc(self):
		return self.ctx.inc() or self.ctx.icontent.index > self.stopIndex #additionnal stopping reason => end of ZCI

	def reachedEnd(self):
		return self.ctx.icontent.index > self.stopIndex



	#ctx related
	def resetCtx(self, newCtx):
		self.ctx         = newCtx
		self.subCtxs[-1] = newCtx #a ZCI must have at least 1 subCtx

	def copy(self, ctxCopy=None): #this copy mainly affects ZCI ctx rather than the other fields
		if ctxCopy is None:
			ctxCopy = self.ctx.copy()
		copy            = newZCI(lst_copy(self.subCtxs), modulePrefix=self.modulePrefix, pairs=self.pairs)
		copy.startIndex = self.startIndex
		copy.stopIndex  = self.stopIndex
		copy.text = self.text
		copy.resetCtx(ctxCopy) #we copy ctx & subctxs so that we can TEMPORARILY work on that ZCI without affecting it really
		return copy

	#WARNING! Must be used with ctx.icontent.index at startIndex position !
	#ctx will be forwarded if necessary (beginning strip).
	def strip(self):
		self.updateText()

		#strip beginning
		beginningShift = str_getBeginningStripIndex(self.text, charset=BLANKS_EXTENDED)
		if beginningShift != 0:
			self.forward(beginningShift)
			self.text       = str_sub(self.text, start=beginningShift)
			self.startIndex = self.ctx.icontent.index

		#strip end
		endingIndex = str_getEndStripIndex(self.text, charset=BLANKS_EXTENDED)
		if endingIndex != -1 and endingIndex != len(self.text)-1:
			textLengthBefore = len(self.text)
			self.text        = str_sub(self.text, stop=endingIndex) #strip end of self.text
			self.stopIndex  -= textLengthBefore - len(self.text)    #shift stopIndex the same amount



	#debug output
	def textFormat(self):
		return '\"' + self.text.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n") + '\"'

	def toStr(self):
		return "{module:\"" + self.modulePrefix + "\",ctx:\"" + self.ctx.toStr() + "\",ctx.icontent.index:" + str(self.ctx.icontent.index) + ",startIndex:" + str(self.startIndex) + ",stopIndex:" + str(self.stopIndex) + ",text:" + self.textFormat() + ",pairs:\"" + str(self.pairs).replace(' ', '') + "\"}"

def newZCI(subCtxs, modulePrefix=None, pairs=None):
	if modulePrefix is None:
		modulePrefix = ""
	if pairs is None:
		pairs = {}
	if lst_isEmpty(subCtxs):
		print("[INTERNAL] Cannot instantiate a ZCI with no subCtxs.")
		exit(1)
	result = zci()
	result.subCtxs      = subCtxs
	result.ctx          = subCtxs[-1]
	result.pairs        = pairs
	result.modulePrefix = modulePrefix
	result.startIndex   = result.ctx.icontent.index #current position is where our ZCI starts
	result.stopIndex    = result.startIndex
	return result

def dumpZCIs(ZCIs, filename):
	output = "[\n"
	for ZCI in ZCIs:
		output += "\t" + ZCI.toStr() + ",\n"
	output += "]"
	writeFile(filename, output)



#types
class typ_commonDcnData: #common type data among every declination
	def __init__(self, dcnDeg):
		self.parent = None
		self.size   = 0
		self.dcnDeg = dcnDeg

		#stc related
		self.nature  = NATURE__PRIMITIVE
		self.fields  = None #lst[dataItem]
		self.stcSize = 0

class typ:
	def __init__(self):
		self.name          = None
		self.methods       = None #lst[fct]
		self.dcns          = None #tab[typ]
		self.commonDcnData = None #typ_commonDcnData

	def computeStcSize(self):
		if self.commonDcnData.nature != NATURE__PRIMITIVE:
			for f in self.commonDcnData.fields: #NOTE THAT HERE, WE DO SUM SIZES AND NOT STC-SIZES ! Structures contained inside another structure are always considered as pointers.
				self.commonDcnData.stcSize += f.Type.commonDcnData.size

def newTyp(name, dcnDeg=0, dcns=None, commonDcnData=None):
	if commonDcnData is None:
		commonDcnData = typ_commonDcnData(dcnDeg) #create a new commonDcnData by default (new type => new commonDcnData)
	result = typ()
	result.name          = name
	result.methods       = []   #lst[fct]
	result.dcns          = dcns #tab[typ]
	result.commonDcnData = commonDcnData #typ_commonDcnData
	return result

#scope
class scp:
	def __init__(self):
		self.exes      = None #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
		self.dataItems = None #lst[dataItem]
		self.parent    = None #scp

def newScp(parent=None):
	result = scp()
	result.exes      = [] #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
	result.dataItems = [] #lst[dataItem]
	result.parent    = parent
	return result






# -------- VAP RELATED --------

#value
class value:
	def __init__(self, Type, data, constant=False):
		self.Type     = Type
		self.data     = data  #atm #can be either a root type (literal), str (name) or call.
		self.constant = constant

	def toStr(self, depth=0):
		if self.data.id == ATM__BOO: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< I know, this seems weird in Python but it makes sens in Z (will have to be a swi btw)
			dataStr = "false"
			if self.data:
				dataStr = "true"

		#numerical
		elif self.data.id == ATM__S1:
			dataStr = 'S' + hexOnN(self.data.data, 2)
		elif self.data.id == ATM__U1:
			dataStr = 'U' + hexOnN(self.data.data, 2)
		elif self.data.id == ATM__S2:
			dataStr = 'S' + hexOnN(self.data.data, 4)
		elif self.data.id == ATM__U2:
			dataStr = 'U' + hexOnN(self.data.data, 4)
		elif self.data.id == ATM__S4:
			dataStr = 'S' + hexOnN(self.data.data, 8)
		elif self.data.id == ATM__U4:
			dataStr = 'U' + hexOnN(self.data.data, 8)
		elif self.data.id == ATM__S8:
			dataStr = 'S' + hexOnN(self.data.data, 16) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< no way to get arch type here... will stay in 64b for the moment (can be formatted again later)
		elif self.data.id == ATM__U8:
			dataStr = 'U' + hexOnN(self.data.data, 16)
		elif self.data.id == ATM__CHR:
			dataStr = '\'' + self.data.data + '\''
		elif self.data.id == ATM__STR: #this case covers both literal string & name. In all cases, toStr() will output a double-quoted result.
			dataStr = '\"' + self.data.data + '\"' #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< for the moment, it also covers the case of literal structures (stored under raw text)

		#common data structures (all stored as lst)
		elif self.data.id == ATM__LST:
			dataStr = '['
			for e in self.data.data:
				dataStr += e.toStr() + ','
			dataStr += ']'

		#calls
		elif self.data.id == ATM__CALL:
			depthSpace = '\t' * depth
			dataStr  = "\"call " + self.data.data.name + "(\n"
			for p in self.data.data.params:
				dataStr += depthSpace + '\t' + p.toStr(depth+1) + ',\n' #recursive call
			dataStr += depthSpace + ')'

		#invalid
		else:
			print("[INTERNAL] Invalid data stored inside value (can only be literal, name or call).")
			exit(1)
		return "{type:\"" + self.Type.name + "\",constant:" + str(self.constant) + ",data:" + dataStr + "}"



#calls
class call:
	def __init__(self, name, params):
		self.name   = name
		self.params = params #lst[value]

#"potential operator call" Same things as a call except we store only 2 params and under atm types.
#                          We expect to have only zci or POCall types for these atoms.
#                          This allows us to work with operator calls while parameters are not analyzed yet during progressive priorizing.
class POCall:
	def __init__(self, firstOperand, secondOperand):
		self.name          = None          #str, makes no sens to give a correct value on stc creation because we will set it depending on whether a next operand exists (so we don't know at creation time)
		self.operatorIndex = 0             #same thing
		self.firstOperand  = firstOperand  #atm
		self.secondOperand = secondOperand #atm

	def toStr(self, depth=0):
		depthSpacing = '\t' * depth

		#name
		nameStr = "null"
		if self.name is not None:
			nameStr = '"' + self.name + '"'

		#1st operand
		firstOperandText = "null"
		if self.firstOperand is not None:
			if self.firstOperand.id == ATM__ZCI:
				firstOperandText = self.firstOperand.data.textFormat()
			elif self.firstOperand.id == ATM__POCALL:
				firstOperandText = self.firstOperand.data.toStr(depth+1)

		#2nd operand
		secondOperandText = "null"
		if self.secondOperand is not None:
			if self.secondOperand.id == ATM__ZCI:
				secondOperandText = self.secondOperand.data.textFormat()
			elif self.secondOperand.id == ATM__POCALL:
				secondOperandText = self.secondOperand.data.toStr(depth+1)

		#final string
		return "{\n" + depthSpacing + "\tname:" + nameStr + ",\n" + depthSpacing + "\tfirstOperand:" + firstOperandText + ",\n" + depthSpacing + "\tsecondOperand:" + secondOperandText + "\n" + depthSpacing + "}"

class ODPResult:
	def __init__(self, maxStopIndex, mainPOCall):
		self.maxStopIndex = maxStopIndex
		self.mainPOCall   = mainPOCall

class opSeq:
	def __init__(self, stopIndex, operands, operators, operatorIndexes):
		self.stopIndex       = stopIndex
		self.operands        = operands  #lst[zci]
		self.operators       = operators #lst (lst[ubyt] cause enm will be stored)
		self.operatorIndexes = operatorIndexes

	def toStr(self):
		operandsText = ""
		for a in self.operands:
			operandsText += a.textFormat() + ','
		operatorsText = ""
		for o in self.operators:
			operatorsText += OPERATOR_NAMES[o] + ','
		return "{stopIndex:" + str(self.stopIndex) + ",operands:[" + operandsText + "],operators:[" + operatorsText + "]}"



#type for holding some VAP 2nd analysis information
class vap2:
	def __init__(self, ZCIKindIfError, scope, cstOnly):
		self.ZCIKindIfError = ZCIKindIfError
		self.scope          = scope
		self.cstOnly        = cstOnly



#dataItem
class dataItem:
	def __init__(self, Type, name, initialized, initialValue, constant=False, fields=None):
		self.Type         = Type
		self.name         = name
		self.initialized  = initialized
		self.initialValue = initialValue #value
		self.constant     = constant
		self.fields       = fields #lst[dataItem]

	def toStr(self):
		initialValueStr = "null"
		if self.initialValue is not None:
			initialValueStr = self.initialValue.toStr()
		typeStr = "null"
		if self.Type is not None:
			typeStr = '\"' + self.Type.name + '\"'
		fieldsText = "null"
		if self.fields is not None:
			fieldsText = "[\n"
			for f in self.fields:
				fieldsText += "\t" + f.toStr() + ",\n"
			fieldsText += "]"
		return "{type:" + typeStr + ",name:\"" + self.name + "\",initialized:" + str(self.initialized) + ",initialValue:" + initialValueStr + ",constant:" + str(self.constant) + ",fields:" + fieldsText + "}"






# -------- EXES --------

#assignment
class asg:
	def __init__(self, dst, src):
		self.dst = dst #dataItem or str (name only) ?
		self.src = src #value



#statements
class stm:
	def __init__(self):
		self.kind  = None
		self.scope = None

def newStm(kind, parentScope):
	result       = stm()
	result.kind  = kind
	result.scope = newScp(parent=parentScope)
	return result

class fct:
	def __init__(self):
		self.name    = None
		self.retType = None #typ
		self.params  = None #lst[dataItem]
		self.scope   = None









