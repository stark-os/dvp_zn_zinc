#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.string     import *
from std.path       import *
from std.list       import *
from std.io         import *
from std.parsingCtx import *
from std.int        import *

#charsets
import string






# -------- STD Z --------

#local-python version of atm
ATM__BOO  = 0
ATM__BYT  = 1
ATM__UBYT = 2
ATM__SHR  = 3
ATM__USHR = 4
ATM__INT  = 5
ATM__UINT = 6
ATM__LNG  = 7
ATM__ULNG = 8
ATM__CHR  = 9
ATM__STR  = 10
ATM__CALL     = 11
ATM__ZCI      = 12
ATM__VALUE    = 13
ATM__DATAITEM = 14
ATM__TYP      = 15
ATM__TYP_COMMONDATA = 16
ATM__SCP = 17
ATM__ASG = 18
ATM__STM = 19
ATM__FCT = 20
ATM__OPSEQ  = 21
ATM__POCALL = 22
ATM__LST = 23
ATM__ATM = 99
class atm:
	def __init__(self, id, data):
		self.id   = id   #ulng
		self.data = data #ulng





# -------- GENERAL --------

#general name parsing
NO_NAME            = -1
BLANK_AFTER_NAME   = -2
NOTHING_AFTER_NAME = -3

#root types
ROOT_TYPES = (
	"boo",
	"byt", "ubyt",
	"shr", "ushr",
	"int", "uint",
	"lng", "ulng",
	"flt", "dbl",
	"ptr"
)
RT__BOO  = 0 #enm #for indexing in zCtx.rootTypes
RT__BYT  = 1
RT__UBYT = 2
RT__SHR  = 3
RT__USHR = 4
RT__INT  = 5
RT__UINT = 6
RT__LNG  = 7
RT__ULNG = 8
RT__FLT  = 9
RT__DBL  = 10
RT__PTR  = 11

#common data structures (shortcut notations)
TYPE_FULLNAME_TAB  = "GUtab"
TYPE_FULLNAME_LST  = "GUlst"
TYPE_FULLNAME_FLY  = "GUfly"
TYPE_FULLNAME_FMAP = "GUfmap"
TYPE_FULLNAME_MMAP = "GUmmap"

#byte notations
BN_PREFIX = '`'

#Single Operators
SYMBOL__SIN  = 1 #invert
SYMBOL__SNO  = 2 #not
SO = (SYMBOL__SIN, SYMBOL__SNO)

#Decisionnal Operators
SYMBOL__DAN = 3 #decisionnal and
SYMBOL__DOR = 4 #decisionnal or
DO = (SYMBOL__DAN, SYMBOL__DOR)

#Arithmetic Operators
SYMBOL__AMU = 5 #multiply
SYMBOL__ADI = 6 #divide
SYMBOL__AMO = 7 #modulo
SYMBOL__APO = 8 #power
AO = (SYMBOL__AMU, SYMBOL__ADI, SYMBOL__AMO, SYMBOL__APO)

#B-rithmetic Operators
SYMBOL__BAD =  9 #add
SYMBOL__BSU = 10 #subtract
BO = (SYMBOL__BAD, SYMBOL__BSU)

#Logical Operators
SYMBOL__LAN = 11 #logical and
SYMBOL__LOR = 12 #logical or
SYMBOL__LXO = 13 #logical xor
SYMBOL__LLS = 14 #left shift
SYMBOL__LRS = 15 #right shift
SYMBOL__LLB = 16 #left byte-shift
SYMBOL__LRB = 17 #right byte-shift
SYMBOL__LLR = 18 #left roll
SYMBOL__LRR = 19 #right roll
LO = (
	SYMBOL__LAN, SYMBOL__LOR, SYMBOL__LXO,
	SYMBOL__LLS, SYMBOL__LRS,
	SYMBOL__LLB, SYMBOL__LRB,
	SYMBOL__LLR, SYMBOL__LRR
)

#Conditionnal Operators
SYMBOL__CEQ = 20 #equals
SYMBOL__CNE = 21 #not equals
SYMBOL__CLT = 22 #lesser than
SYMBOL__CGT = 23 #greater than
SYMBOL__CLE = 24 #lesser or equal
SYMBOL__CGE = 25 #greater or equal
CO = (
	SYMBOL__CEQ, SYMBOL__CNE,
	SYMBOL__CLT, SYMBOL__CGT,
	SYMBOL__CLE, SYMBOL__CGE
)

#Indexing Operators (without includers)
SYMBOL__IAM = 30 #among
SYMBOL__INA = 31 #not among
IO_AMONG = (SYMBOL__IAM, SYMBOL__INA)

#Fixed Operators
SYMBOL__FSZ = 32 #size
SYMBOL__FRF = 33 #reference
SYMBOL__FCA = 34 #casht
SYMBOL__FFA = 35 #field access

#mono-operand operators
MONO_OPERAND = SO + (SYMBOL__FSZ, SYMBOL__FRF)

#other
SYMBOL__ASG       = 1 #assignment
SYMBOL__NOT_FOUND = 0

#lengths
SYMBOL_LENGTHS = { #map[ubyt,ubyt]
	SYMBOL__SIN: 1, SYMBOL__SNO: 1, SYMBOL__DAN: 2, SYMBOL__DOR: 2,
	SYMBOL__AMU: 1, SYMBOL__ADI: 1, SYMBOL__AMO: 1, SYMBOL__APO: 2,
	SYMBOL__BAD: 1, SYMBOL__BSU: 1, SYMBOL__LAN: 1, SYMBOL__LOR: 1,
	SYMBOL__LXO: 1, SYMBOL__LLS: 2, SYMBOL__LRS: 2, SYMBOL__LLB: 3,
	SYMBOL__LRB: 3, SYMBOL__LLR: 3, SYMBOL__LRR: 3, SYMBOL__CEQ: 2,
	SYMBOL__CNE: 2, SYMBOL__CLT: 1, SYMBOL__CGT: 1, SYMBOL__CLE: 2,
	SYMBOL__CGE: 2, SYMBOL__IAM: 2, SYMBOL__INA: 3, SYMBOL__FSZ: 1,
	SYMBOL__FRF: 1, SYMBOL__FCA: 1, SYMBOL__FFA: 1, SYMBOL__ASG: 1,
	SYMBOL__NOT_FOUND: 0
}
OPERATOR_NAMES = {
	SYMBOL__SIN: "sin", SYMBOL__SNO: "sno", SYMBOL__DAN: "dan", SYMBOL__DOR: "dor",
	SYMBOL__AMU: "amu", SYMBOL__ADI: "adi", SYMBOL__AMO: "amo", SYMBOL__APO: "apo",
	SYMBOL__BAD: "bad", SYMBOL__BSU: "bsu", SYMBOL__LAN: "lan", SYMBOL__LOR: "lor",
	SYMBOL__LXO: "lxo", SYMBOL__LLS: "lls", SYMBOL__LRS: "lrs", SYMBOL__LLB: "llb",
	SYMBOL__LRB: "lrb", SYMBOL__LLR: "llr", SYMBOL__LRR: "lrr", SYMBOL__CEQ: "ceq",
	SYMBOL__CNE: "cne", SYMBOL__CLT: "clt", SYMBOL__CGT: "cgt", SYMBOL__CLE: "cle",
	SYMBOL__CGE: "cge", SYMBOL__IAM: "iam", SYMBOL__INA: "ina", SYMBOL__FSZ: "fsz",
	SYMBOL__FRF: "frf", SYMBOL__FCA: "fca", SYMBOL__FFA: "ffa"
}
FO_NAMES = (
	OPERATOR_NAMES[SYMBOL__FSZ], OPERATOR_NAMES[SYMBOL__FRF],
	OPERATOR_NAMES[SYMBOL__FCA], OPERATOR_NAMES[SYMBOL__FFA]
)

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DEFAULT_NAME_CHARSET            = tuple(string.ascii_letters + string.digits + '_')
ZCI_FIRSTWORD_DETECTION_CHARSET = BLANKS + tuple(INCLUDERS.keys())
FCT_NAME_CHARSET                = DEFAULT_NAME_CHARSET + ('.', '[', ']', '=', '-', '+', '*', '/', '^', '%', '[', ':', '~', '!', '?', '&', '|', '<', '>')
VALUE_CHARSET                   = FCT_NAME_CHARSET + ZCI_FIRSTWORD_DETECTION_CHARSET + ('@', '#', '$') #additionnal FO

