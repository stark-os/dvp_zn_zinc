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
ATM__CALL = 11
class atm:
	def __init__(self, id, data):
		self.id   = id
		self.data = data






# -------- GENERAL --------

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DEFAULT_NAME_CHARSET            = string.ascii_letters + string.digits + '_'
ZCI_FIRSTWORD_DETECTION_CHARSET = BLANKS + tuple(INCLUDERS.keys())
FCT_NAME_CHARSET                = DEFAULT_NAME_CHARSET + ".[]=-+*/^%[:~!&|<>"

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

#Single Operators
SYMBOL__SIN  = 1 #invert
SYMBOL__SNO  = 2 #not

#Decisionnal Operators
SYMBOL__DAN = 3 #decisionnal and
SYMBOL__DOR = 4 #decisionnal or

#Arithmetic Operators
SYMBOL__AMU = 5 #multiply
SYMBOL__ADI = 6 #divide
SYMBOL__AMO = 7 #modulo
SYMBOL__APO = 8 #power

#B-rithmetic Operators
SYMBOL__BAD =  9 #add
SYMBOL__BSU = 10 #subtract

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

#Conditionnal Operators
SYMBOL__CEQ = 20 #equals
SYMBOL__CNE = 21 #not equals
SYMBOL__CLT = 22 #lesser than
SYMBOL__CGT = 23 #greater than
SYMBOL__CLE = 24 #lesser or equal
SYMBOL__CGE = 25 #greater or equal

#Indexing Operators (without includers)
SYMBOL__IAM = 30 #among
SYMBOL__INA = 31 #not among

#Fixed Operators
SYMBOL__FSZ = 32 #size
SYMBOL__FRF = 33 #reference
SYMBOL__FCA = 34 #casht
SYMBOL__FFA = 35 #field access

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

#tools
def unprefixizeModule(modulePrefix):
	if len(modulePrefix) == 0:
		return ""
	if modulePrefix[0] == 'G':
		return ""
	return "^" + str_sub(modulePrefix, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1] + '.'

#ZCI
class zci:
	def __init__(self, subCtxs, modulePrefix=None, pairs=None):
		if modulePrefix is None:
			modulePrefix = ""
		if pairs is None:
			pairs = {}
		if lst_isEmpty(subCtxs):
			print("[INTERNAL] Cannot instantiate a ZCI with no subCtxs.")
			exit(1)
		self.subCtxs      = subCtxs
		self.ctx          = subCtxs[-1]
		self.pairs        = pairs #map[unt_l,unt_l]
		self.modulePrefix = modulePrefix
		self.text         = ""
		self.startIndex   = self.ctx.icontent.index #current position is where our ZCI starts
		self.stopIndex    = self.startIndex



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

	def tmpCtxCopy(self):
		tmpCtxCopyZCI      = zci(lst_copy(self.subCtxs), modulePrefix=self.modulePrefix, pairs=self.pairs)
		tmpCtxCopyZCI.text = self.text
		tmpCtxCopyZCI.resetCtx(self.ctx.copy()) #we copy ctx & subctxs so that we can TEMPORARILY work on that ZCI without affecting it really
		return tmpCtxCopyZCI



	#debug output
	def textFormat(self):
		return '\"' + self.text.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n") + '\"'

	def toStr(self):
		return "{module:\"" + self.modulePrefix + "\",ctx:\"" + self.ctx.toStr() + "\",startIndex:" + str(self.startIndex) + ",stopIndex:" + str(self.stopIndex) + ",text:" + self.textFormat() + ",pairs:\"" + str(self.pairs).replace(' ', '') + "\"}"

def dumpZCIs(ZCIs, filename):
	output = "[\n"
	for ZCI in ZCIs:
		output += "\t" + ZCI.toStr() + ",\n"
	output += "]"
	writeFile(filename, output)






# -------- PRECOMPILATION --------

#pcpl items
PCPL_ITEM_NAME_CHARSET = DEFAULT_NAME_CHARSET #no link, but same value

#pcpl data
class pcplDat:
	def __init__(self, configs, items):
		self.items      = items
		self.configs    = configs

#format configs
def pcplDat_new(configs, items):
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