#option to be defined in src/main.z
deepDebug_stepByStep = False #should be a global VARIABLE dataitem

#cpl opt set
CPL_OPT_VALUES__ARCHT = 0 #architecture type
CPL_OPT_VALUES__ONOFF = 1
CPL_OPT_VALUES__DIGIT = 2
CPL_OPT_VALUES__RTYPE = 3 #root type
CPL_OPT_ALLOWED = {
	"ARCH":                           CPL_OPT_VALUES__ARCHT,
	"INTERPRET_COMMON_STRUCTURES":    CPL_OPT_VALUES__ONOFF,
	"MAX_INSTRUCTS_NOFUNCTION":       CPL_OPT_VALUES__DIGIT,
	"CHECK_NULL_STC_BEFORE_METHOD":   CPL_OPT_VALUES__ONOFF,
	"OPERATORS_SUPPORTS_INHERITANCE": CPL_OPT_VALUES__ONOFF,
	"METHODS_SUPPORTS_INHERITANCE":   CPL_OPT_VALUES__ONOFF,
	"EMPTY_DATA_ITEM_NULL":           CPL_OPT_VALUES__ONOFF,
	"UNDECLINATED_IMPLICITSOURCE":    CPL_OPT_VALUES__RTYPE,
	"LS_CNT_DIGITS":                  CPL_OPT_VALUES__DIGIT
}

#data item nature
NATURE__PRIMITIVE = 0
NATURE__STRUCTURE = 1
NATURE__ENUMERATE = 2

#statement kinds
STM__IF_ = 0
STM__FOR = 1
STM__WHI = 2
STM__SWI = 3

#pcpl items
PCPL_ITEM_NAME_CHARSET = DEFAULT_NAME_CHARSET #no link, but same value






# -------- TEXT TOOLS --------

#unprefixing module prefixes especially
def unprefixizeModule(modulePrefix):
	if len(modulePrefix) == 0:
		return ""
	if modulePrefix[0] == 'G':
		return ""
	return "^" + str_sub(modulePrefix, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1] + '.'

def extractModulePrefix(name):
	if len(name) == 0:
		return ""
	if name[0] != 'M': #no module prefix
		return ""

	#get only module prefix from name
	modulePrefix    = "M"
	foundUnderscore = False
	for c in name[1:]:

		#previous character was an underscore => potential end of module prefix
		if foundUnderscore:
			foundUnderscore = False

			#- double underscore => regular text, ignore it
			#- end of module prefix, but another one follows => still in it
			#else => definitely out of module prefix
			if c != '_' and c != 'M':
				break

		#previous character was not an underscore => we are in module prefix, sure at 100%
		elif c == '_':
			foundUnderscore = True

		#in module prefix
		modulePrefix += c

	#count ending underscores
	uNbr = 0
	modulePrefix_length = len(modulePrefix)
	for c in range(modulePrefix_length):
		if modulePrefix[modulePrefix_length-c-1] == '_':
			uNbr += 1
		else:
			break

	#error case : should never occur. It would mean we made s-thing wrong when transforming module notation into module prefix
	if uNbr%2 == 0:
		print("[INTERNAL] Invalid module prefix '" + modulePrefix + "' extracted from name '" + name + "' (ending with even number of underscores).")
		exit(1)
	return modulePrefix

#unprefixing anything <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE MAKE IT EFFICIENT ENOUGH SO THAT WE CAN GET RID OF UNPREFIXIZEMODULE & EXTRACTMODULEPREFIX ?
def unprefixizeAnyName(name): #GE<name> => <name>, M<mod>_E<name> => ^<mod>.<name>, ...
	prefix = extractModulePrefix(name)
	return unprefixizeModule(prefix) + str_sub(name, len(prefix)).replace("__", '_')

#def extractAnyPrefix()
#	return





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
				self.commonDcnData.stcSize += f.type.commonDcnData.size

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
		self.type     = Type
		self.data     = data  #atm #can be either a root type (literal), str (name) or call.
		self.constant = constant

	def toStr(self, depth=0):
		if self.data.id == ATM__BOO: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< I know, this seems weird in Python but it makes sens in Z (will have to be a swi btw)
			dataStr = "false"
			if self.data:
				dataStr = "true"

		#numerical
		elif self.data.id == ATM__BYT:
			dataStr = 'S' + hexOnN(self.data.data, 2)
		elif self.data.id == ATM__UBYT:
			dataStr = 'U' + hexOnN(self.data.data, 2)
		elif self.data.id == ATM__SHR:
			dataStr = 'S' + hexOnN(self.data.data, 4)
		elif self.data.id == ATM__USHR:
			dataStr = 'U' + hexOnN(self.data.data, 4)
		elif self.data.id == ATM__INT:
			dataStr = 'S' + hexOnN(self.data.data, 8)
		elif self.data.id == ATM__UINT:
			dataStr = 'U' + hexOnN(self.data.data, 8)
		elif self.data.id == ATM__LNG:
			dataStr = 'S' + hexOnN(self.data.data, 16) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< no way to get arch type here... will stay in 64b for the moment (can be formatted again later)
		elif self.data.id == ATM__ULNG:
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
class VAP2:
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



#functions
class fct:
	def __init__(self):
		self.name    = None
		self.retType = None #typ
		self.params  = None #lst[dataItem]
		self.scope   = None




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
		self.textResult  = ""

def newCplDat(options, rootTypes):
	result = cplDat()
	result.options = options

	#z abstract elements
	result.modulePrefixes = [] #lst[str]
	result.types          = lst_copy(rootTypes) #lst[typ]
	result.globalScope    = newScp()
	result.functions      = [] #lst[fct]
	result.linkedLibs     = [] #lst[]

	#program concrete elements
	#result.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
	return result



#imp zctx




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



#look for data item in given scope
def getDataItem(name, scope):

	#look for dataItem in current scope first
	for di in scope.dataItems:
		if name == di.name:
			return di

	#look for dataItem in parent scope
	if scope.parent is not None:
		return getDataItem(name, scope.parent)

	#not found even after scanning global scope => unknown
	return None







#each cpl option must be defined
def checkCplOpt(self, cpl_opt):

	#check each required option
	for o in CPL_OPT_ALLOWED.keys():

		#option must be defined
		if o not in cpl_opt:
			self.error("Missing compilation option \"" + o + "\" in configuration file cpl_opt.cfg.")

		#check value: ARCH type
		if CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__ARCHT:
			if cpl_opt[o] not in ("32", "64"):
				self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (32 or 64 expected)")

		#check value: ON / OFF
		elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__ONOFF:
			if cpl_opt[o] not in ("ON", "OFF"):
				self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (ON or OFF expected)")

		#check value: integer
		elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__DIGIT:
			if not str_isConvertible_int(cpl_opt[o]):
				self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (integer expected)")

		#check value: root type
		elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__RTYPE:
			if cpl_opt[o] not in ROOT_TYPES:
				self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (root type expected among " + ", ".join(ROOT_TYPES) + ")")

	#check for additionnal options (not allowed)
	if len(cpl_opt) > len(CPL_OPT_ALLOWED):
		for o in cpl_opt.keys():
			if o not in CPL_OPT_ALLOWED.keys():
				self.error("Unknown compilation option \"" + o + "\".")



	#output
	def internal(self, msg, printSubCtxs=True, printLine=True):
		print("[INT ERR] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to internal-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)

	def error(self, msg, printSubCtxs=True, printLine=True):
		print("[ ERROR ] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to error-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()
		exit(1)

	def warning(self, msg, printSubCtxs=True, printLine=True):
		print("[WARNING] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to warning-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()

	def debug(self, msg, printSubCtxs=False, printLine=False):
		if self.debugMode:
			print("[ DEBUG ] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if self.ctx is None:
					self.internal("No context to debug-output line from.", printSubCtxs=False, printLine=False)
				self.ctx.printLineIndicator()

	def deepDebug(self, msg, printSubCtxs=False, printLine=False):
		if self.deepDebugMode:
			print("[D-DEBUG] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if self.ctx is None:
					self.internal("No context to deep-debug-output line from.", printSubCtxs=False, printLine=False)
				self.ctx.printLineIndicator()

	def deepDebugPause(self):
		if self.deepDebugMode and deepDebug_stepByStep:
			print("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~", end="")
			input()
			print(Term__CUU1 + "                                       \r", end="")



#imp parsing






	# PARSING

	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)



	# SUBCONTEXTS

	#file contexts return true if successfully openned (false means : file already processed => ignoring it)
	def openNewSubCtx(self, filepath):
		if not filepath.endswith(".z"):
			filepath += ".z"

		#resolve relativeness of given filepath regarding current context location
		if not filepath.startswith('/'):
			filepath = self.ctx.dirname + '/' + filepath

		#check already openned
		realNewPath = os.path.realpath(filepath)
		for c in self.imported:
			if realNewPath == c:
				self.deepDebug("Subctx \"" + realNewPath + "\" already openned once => skipping it.")
				return False

		#open new subcontext
		self.deepDebug("Opening subctx \"" + filepath + "\".")
		try:
			newCtx   = ParsingCtx(filepath, readFile(filepath))
		except FileNotFoundError:
			self.error("File " + filepath + " not found.")
		except IsADirectoryError:
			self.error("Element " + filepath + " is a directory (expected file).")

		#not already openned => add it to importations
		self.ctx = newCtx
		self.subCtxs.append(newCtx)
		self.imported.append(realNewPath)
		return True

	def closeCurrentCtx(self): #return True if no more context remains
		self.deepDebug("Closing latest subctx.")
		lst_pop(self.subCtxs)

		#no more subcontext remaining
		if lst_isEmpty(self.subCtxs):
			self.ctx = None
			self.deepDebug("No more subctx remaining.")
			return True

		#subcontexts remaining
		self.deepDebug("Back here:", printSubCtxs=True)
		self.ctx = lst_last(self.subCtxs)
		return False

	def overwriteSubCtxs(self, subCtxs):
		self.subCtxs = subCtxs
		if lst_isEmpty(subCtxs):
			self.ctx = None
		else:
			self.ctx = subCtxs[-1]



	# ZCI OUTPUT (cpl)

	#output after precompilation is closely related to ZCIs, no longer to global subCtxs
	def ZCIInternal(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.internal(msg, printSubCtxs, printLine)

	def ZCIError(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.error(msg, printSubCtxs, printLine)

	def ZCIWarning(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.warning(msg, printSubCtxs, printLine)

	def ZCIDebug(self, ZCI, msg, printSubCtxs=False, printLine=True):
		previousSubCtxs = self.subCtxs
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.debug(msg, printSubCtxs, printLine)
		self.overwriteSubCtxs(previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)

	def ZCIDeepDebug(self, ZCI, msg, printSubCtxs=False, printLine=True):
		previousSubCtxs = self.subCtxs
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.deepDebug(msg, printSubCtxs, printLine)
		self.overwriteSubCtxs(previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)
# DEBUG

	#modules
	def debugModules(self):
		unprefixedModules = ""
		for mp in self.cpl.modulePrefixes:
			unprefixedModules += "\n - " + unprefixizeModule(mp)
		self.debug("Available modules are :" + unprefixedModules)

	#cpl steps output
	def cplStep_debugZCIs(self, cplStep):
		if self.debugMode:
			dumpZCIs(self.ZCIs, "debug/" + path_name(self.initialCtx.filename) + ".c" + cplStep + ".json")




	# GENERAL PARSING TOOLS

	#move ctx cursor just before the first non-blank character found
	def jumpBlankZone(self, ZCI, missingFieldIfError, blanks=BLANKS): #!WARNING: we MUST be on a blank character before calling that function
		while not ZCI.inc():
			if ZCI.get() not in blanks:
				return
		if missingFieldIfError is not None:
			self.ZCIError(ZCI, "Expected something after blank zone: " + missingFieldIfError)

	def optionnalBlanks(self, ZCI, missingFieldIfError, blanks=BLANKS):
		if ZCI.get() in blanks:
			self.jumpBlankZone(ZCI, missingFieldIfError, blanks=blanks)

	def endOfZCI(self, ZCI, ZCIKindIfError):
		if not ZCI.reachedEnd():
			self.ZCIError(ZCI, "Too much elements in " + ZCIKindIfError + " Should stop here.")






	# REAL ZCE PARSING TOOLS (bare metal syntax-related)

	#read hexadecimal byte
	def readHexByte(self, ZCI):

		#read & check 1st digit
		h1 = ZCI.get()
		if h1 not in HEX_DIGITS_LOWERCASE:
			self.ZCIError(ZCI, "Invalid first hexadecimal digit '" + h1 + "' given in byte notation.")

		#read & check 2nd digit
		if ZCI.inc():
			self.ZCIError(ZCI, "Missing second hexadecimal digit in byte notation.")
		h0 = ZCI.get()
		if h0 not in HEX_DIGITS_LOWERCASE:
			self.ZCIError(ZCI, "Invalid second hexadecimal digit '" + h0 + "' given in byte notation.")

		#return byte
		return hex_toByt(h1, h0)



	#try reading symbol (don't move ZCI ctx)
	def readSymbol(self, ZCI):
		self.ZCIDeepDebug(ZCI, "Reading symbol.")
		tmpZCI = ZCI.copy()
		c1 = tmpZCI.get()

		#1-character symbol
		if c1 == '~':
			return SYMBOL__SIN
		elif c1 == '/':
			return SYMBOL__ADI
		elif c1 == '+':
			return SYMBOL__BAD
		elif c1 == '%':
			return SYMBOL__AMO
		elif c1 == '^':
			return SYMBOL__LXO
		elif c1 == '#':
			return SYMBOL__FSZ
		elif c1 == '@':
			return SYMBOL__FRF
		elif c1 == '$':
			return SYMBOL__FCA
		elif c1 == '.':
			return SYMBOL__FFA

		#multi-character symbol: starting with '!'
		elif c1 == '!':
			tmpZCI.inc()
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CNE
			elif c2 == '?':
				return SYMBOL__INA
			return SYMBOL__SNO

		#multi-character symbol: starting with '*'
		elif c1 == '*':
			if tmpZCI.inc():
				return SYMBOL__AMU
			if tmpZCI.get() == '*':
				return SYMBOL__APO
			return SYMBOL__AMU

		#multi-character symbol: starting with '&'
		elif c1 == '&':
			self.ZCIDeepDebug(tmpZCI, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + tmpZCI.toStr())
			if tmpZCI.inc():
				return SYMBOL__LAN #ending with lonely '&'
			if tmpZCI.get() == '&':
				return SYMBOL__DAN
			return SYMBOL__LAN

		#multi-character symbol: starting with '|'
		elif c1 == '|':
			tmpZCI.inc()
			c2 = tmpZCI.get()
			if c2 == '|':
				return SYMBOL__DOR
			elif c2 == '<':
				if tmpZCI.inc():
					return SYMBOL__LOR
				if tmpZCI.get() == '<':
					return SYMBOL__LLB
			return SYMBOL__LOR

		#multi-character symbol: starting with '-'
		elif c1 == '-':
			tmpZCI.inc()
			if tmpZCI.get() == '>':
				if tmpZCI.inc():
					return SYMBOL__BSU
				if tmpZCI.get() == '>':
					return SYMBOL__LRR
			return SYMBOL__BSU

		#multi-character symbol: starting with '<'
		elif c1 == '<':
			if tmpZCI.inc():
				return SYMBOL__CLT
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CLE
			elif c2 == '<':
				if tmpZCI.inc():
					return SYMBOL__LLS
				if tmpZCI.get() == '-':
					return SYMBOL__LLR
				return SYMBOL__LLS
			return SYMBOL__CLT

		#multi-character symbol: starting with '>'
		elif c1 == '>':
			if tmpZCI.inc():
				return SYMBOL__CGT
			c2 = tmpZCI.get()
			if c2 == '=':
				return SYMBOL__CGE
			elif c2 == '>':
				if tmpZCI.inc():
					return SYMBOL__LRS
				if tmpZCI.get() == '|':
					return SYMBOL__LRB
				return SYMBOL__LRS
			return SYMBOL__CGT

		#multi-character symbol: starting with '='
		elif c1 == '=':
			if tmpZCI.inc():
				return SYMBOL__ASG
			if tmpZCI.get() == '=':
				return SYMBOL__CEQ
			return SYMBOL__ASG

		#multi-character symbol: starting with '?'
		elif c1 == '?':
			return SYMBOL__IAM

		#no match
		return SYMBOL__NOT_FOUND



	#read a name according to the given charset (either blacklist or whitelist)
	# IMPORTANT : Reading ctx from its CURRENT position and move it right AFTER the extracted result
	#also, blacklist is prioritary : if null => use whitelist, else, use it (no matter whitelist value)
	#
	# /!\ This method must be included in STDZ into ^Parsing.ctx whithout the module prefix part.
	#     Must also include the first 2 lines of comment over it
	#
	def readName(self,
		ZCI,
		missingFieldIfError, #null means "don't raise error if empty"
		blacklist=None, whitelist=DEFAULT_NAME_CHARSET,
		doubleUnderscores=False,
		parseModulePrefixes=False,
		modulePrefix_asHeaderOnly=False #means "if any, it must BEGIN with it and be the only occurrence"
	):
		self.ZCIDeepDebug(ZCI, "Reading name.")
		if parseModulePrefixes:
			doubleUnderscores = True #doesn't make sens to double underscores in module prefixes but not in the name => force it

		#read until given blacklist/whitelist no longer matches
		name           = ""
		firstCharacter = True
		while True:
			if not firstCharacter: #skip ZCI.inc() for first character only
				if ZCI.inc():
					break
			c = ZCI.get()



			# I] MODULE PREFIX PARSING

			#module prefix detection
			if parseModulePrefixes and c == '^':
				modules           = []
				currentModuleName = ""

				#only allowing it as name header
				if modulePrefix_asHeaderOnly and not firstCharacter:
					self.ZCIError(ZCI, "Module prefixes only allowed at beginning of name here.")



				# I.1) EXTRACTING MODULE NAMES

				#read module names until the end
				while not ZCI.inc():
					c = ZCI.get() #always using the same 'c'

					#end of current module name
					if c == '.':
						modules.append(currentModuleName)
						currentModuleName = ""

						#can't continue ? => ending ZCI text without giving the module element to target
						if ZCI.inc():
							zCtx.ZCIError(ZCI, "Missing an element name to target inside that module (reached end of ZCI)")

						#chaining with another module name (potentially) => continue in the same loop, else => break here, we reached our next "name" character
						c = ZCI.get()
						if c == '^':
							continue
						else:
							break

					#doubling underscores
					if c == '_':
						currentModuleName += '_'

					#not part of module name => break here, that one is the next "name" character actually
					if c not in DEFAULT_NAME_CHARSET:
						break

					#part of module name
					currentModuleName += c



				# I.2) SOLVE THEM

				#unfinished module name access
				if len(currentModuleName) != 0:
					self.ZCIError(ZCI, "Missing ending dot delimiter '.' when targetting something from module.")

				#there was no module names actually, it was just a lonely '^' => do as nothing happened
				if len(modules) == 0:
					name += '^'

				#at least one module name => add it to name
				else:

					#resolve implicit module naming
					for m in range(len(modules)):
						if len(modules[m]) == 0:
							if len(ZCI.modulePrefix) == 0:
								self.ZCIError(ZCI, "Can't resolve implicit module prefix, we are outside of any module.")
							modules[m] = ZCI.modulePrefix

					#add module prefix to our name
					name += 'M' + "_M".join(modules) + '_'

				#reached end of ZCI => regular end of name
				if ZCI.reachedEnd():
					break



			# II] STORE IN NAME OR STOP

			#stopping condition
			if blacklist is None:
				if c not in whitelist:
					break
			elif c in blacklist:
				break

			#allowed character => add it
			name += c
			if doubleUnderscores and c == '_':
				name += '_'

			#no longer in first character (maybe, getting rid of the "if" and keeping only the assignment would be more optimized ?)
			if firstCharacter:
				firstCharacter = False
		self.ZCIDeepDebug(ZCI, "Ended reading name.")

		#missing name field
		if len(name) == 0:
			if missingFieldIfError is None:
				return ""
			self.ZCIError(ZCI, "Missing or invalid name : " + missingFieldIfError)

		#return result
		return name



	def tryReadDataItemIncludingFields(self, ZCI, scope):
		di = getDataItem(
			self.readName(ZCI, "Any data item name", parseModulePrefixes=True, modulePrefix_asHeaderOnly=True),
			scope
		)

		#we may find some additionnal fields
		while ZCI.get() == '.':
			fieldName = self.readName(ZCI, "Field from data item " + unprefixizeModule() + "." + di.name)

			#found a field with that name in our dataItem
			fieldFound = None
			for f in di.fields:
				if f.name == fieldName:
					fieldFound = f
					break
			if fieldFound is None:
				self.ZCIError(ZCI, "Data item " + di.name + " has no field " + fieldName)

		#return result
		return di




	# ABSTRACT ZCEs PARSING TOOLS

	#expecting a Z type
	def readType(self, ZCI, ZCIKindIfError, nullIfNotExisting=False):
		self.ZCIDeepDebug(ZCI, "Reading type.")
		initialZCICtx = ZCI.ctx.copy()

		#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
		tRawName = self.readName(ZCI, "Type name in " + ZCIKindIfError, parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)

		#module-realted / global
		if initialZCICtx.get() == '^':
			tModulePrefix = self.splitModulePrefix(tRawName)            #save its module prefix elsewhere
			tRawName      = str_sub(tRawName, start=len(tModulePrefix)) # + cut it from "rawName" to keep only the REAL RAW NAME
		else:
			tModulePrefix = "G"

		#build full type name (forced "undeclinated" for the moment)
		tFullName = tModulePrefix + 'U' + tRawName

		#1 - check UNDECLINATED variant existence
		tInstance = self.getType(tFullName)
		if tInstance is None:
			if nullIfNotExisting:
				self.ZCIDeepDebug(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", printLine=False)
				ZCI.resetCtx(initialZCICtx)
				self.ZCIDeepDebug(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
				return None
			self.ZCIError(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " does not exist.")
		self.ZCIDeepDebug(ZCI, "Undeclinated type \"" + tFullName + "\" targetted.")

		#2 - declination list given => solve them
		if ZCI.get() == '[':
			initialIndex = ZCI.ctx.icontent.index
			peerIndex    = ZCI.pairs[initialIndex]
			ZCI.inc()

			#undeclinable type
			if tInstance.commonDcnData.dcnDeg == 0:
				self.ZCIError(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " is not declinable (null declination degree).")

			#read declination types one by one
			self.deepDebug("Type is declinated, reading declination types.")
			dcns = [] #lst[typ]
			while True:
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

				#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
				dcns.append(self.readType(ZCI, ZCIKindIfError))

				#must be followed by coma or closing peer
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
				next = ZCI.get()
				if next == ']':
					if ZCI.ctx.icontent.index != peerIndex:
						self.ZCIInternal(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(peerIndex) + ").")
					ZCI.inc()
					break
				elif next != ',':
					self.ZCIError(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']').")
				ZCI.inc()

			#debug
			self.ZCIDeepDebug(ZCI, "Found declination types [", printLine=False)
			for d in range(len(dcns)):
				self.ZCIDeepDebug(ZCI, "\t" + dcns[d].name + ",", printLine=False)
			self.ZCIDeepDebug(ZCI, "].", printLine=False)

			#check declination length
			if len(dcns) < tInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")
			elif len(dcns) > tInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")

			#re-build full type name including declinations this time (tModulePrefix can be set to "G" by the way, same logic as undeclinated types)
			tFullName = tModulePrefix + 'D' + tRawName
			for d in dcns:
				tFullName += '_' + d.name

			#check for that declination in currently declared types
			tUndeclinatedInstance = tInstance
			tInstance             = self.getType(tFullName)

			#not found => create that declination (this new combination must exist)
			if tInstance is None:
				tInstance      = newTyp(tFullName, commonDcnData = tUndeclinatedInstance.commonDcnData) #share the same commonDcnData (affecting the undeclinated instance will affect every declination)
				tInstance.dcns = dcns
				self.ZCIDebug(ZCI, "First call of declination \"" + tInstance.name + "\" from type \"" + tUndeclinatedInstance.name + "\", adding it.")
				self.cpl.types.append(tInstance)

		#final result
		self.ZCIDeepDebug(ZCI, "Ended reading type.")
		return tInstance




	#ODP
	def ODP_readAndSplitByOperators(self, ZCI, allowedOperators):
		maxStopIndex         = 0
		allowedOperatorsText = "" #only for deep debug

		#deep debug
		if self.deepDebugMode:
			allowedOperatorsText = "["
			for o in allowedOperators:
				allowedOperatorsText += OPERATOR_NAMES[o] + ','
			allowedOperatorsText += "]"
			self.ZCIDeepDebug(ZCI, "ODP-1: Reading & splitting ZCI content " + ZCI.textFormat() + " by operators " + allowedOperatorsText)

		#split by operator symbols
		operands          = [] #lst[zci]
		operators         = [] #lst (certainly ubyt but prefer using only undeclinated for enm storage)
		operatorIndexes   = []
		operandInitialCtx = ZCI.ctx.copy()
		while not ZCI.reachedEnd() and ZCI.get() in VALUE_CHARSET:



			#checking for symbol
			operator = self.readSymbol(ZCI)

			#CASE 1: not a symbol (that can be anything and especially an includer)
			if operator == SYMBOL__NOT_FOUND:
				if ZCI.ctx.icontent.index in ZCI.pairs.keys():
					ZCI.forward(ZCI.pairs[ZCI.ctx.icontent.index] - ZCI.ctx.icontent.index) #includer? It also belongs to the operand no matter what's inside => skip parsing its content
				ZCI.inc()
				continue

			#CASE 2: '^'
			elif operator == SYMBOL__LXO:
				if ZCI.ctx.icontent.index >= ZCI.stopIndex:
					ZCI.inc()
					self.ZCIError(ZCI, "Missing second operand to logical XOR operator (LXO, \"^\"), reached end of ZCI.")

				#look at the following character to determine whether it is a module prefix or a regular LXO operator
				nextChr = ZCI.ctx.icontent.s[ZCI.ctx.icontent.index+1]
				if nextChr == '.' or nextChr in DEFAULT_NAME_CHARSET:
					self.ZCIDeepDebug(ZCI, "ODP-1: '^' symbol detected as module prefix and not as LXO operator.")
					ZCI.inc() #not an operator actually => skipping it
					continue

			#CASE 3: it is a symbol but not allowed
			if operator not in allowedOperators:
				ZCI.forward(SYMBOL_LENGTHS[operator])
				continue



			#create operand as a unique ZCI.
			# This is actually a value to be analyzed in further steps.
			# However, to parse it easilly, we store it as a fragment of the original ZCI (which is, here, a copy of the original but doesn't matter).
			operand            = ZCI.copy(ctxCopy=operandInitialCtx)
			operand.startIndex = operandInitialCtx.icontent.index #initial context must be at operand beginning index
			operand.stopIndex  = ZCI.ctx.icontent.index-1         #we are just before operator index, so at operand end index
			operand.strip()

			#empty operand
			operandIsEmpty = (ZCI.ctx.icontent.index == operandInitialCtx.icontent.index)
			if operator in MONO_OPERAND:
				if not operandIsEmpty:
					self.ZCIError(ZCI, "Got too much operands for single operator " + OPERATOR_NAMES[operator] + " (only 1 allowed after symbol).")
			else:
				if operandIsEmpty:
					self.ZCIError(ZCI, "Missing first operand to operator " + OPERATOR_NAMES[operator])

			#store operand & operator
			operands.append(operand)
			operators.append(operator)
			operatorIndexes.append(ZCI.ctx.icontent.index)
			self.ZCIDeepDebug(ZCI, "ODP-1: New operator " + OPERATOR_NAMES[operator] + " found, current operating sequence is " + opSeq(ZCI.ctx.icontent.index, operands, operators, operatorIndexes).toStr())

			#moving after symbol
			ZCI.forward(SYMBOL_LENGTHS[operator])

			#prepare next operand
			operandInitialCtx = ZCI.ctx.copy()

		#set maxStopIndex
		maxStopIndex = ZCI.ctx.icontent.index - 1

		#no operator found at all => not an operating sequence => return as it was an operating sequence with no operator and only one operand
		if len(operators) == 0:
			self.ZCIDeepDebug(ZCI, "ODP-1: No operator found at all => Finished with null operating sequence.")
			return opSeq(maxStopIndex, None, None, None)

		#last operand cannot be empty
		if ZCI.ctx.icontent.index == operandInitialCtx.icontent.index:
			lastOperator = operators[-1]
			if lastOperator in MONO_OPERAND:
				self.ZCIError(ZCI, "Missing first (and only) operand to single operator " + OPERATOR_NAMES[lastOperator])
			else:
				self.ZCIError(ZCI, "Missing second operand to operator " + OPERATOR_NAMES[lastOperator])

		#create last operand
		operand            = ZCI.copy(ctxCopy=operandInitialCtx)
		operand.startIndex = operandInitialCtx.icontent.index
		operand.stopIndex  = ZCI.ctx.icontent.index - 1
		operand.strip()

		#add last operand
		operands.append(operand)
		self.ZCIDeepDebug(ZCI, "ODP-1: Last operand added, final operating sequence is " + opSeq(maxStopIndex, operands, operators, operatorIndexes).toStr())

		#deep debug
		self.ZCIDeepDebug(ZCI, "ODP-1: Finished reading & splitting ZCI content " + ZCI.textFormat() + " by operators " + allowedOperatorsText)
		return opSeq(maxStopIndex, operands, operators, operatorIndexes)



	#progressive priorizing equivalent for mono operand operators
	def monoOperandOpSeqConcatenation(self, currentOpSeq):
		lastOperand = currentOpSeq.operands.pop()

		#check other operands (not necessary, internal consistency check only)
		for a in currentOpSeq.operands:
			if a.stopIndex - a.startIndex >= 0:
				self.internal("Non-empty operand found in mono-operand operating sequence (last element excepted).")

		#deep debug: before
		self.deepDebug("ODP-2: Applying mono-operand operating sequence concatenation on " + currentOpSeq.toStr())

		#associate each operand to its operator
		result = POCall(
			None,
			atm(ATM__ZCI, lastOperand)
		)
		current = result
		while len(currentOpSeq.operators) != 0:
			current.name          = OPERATOR_NAMES[currentOpSeq.operators.pop(0)]
			current.operatorIndex = currentOpSeq.operatorIndexes.pop(0)
			current.secondOperand = atm(
				ATM__POCALL,
				POCall(
					None,
					current.secondOperand
				)
			)
			current = current.secondOperand.data

		#deep debug: after
		self.deepDebug("ODP-2: Mono-operand operating sequence concatenation resulted into the following POCall " + result.toStr())
		return result



	#transform an operating sequence into a single POCall (destroying the given opSeq!)
	def progressivePriorizing(self, currentOpSeq, monoOperand): #WARNING! DO NOT USE WITH SO !!!
		if len(currentOpSeq.operands) == 0:
			self.internal("Got no operand in operating sequence when running progressive priorizing.")

		#mono-operand operating sequence => redirect to the adapted equivalent
		if monoOperand:
			return self.monoOperandOpSeqConcatenation(currentOpSeq)

		#deep debug: before
		self.deepDebug("ODP-2: Applying progressive priorizing on operating sequence " + currentOpSeq.toStr())

		#first element (we must keep track of it)
		result = POCall(
			None,
			atm(ATM__ZCI, currentOpSeq.operands.pop())
		)
		current = result

		#for each remaining operand, make function calls (Potential Operator Call)
		while len(currentOpSeq.operands) != 0:
			current.name          = OPERATOR_NAMES[currentOpSeq.operators.pop()]
			current.operatorIndex = currentOpSeq.operatorIndexes.pop()
			current.firstOperand = atm(
				ATM__POCALL,
				POCall(
					None,
					atm(ATM__ZCI, currentOpSeq.operands.pop())
				)
			)
			current = current.firstOperand.data

		#deep debug: after
		self.deepDebug("ODP-2: Progressive priorizing resulted into the following POCall " + result.toStr())
		return result



	#group priorizing
	# This function is higly important! It applies group priorization on every value that can be found in a POCall.
	def ODP_applyGroupPriorization(self, maxStopIndex, currentPOCall, operatorsAllowed, monoOperand=False):

		#1st operand
		if currentPOCall.firstOperand is not None:

			#leaf => apply here
			if currentPOCall.firstOperand.id == ATM__ZCI:
				originalCtx  = currentPOCall.secondOperand.data.ctx.copy()
				currentOpSeq = self.ODP_readAndSplitByOperators(currentPOCall.firstOperand.data, operatorsAllowed)

				#no operator found => restore original ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
				if currentOpSeq.operators is None:
					currentPOCall.firstOperand.data.resetCtx(originalCtx)
					currentPOCall.firstOperand.data.stopIndex = currentOpSeq.stopIndex
					currentPOCall.firstOperand.data.strip()

				#operator found => progressive priorizing
				else:
					currentPOCall.firstOperand = atm(
						ATM__POCALL,
						self.progressivePriorizing(currentOpSeq, monoOperand)
					)

				#update maxStopIndex
				if maxStopIndex < currentOpSeq.stopIndex:
					maxStopIndex = currentOpSeq.stopIndex

			#tree => check deeper
			elif currentPOCall.firstOperand.id == ATM__POCALL:
				maxStopIndex = self.ODP_applyGroupPriorization(maxStopIndex, currentPOCall.firstOperand.data, operatorsAllowed, monoOperand=monoOperand)

		#2nd operand
		if currentPOCall.secondOperand is not None:

			#leaf => apply here
			if currentPOCall.secondOperand.id == ATM__ZCI:
				originalCtx  = currentPOCall.secondOperand.data.ctx.copy()
				currentOpSeq = self.ODP_readAndSplitByOperators(currentPOCall.secondOperand.data, operatorsAllowed)

				#no operator found => restore origin ctx, update ZCI length (even if no op has been found, we know where ODP should stop so we can cut directly => optimization)
				if currentOpSeq.operators is None:
					currentPOCall.secondOperand.data.resetCtx(originalCtx)
					currentPOCall.secondOperand.data.stopIndex = currentOpSeq.stopIndex
					currentPOCall.secondOperand.data.strip()

				#operator found => progressive priorizing
				else:
					currentPOCall.secondOperand = atm(
						ATM__POCALL,
						self.progressivePriorizing(currentOpSeq, monoOperand)
					)

				#update maxStopIndex
				if maxStopIndex < currentOpSeq.stopIndex:
					maxStopIndex = currentOpSeq.stopIndex

			#tree => check deeper
			elif currentPOCall.secondOperand.id == ATM__POCALL:
				maxStopIndex = self.ODP_applyGroupPriorization(maxStopIndex, currentPOCall.secondOperand.data, operatorsAllowed, monoOperand=monoOperand)

		#return it to know until where ODP has been (so we know where to continue reading after that Value)
		return maxStopIndex



	#entry point for Operation Decomposition Process (ODP)
	def ODP(self, originalZCI):
		ZCI            = originalZCI.copy()
		ZCI.startIndex = ZCI.ctx.icontent.index
		ZCI.updateText()

		#prepare result
		result = ODPRODPResultesult = ODPResult(
			0,
			POCall( None, atm(ATM__ZCI, ZCI) ) #formatting raw input value under POCall format
		)

		#deep debug
		self.deepDebug("Beginning ODP on ZCI " + ZCI.textFormat())

		#1st group priorization (lowest): CO
		self.deepDebug("ODP-0: Applying 1st group priorization.")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, CO)
		self.deepDebug("ODP-0: Applied 1st group priorization, resulted into " + result.mainPOCall.toStr())

		#2nd group priorization: BO
		self.deepDebug("ODP-0: Applying 2nd group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, BO)
		self.deepDebug("ODP-0: Applied 2nd group priorization, resulted into " + result.mainPOCall.toStr())

		#3rd group priorization: AO + LO
		self.deepDebug("ODP-0: Applying 3rd group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, AO + LO)
		self.deepDebug("ODP-0: Applied 3rd group priorization, resulted into " + result.mainPOCall.toStr())

		#4th group priorization: DO
		self.deepDebug("ODP-0: Applying 4th group priorization")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, DO)
		self.deepDebug("ODP-0: Applied 4th group priorization, resulted into " + result.mainPOCall.toStr())

		#5th group priorization: SO (highest treated in ODP)
		self.deepDebug("ODP-0: Applying 5th group priorization (SO)")
		result.maxStopIndex = self.ODP_applyGroupPriorization(result.maxStopIndex, result.mainPOCall, SO, monoOperand=True)
		self.deepDebug("ODP-0: Applied 5th group priorization, resulted into " + result.mainPOCall.toStr())
		self.deepDebug("Ended ODP on ZCI " + ZCI.textFormat())
		return result



	#2nd analysis
	def unknownValueErrorIn2ndAnalysis(self, ZCI):
		self.ZCIError(ZCI, "Unknown value given (not respecting any format supported by VAP in 2nd analysis).")

	def secondAnalysis(self, ZCI, vap2info):
		self.ZCIDeepDebug(ZCI, "2nd analysis: Reading ZCI fragment " + ZCI.textFormat() + " to apply second analysis on it.")
		result = None
		c = ZCI.get()



		# I] LITERAL: COMMON DATA STRUCTURES

		#map starter symbol
		targettingMap = False
		if c == ':':
			if ZCI.inc():
				self.unknownValueErrorIn2ndAnalysis(ZCI)
			targettingMap = True

		#starting with includer
		if c in ('(', '[', '{'):
			#Seems similar to check in the whole INCLUDERS.keys() but this is not related to these actually.
			#We are specificly targetting these 3 and not because they are includer keys but because we have specific pattern associated to them.
			keyValue_initializerType = None #for maps only
			if c == '(':
				if targettingMap:
					targettedType            = self.getType(TYPE_FULLNAME_FMAP)
					keyValue_initializerType = self.getType(TYPE_FULLNAME_TAB) #require 2 tab for fmap initialization
				else:
					targettedType = self.getType(TYPE_FULLNAME_TAB)
			elif c == '[':
				if targettingMap:
					targettedType            = self.getType(TYPE_FULLNAME_MMAP)
					keyValue_initializerType = self.getType(TYPE_FULLNAME_LST) #require 2 lst for mmap initialization
				else:
					targettedType = self.getType(TYPE_FULLNAME_LST)
			elif c == '{':
				if targettingMap:
					self.ZCIError(ZCI, "Associative notation cannot be set to braces includer (\":{...}\" is linked to nothing).")
				targettedType = self.getType(TYPE_FULLNAME_FLY)

			#init limits
			peerIndex    = ZCI.pairs[ZCI.ctx.icontent.index]
			targettedEnd = ZCI.ctx.icontent.s[peerIndex]
			ZCI.inc()

			#read subvalues as long as we have some (separated by comas)
			subValues        = [] #lst[value]
			subValues_second = [] #for maps
			while True:

				#read subvalue
				self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
				subValues.append( self.readValue(ZCI, vap2info.ZCIKindIfError, vap2info.scope, vap2info.cstOnly) )

				#read second subValue (for maps only)
				if targettingMap:

					#colon separator required
					self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
					next = ZCI.get()
					if next != ':':
						self.ZCIError(ZCI, "Invalid element " + next + " given in associative sequence (expected colon separator ':').")
					ZCI.inc()

					#read a second subvalue (require a couple for association)
					self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
					subValues_second.append( self.readValue(ZCI, vap2info.ZCIKindIfError, vap2info.scope, vap2info.cstOnly) )

				#look for end separator
				self.optionnalBlanks(ZCI, None, BLANKS_EXTENDED)
				next = ZCI.get()
				if next == targettedEnd:
					if ZCI.ctx.icontent.index != peerIndex:
						self.ZCIInternal(ZCI, "Ending value sequence inside includer with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(peerIndex) + ").")
					ZCI.inc()
					break
				if next != ',':
					self.ZCIError(ZCI, "Invalid element " + next + " given in value sequence between includers (expected coma separator ',' or closing includer '" + targettedEnd + "').")
				ZCI.inc()

			#table with only one element => explicit priorization
			if targettedEnd == ')' and not targettingMap and len(subValues) == 1:
				result = subValues[0]
				self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in EXPLICIT PRIORIZATION " + result.toStr())
				return result

			#finishing result: maps
			if targettingMap:

				#set keys et values for map initialization
				keys   = value(keyValue_initializerType, atm(ATM__LST, subValues))
				values = value(keyValue_initializerType, atm(ATM__LST, subValues_second))
				result = value(
					targettedType,
					atm(ATM__LST, [keys, values])
				)

			#finishing result: tab, lst & fly
			else:
				result = value(targettedType, atm(ATM__LST, subValues))

			#return result
			self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in COMMON DATA STRUCTURE SHORTCUT NOTATION " + result.toStr())
			return result

		#having found a colon but wasn't a map => no pattern matches such a thing
		if targettingMap:
			self.unknownValueErrorIn2ndAnalysis(ZCI)



		# II] LITERAL: BYTE NOTATIONS

		#prefix found
		if c == BN_PREFIX:
			if ZCI.inc():
				self.ZCIError(ZCI, "Missing content after byte notation.")

			#multi-byte sequence
			if ZCI.get() == BN_PREFIX:
				if ZCI.inc():
					self.ZCIError(ZCI, "Missing content after multiple-bytes notation.")

				#prepare sequence
				sequence = [] #lst[value]
				while ZCI.get() in HEX_DIGITS_LOWERCASE:
					sequence.append(
						value(self.rootTypes[RT__BYT], atm(ATM__BYT, self.readHexByte(ZCI)) )
					)
					if ZCI.inc():
						break

				#missing characters
				if len(sequence) == 0:
					self.ZCIError(ZCI, "Missing valid hexadecimal characters in multi-bytes notation.")

				#finish result
				result = value(self.rootTypes[RT__PTR], atm(ATM_LST, sequence))
				self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in MULTI-BYTE NOTATION " + result.toStr())
				return result

			#single-byte sequence
			result = value(
				self.rootTypes[RT__BYT],
				atm(ATM__BYT, self.readHexByte(ZCI))
			)
			ZCI.inc()
			self.ZCIDeepDebug(ZCI, "2nd analysis: Finished reading ZCI fragment " + ZCI.textFormat() + ", resulted in SINGLE-BYTE NOTATION " + result.toStr())
			return result



		# III] .

		#
		#



		#unknown value format
		self.unknownValueErrorIn2ndAnalysis(ZCI)



	def secondAnalysisIncludingFOs(self, ZCI, vap2info):

		#mono-operand FOs: size (FSZ)
		if ZCI.get() == '#':
			self.ZCIDeepDebug(ZCI, "2nd analysis: Processing FSZ operator.")
			Type = None

			#try to get type directly
			Type = self.readType(ZCI, vap2info.ZCIKindIfError, nullIfNotExisting=True)

			#rather try to get it through a data item name given
			if Type is None:
				di = getDataItem(
					self.readName(ZCI, "raw type or data item name for size operator (#)"),
					vap2info.scope
				)
				if di is None:
					self.ZCIError(ZCI, "Unable to get raw type or data item name for size operator (#).")
				Type = di.Type

			#process FO & return result
			#result = value(self.rootTypes[RT__LONG], atm(ATM_CALL, result)) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO CONTINUE
			#size = Type.size
			#if reslt
			self.ZCIDeepDebug("2nd analysis: FSZ resulted into fsz(" + Type.name + ") = " + str(Type.size))
			return result

		#mono-operand FOs: reference (FRF)
		if ZCI.get() == '@':
			return None

		#second analysis: read value but don't care if there are still things to analyze ()
		result = self.SecondAnalysis(ZCI, vap2info) #after this, ZCI index is right AFTER the value read
		self.optionnalBlanks(ZCI, None)

		#that was it
		if ZCI.reachedEnd():
			return result

		#2-operands FOs: casht (FCA)
		if ZCI.get() == '$':
			return None

		#2-operands FOs: field access (FFA)
		if ZCI.get() == '.':
			return None

		#too much content in VALUE ZCE
		self.ZCIError(ZCI, "Too much elements in VALUE ZCE (2nd analysis parsing).")



	def applySecondAnalysis(self, currentPOCall, originalZCI, vap2info):

		#process 1st operand
		firstOperandValue = None
		if currentPOCall.firstOperand is not None:

			#recursively solving children before
			if currentPOCall.firstOperand.id == ATM__POCALL:
				firstOperandValue = self.applySecondAnalysis(currentPOCall.firstOperand.data, originalZCI, vap2info)

			#considering it can only be a ZCI atm (internal error case could have added)
			else:
				firstOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.firstOperand.data, vap2info)

		#process 2nd operand
		secondOperandValue = None
		if currentPOCall.secondOperand is not None:

			#recursively solving children before
			if currentPOCall.secondOperand.id == ATM__POCALL:
				secondOperandValue = self.secondAnalysisIncludingFOs(currentPOCall.secondOperand.data, originalZCI, vap2info)

			#considering it can only be a ZCI atm (internal error case could have added)
			else:
				secondOperandValue = self.processFOAndSecondAnalysis(currentPOCall.secondOperand.data, vap2info)



		#1ST CASE: SINGLE VALUE UNIT (NON-CALL)

		#null name => mono-operand mandatorily
		if currentPOCall.name is None:
			target = None
			if currentPOCall.firstOperand is None:
				target = secondOperandValue
			elif currentPOCall.secondOperand is None:
				target = firstOperandValue

			#should never occur
			if target is None:
				self.internal("Found null-name POCall with 2 null or 2 non-null operands (inconsistent result from ODP).")
			return target



		#2ND CASE: OPERATOR CALL

		#set operator parameters
		params = []
		if firstOperandValue is not None:
			params.append(firstOperandValue)
		if secondOperandValue is not None:
			params.append(secondOperandValue)

		#solve name
		operatorFullName = currentPOCall.name[:] #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO COMPLETE with full name constitution
		#operatorFullName = 'O' + currentPOCall.name
		#for p in params:
		#	operatorFullName += '_' + p.type.name

		#check for matching operator function
		matchingFunction = None
		for f in self.cpl.functions:
			if f.name == operatorFullName:
				matchingFunction = f
				break
		if matchingFunction is None:
			originalZCI.forward(currentPOCall.operatorIndex - originalZCI.ctx.icontent.index)
			self.ZCIError(originalZCI, "No operator \"" + f.name + "\" declared yet.")

		#result
		return value(
			matchingFunction.retType,
			atm(ATM__CALL, call(operatorFullName, params))
		)



	#value analysis process (VAP)
	def readValue(self, ZCI, ZCIKindIfError, scope, cstOnly=False):
		self.ZCIDeepDebug(ZCI, "Reading value.")

		#1st analysis: ODP
		firstAnalysisResult = self.ODP(ZCI)
		ZCI.forward( firstAnalysisResult.maxStopIndex - ZCI.ctx.icontent.index +1)

		#apply 2nd analysis recursively in ODP result
		secondAnalysisResult = self.applySecondAnalysis(firstAnalysisResult.mainPOCall, ZCI, vap2(ZCIKindIfError, scope, cstOnly)) #here, ZCI is given for error messages only
		self.ZCIDeepDebug(ZCI, "Ended reading value with result :" + secondAnalysisResult.toStr())
		return secondAnalysisResult





	#data items
	def checkAlreadyDeclaredDataItemOrField(self, ZCI, dis, di):
		for other in dis:
			if other.name == di.name:
				self.ZCIError(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")

	def readDataItem(self, ZCI, ZCIKindIfError, scope, cstInitialValueOnly=False, allowUnsolvedType=False):
		self.ZCIDeepDebug(ZCI, "Reading data item.")

		#read type (if any. Else, continue as nothing happened)
		Type = self.readType(ZCI, "data item declarator, in " + ZCIKindIfError, nullIfNotExisting=True)
		if Type is not None:
			self.jumpBlankZone(ZCI, "data item name") #no line feed allowed between type-name-initialValue

		#read name
		name = self.readName(ZCI, "data item name", parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)

		#default initial value: uninitialized
		initialized  = False
		initialValue = None

		#special behavior in global scope
		if scope == self.cpl.globalScope:
			cstInitialValueOnly = True #force cst values

		#optionnal assignment symbol => initial value given
		self.optionnalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
		sym = self.readSymbol(ZCI)
		if sym != SYMBOL__NOT_FOUND: #found a symbol
			if sym != SYMBOL__ASG:
				self.ZCIError(ZCI, "Invalid symbol given here, can only have assignment.")
			ZCI.forward(SYMBOL_LENGTHS[SYMBOL__ASG])

			#read given initial value
			initialized = True
			self.optionnalBlanks(ZCI, None) #no line feed allowed between type-name-initialValue
			initialValue = self.readValue(ZCI, ZCIKindIfError, scope, cstOnly=cstInitialValueOnly)

			#solve type if missing using initialValue
			if Type is None:
				Type = initialValue.Type
				self.ZCIDeepDebug(ZCI, "Solving missing type using initial value given \"" + Type.name + "\".")
		self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

		#missing Type still not solved
		if not allowUnsolvedType:
			if Type is None:
				self.ZCIError(ZCI, "Missing type to given element (required either explicitely or implicity).")

		#result
		self.ZCIDeepDebug(ZCI, "Ended reading data item.")
		return dataItem(Type, name, initialized, initialValue)

	#read dataitem sequence
	# Given ZCI must be at an opening includer character.
	def readDataItemSequence(self, ZCI, ZCIKindIfError, scope, cstValuesOnly=False, allowUnsolvedTypes=False):
		self.ZCIDeepDebug(ZCI, "Reading sequence of data item(s).")

		#initial conditions
		initialIndex = ZCI.ctx.icontent.index
		peerIndex    = ZCI.pairs[initialIndex]
		if ZCI.get() not in INCLUDERS.keys():
			self.ZCIInternal(ZCI, "Must be at the beginning of an includer to read data item sequence.")
		ZCI.inc()

		#read sequence
		dis = []   #lst[dataItem]
		foundSelfKw = False
		while True:
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

				#read & store data item
				di = self.readDataItem(ZCI, ZCIKindIfError, scope, cstInitialValueOnly=cstValuesOnly, allowUnsolvedType=allowUnsolvedTypes)
				self.checkAlreadyDeclaredDataItemOrField(ZCI, dis, di)
				dis.append(di)
				self.ZCIDeepDebug(ZCI, "Got data item " + di.toStr())

				#must be followed by coma or closing peer
				next = ZCI.get()
				if next in INCLUDERS.values():
					if ZCI.ctx.icontent.index != peerIndex:
						self.ZCIInternal(ZCI, "Ending data item sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(peerIndex) + ").")
					ZCI.inc()
					break
				if next != ',':
					self.ZCIError(ZCI, "Invalid element " + next + " given in data item sequence (expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[peerIndex] + "').")
				ZCI.inc()

		#return result
		self.ZCIDeepDebug(ZCI, "Ended reading sequence of data item(s).")
		return dis