#ztyp can be declared after zprm & zstc in Z.
#However, here in Python, we must declare it before to allow dataItem definition and so, zstc.
#Same thing for zfct.
class ztyp_commonDcnData: #common ztype data among every declination
	def __init__(self, dcnDeg):
		self.parent = None
		self.size   = 0
		self.dcnDeg = dcnDeg

		#stc related
		self.isStc   = False #<=> type "nature" (is primitive / structure)
		self.fields  = None
		self.stcSize = 0

class ztyp:
	def __init__(self, name, dcnDeg=0, dcns=None, commonDcnData=None):
		if commonDcnData is None:
			commonDcnData = ztyp_commonDcnData(dcnDeg) #create a new commonDcnData by default (new type => new commonDcnData)
		self.name          = name
		self.methods       = []   #lst[zfct]
		self.dcns          = dcns #tab[ztyp]
		self.commonDcnData = commonDcnData #ztyp_commonDcnData

	def computeStcSize(self):
		if self.commonDcnData.isStc:
			for f in self.commonDcnData.fields: #NOTE THAT HERE, WE DO SUM SIZES AND NOT STC-SIZES ! Structures contained inside another structure are always considered as pointers.
				self.commonDcnData.stcSize += f.ztype.commonDcnData.size

class value:
	def __init__(self, ztype, data, constant=False):
		self.ztype    = ztype
		self.data     = data  #atm #can be either a root type (literal), str (name) or call.
		self.constant = constant

	def toStr(self):
		if self.data.id == ATM__BOO: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< I know, this seems weird in Python but it makes sens in Z (will have to be a swi btw)
			dataStr = "false"
			if self.data:
				dataStr = "true"
		elif self.data.id == ATM__BYT:
			dataStr = 'S' + hexOnN(self.data, 2)
		elif self.data.id == ATM__UBYT:
			dataStr = 'U' + hexOnN(self.data, 2)
		elif self.data.id == ATM__SHR:
			dataStr = 'S' + hexOnN(self.data, 4)
		elif self.data.id == ATM__USHR:
			dataStr = 'U' + hexOnN(self.data, 4)
		elif self.data.id == ATM__INT:
			dataStr = 'S' + hexOnN(self.data, 8)
		elif self.data.id == ATM__UINT:
			dataStr = 'U' + hexOnN(self.data, 8)
		elif self.data.id == ATM__LNG:
			dataStr = 'S' + hexOnN(self.data, 16) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< no way to get arch type here... will stay in 64b for the moment (can be formatted again later)
		elif self.data.id == ATM__ULNG:
			dataStr = 'U' + hexOnN(self.data, 16)
		elif self.data.id == ATM__CHR:
			dataStr = '\'' + self.data + '\''
		elif self.data.id == ATM__STR: #this case covers both literal string & name. In all cases, toStr() will output a double-quoted result.
			dataStr = '\"' + self.data + '\"' #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< for the moment, it also covers the case of literal structures (stored under raw text)
		elif self.data.id == ATM__CALL:
			dataStr  = '\"' + self.data.name + '('
			for p in self.data.params:
				dataStr += p.toStr() + ',' #recursive call
			dataStr += ")\""
		else:
			print("[INTERNAL] Invalid data stored inside value (can only be literal, name or call).")
			exit(1)
		return "{type:\"" + self.ztype.name + "\",constant:" + str(self.constant) + ",data:" + dataStr + "}"

class call:
	def __init__(self, name, params):
		self.name   = name
		self.params = params #lst[value]

class dataItem:
	def __init__(self, ztype, name, initialized, initialValue, constant=False):
		self.ztype        = ztype
		self.name         = name
		self.initialized  = initialized
		self.initialValue = initialValue #value
		self.constant     = constant

	def toStr(self):
		initialValueStr = "null"
		if self.initialValue is not None:
			initialValueStr = self.initialValue.toStr()
		ztypeStr = "null"
		if self.ztype is None:
			ztypeStr = '\"' + self.ztype.name + '\"'
		return "{type:" + ztypeStr + ",name:\"" + self.name + "\",initialized:" + str(self.initialized) + ",initialValue:" + initialValueStr + ",constant:" + str(self.constant) + "}"

#scope
class scp:
	def __init__(self, parent=None):
		self.exes      = [] #lst[atm] #can have either asg, call (vfc in that case) or stm inside, all mixed of course.
		self.dataItems = [] #lst[dataItem]
		self.parent    = parent

class asg:
	def __init__(self, dst, src):
		self.dst = dst #dataItem or str (name only) ?
		self.src = src #value

#statement kinds
STM__IF_ = 0
STM__FOR = 1
STM__WHI = 2
STM__SWI = 3

class stm:
	def __init__(self, kind, parentScope):
		self.kind  = kind
		self.scope = scp(parent=parentScope)

class fct:
	def __init__(self, name, params, parentScope):
		self.name   = name
		self.params = params #lst[dataItem]
		self.scope  = scp(parent=parentScope)

#compiler data
class cplDat:
	def __init__(self, options, rootTypes):
		self.options = options

		#z abstract elements
		self.modulePrefixes = [] #lst[str]
		self.ztypes         = lst_copy(rootTypes) #lst[ztyp]
		self.globalScope    = scp()
		self.functions      = [] #lst[fct]
		self.linkedLibs     = [] #lst[]

		#program concrete elements
		#self.dataResult = program() <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< maybe not required
		self.textResult = ""






# -------- CONTEXTS --------

#z code context
class zctx:
	def __init__(self,
		filepath, LLI,
		pcpl_cfg, pcpl_itm,
		cpl_opt,  debugMode=False, deepDebugMode=False
	):
		self.LLI           = {}
		self.debugMode     = debugMode
		self.deepDebugMode = deepDebugMode

		#every imported context & the current one
		self.initialCtx   = ParsingCtx(filepath, readFile(filepath))
		self.ctx          = self.initialCtx
		self.imported     = [] #history of every filename imported
		self.subCtxs      = [] #subcontexts currently in use
		self.subCtxs.append(self.initialCtx)

		#check CPL options
		self.checkCplOpt(cpl_opt)

		#real memory items <<<<<<<<<<<<<<<<<<<<<< to be stored into an enm
		self.SIZE__BYT = 1
		self.SIZE__SHR = 2
		self.SIZE__INT = 4
		self.SIZE__LNG = 4
		if cpl_opt["ARCH"] == "64":
			self.SIZE__LNG = 8

		#init root types locally (to be given to cpl data)
		self.rootTypes = [None,None,None, None,None,None, None,None,None, None,None,None] #can be already declared as a fixed-size table (length: 12)

		#boolean
		self.rootTypes[RT__BOO]      = ztyp("GUboo")
		self.rootTypes[RT__BOO].size = self.SIZE__BYT

		#bytes
		self.rootTypes[RT__BYT]       = ztyp("GUbyt")
		self.rootTypes[RT__BYT].size  = self.SIZE__BYT
		self.rootTypes[RT__UBYT]      = ztyp("GUubyt")
		self.rootTypes[RT__UBYT].size = self.SIZE__BYT

		#shorts
		self.rootTypes[RT__SHR]       = ztyp("GUshr")
		self.rootTypes[RT__SHR].size  = self.SIZE__SHR
		self.rootTypes[RT__USHR]      = ztyp("GUushr")
		self.rootTypes[RT__USHR].size = self.SIZE__SHR

		#integers
		self.rootTypes[RT__INT]       = ztyp("GUint")
		self.rootTypes[RT__INT].size  = self.SIZE__INT
		self.rootTypes[RT__UINT]      = ztyp("GUuint")
		self.rootTypes[RT__UINT].size = self.SIZE__INT

		#longs
		self.rootTypes[RT__LNG]       = ztyp("GUlng")
		self.rootTypes[RT__LNG].size  = self.SIZE__LNG
		self.rootTypes[RT__ULNG]      = ztyp("GUulng")
		self.rootTypes[RT__ULNG].size = self.SIZE__LNG

		#floating point
		self.rootTypes[RT__FLT]      = ztyp("GUflt")
		self.rootTypes[RT__FLT].size = self.SIZE__INT
		self.rootTypes[RT__DBL]      = ztyp("GUdbl")
		self.rootTypes[RT__DBL].size = self.SIZE__LNG

		#pointer
		self.rootTypes[RT__PTR]      = ztyp("GUptr", 1)
		self.rootTypes[RT__PTR].size = self.SIZE__LNG

		#data
		self.ZCIs = None
		self.pcpl = pcplDat_new(pcpl_cfg, pcpl_itm)
		self.cpl  = cplDat(cpl_opt, self.rootTypes)



	# CFG CHECK

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



	# PARSING

	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)

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



	# GENERAL PARSING TOOLS

	#move ctx cursor just before the first non-blank character found
	def jumpBlankZone(self, ZCI, missingFieldIfError, blanks=BLANKS):
		while not ZCI.inc():
			if ZCI.get() not in blanks:
				return
		if missingFieldIfError is not None:
			self.ZCIError(ZCI, "Expected something after blank zone : " + missingFieldIfError)

	def optionnalBlanks(self, ZCI, missingFieldIfError, blanks=BLANKS):
		if ZCI.get() in blanks:
			self.jumpBlankZone(ZCI, missingFieldIfError, blanks=blanks)

	def endOfZCI(self, ZCI, ZCIKindIfError):
		if not ZCI.reachedEnd():
			self.ZCIError(ZCI, "Too much elements in " + ZCIKindIfError + " Should stop here.")



	# REAL ZCE PARSING TOOLS (bare metal syntax-related)

	#try reading symbol (don't move ZCI ctx)
	def readSymbol(self, ZCI):
		self.ZCIDeepDebug(ZCI, "Reading symbol.")
		tmpZCI = ZCI.tmpCtxCopy()
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
			elif c2 == 'i':
				tmpZCI.inc()
				if tmpZCI.get() == 'n':
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

		#multi-character symbol: starting with 'i'
		elif c1 == 'i':
			tmpZCI.inc()
			if tmpZCI.get() == 'n':
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

	def splitModulePrefix(self, ZCI, name):
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
			self.ZCIInternal(ZCI, "Invalid module prefix '" + modulePrefix + "' extracted from name '" + name + "' (ending with even number of underscores).")
		return modulePrefix



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



	# ABSTRACT ZCEs PARSING TOOLS

	#expecting a Z type
	def readZType(self, ZCI, ZCIKindIfError, nullIfNotExisting=False):
		self.ZCIDeepDebug(ZCI, "Reading Z type.")
		initialZCICtx = ZCI.ctx.copy()

		#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
		ztRawName = self.readName(ZCI, "Type name in " + ZCIKindIfError, parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)

		#module-realted / global
		if initialZCICtx.get() == '^':
			ztModulePrefix = self.splitModulePrefix(ZCI, ztRawName)        #save its module prefix elsewhere
			ztRawName      = str_sub(ztRawName, start=len(ztModulePrefix)) # + cut it from "rawName" to keep only the REAL RAW NAME
		else:
			ztModulePrefix = "G"

		#build full type name (forced "undeclinated" for the moment)
		ztFullName = ztModulePrefix + 'U' + ztRawName

		#1 - check UNDECLINATED variant existence
		ztInstance = None
		for t in self.cpl.ztypes:
			if ztFullName == t.name:
				ztInstance = t
				break
		if ztInstance is None:
			if nullIfNotExisting:
				self.ZCIDeepDebug(ZCI, "Type " + unprefixizeModule(ztModulePrefix) + ztRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", printLine=False)
				ZCI.resetCtx(initialZCICtx)
				self.ZCIDeepDebug(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
				return None
			self.ZCIError(ZCI, "Type " + unprefixizeModule(ztModulePrefix) + ztRawName.replace("__", '_') + " does not exist.")
		self.ZCIDeepDebug(ZCI, "Undeclinated Z type \"" + ztFullName + "\" targetted.")

		#2 - declination list given => solve them
		if ZCI.get() == '[':
			initialIndex = ZCI.ctx.icontent.index
			ZCI.inc()

			#undeclinable type
			if ztInstance.commonDcnData.dcnDeg == 0:
				self.ZCIError(ZCI, "Type " + unprefixizeModule(ztModulePrefix) + ztRawName.replace("__", '_') + " is not declinable (null declination degree).")

			#read declination types one by one
			self.deepDebug("Type is declinated, reading declination types.")
			dcns = [] #lst[ztyp]
			while True:
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

				#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
				dcns.append(self.readZType(ZCI, ZCIKindIfError))

				#must be followed by coma or closing peer
				self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
				next = ZCI.get()
				if next == ']':
					if ZCI.ctx.icontent.index != ZCI.pairs[initialIndex]:
						self.ZCIInternal(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(ZCI.pairs[initialIndex]) + " in string \"" + ZCI.ctx.icontent.s + "\").")
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
			if len(dcns) < ztInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(ztInstance.commonDcnData.dcnDeg) + " required).")
			elif len(dcns) > ztInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(ztInstance.commonDcnData.dcnDeg) + " required).")

			#re-build full type name including declinations this time (ztModulePrefix can be set to "G" by the way, same logic as undeclinated types)
			ztFullName = ztModulePrefix + 'D' + ztRawName
			for d in dcns:
				ztFullName += '_' + d.name

			#check for that declination in currently declared ztypes
			ztUndeclinatedInstance = ztInstance
			ztInstance             = None
			for t in self.cpl.ztypes:
				if ztFullName == t.name:
					ztInstance = t
					break

			#not found => create that declination (this new combination must exist)
			if ztInstance is None:
				ztInstance      = ztyp(ztFullName, commonDcnData = ztUndeclinatedInstance.commonDcnData) #share the same commonDcnData (affecting the undeclinated instance will affect every declination)
				ztInstance.dcns = dcns
				self.ZCIDebug(ZCI, "First call of declination \"" + ztInstance.name + "\" from type \"" + ztUndeclinatedInstance.name + "\", adding it.")
				self.cpl.ztypes.append(ztInstance)

		#final result
		self.ZCIDeepDebug(ZCI, "Ended reading Z type.")
		return ztInstance



	#value analysis process (VAP)
	def readValue(self, ZCI, ZCIKindIfError, scope, cstOnly=False):
		self.ZCIDeepDebug(ZCI, "Reading value.")

		#

		self.ZCIDeepDebug(ZCI, "Ended reading value.")
		n = self.readName(ZCI, ZCIKindIfError) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
		return value(self.rootTypes[RT__ULNG], 0)



	#data items
	def checkAlreadyDeclaredDataItemOrField(self, ZCI, dis, di):
		for other in dis:
			if other.name == di.name:
				self.ZCIError(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")

	def readDataItem(self, ZCI, ZCIKindIfError, scope, cstInitialValueOnly=False, allowUnsolvedType=False):
		self.ZCIDeepDebug(ZCI, "Reading data item.")

		#read type (if any. Else, continue as nothing happened)
		ztype = self.readZType(ZCI, "data item declarator, in " + ZCIKindIfError, nullIfNotExisting=True)

		#read name
		self.jumpBlankZone(ZCI, "data item name") #no line feed allowed between type-name-initialValue
		name = self.readName(ZCI, "data item name")

		#default initial value: uninitialized
		initialized  = False
		initialValue = None

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

			#solve ztype if missing using initialValue
			if ztype is None:
				ztype = initialValue.ztype
				self.ZCIDeepDebug(ZCI, "Solving missing type using initial value given \"" + ztype.name + "\".")
		self.optionnalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

		#missing ztype still not solved
		if allowUnsolvedType:
			if ztype is None:
				self.ZCIError(ZCI, "Missing type to given element (required either explicitely or implicity).")

		#result
		self.ZCIDeepDebug(ZCI, "Ended reading data item.")
		return dataItem(ztype, name, initialized, initialValue)

	#read dataitem sequence
	# Given ZCI must be at an opening includer character.
	def readDataItemSequence(self, ZCI, ZCIKindIfError, scope, cstValuesOnly=False, allowUnsolvedTypes=False):
		self.ZCIDeepDebug(ZCI, "Reading sequence of data item(s).")

		#initial conditions
		initialIndex = ZCI.ctx.icontent.index
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
					if ZCI.ctx.icontent.index != ZCI.pairs[initialIndex]:
						self.ZCIInternal(ZCI, "Ending data item sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.index) + " instead of targetted " + str(ZCI.pairs[initialIndex]) + " in string \"" + ZCI.ctx.icontent.s + "\").")
					ZCI.inc()
					break
				elif next != ',':
					self.ZCIError(ZCI, "Invalid element given " + next + " in data item sequence (expected coma separator ',' or closing includer '" + ZCI.ctx.icontent.s[ ZCI.pairs[initialIndex] ] + "').")
				ZCI.inc()

		#return result
		self.ZCIDeepDebug(ZCI, "Ended reading sequence of data item(s).")
		return dis
