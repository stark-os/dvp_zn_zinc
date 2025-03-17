#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.list       import *
from std.io         import *
from std.parsingCtx import *

#charsets
import string






# -------- CONSTANTS --------

#precompiler
PCPL_ITEM_NAME_CHARSET = string.ascii_letters + string.digits + '_'

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DATAITEM_NAME_CHARSET           = PCPL_ITEM_NAME_CHARSET #no link with PCPL items, but same value
ZCI_FIRSTWORD_DETECTION_CHARSET = BLANKS + tuple(INCLUDERS.keys())
ZCE_NAME_CHARSET                = DATAITEM_NAME_CHARSET + "^."

#general name parsing
NO_NAME            = -1
BLANK_AFTER_NAME   = -2
NOTHING_AFTER_NAME = -3






# -------- GENERAL --------

#tools
def unprefixizeModule(modulePrefix):
	return "^" + str_sub(modulePrefix, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1]

#ZCI
class zci:
	def __init__(self, ctx, subCtxs, modulePrefix=""):
		self.subCtxs      = subCtxs
		self.ctx          = ctx
		self.pairs        = {} #map[ulng,ulng]
		self.modulePrefix = modulePrefix

	#ctx forwards
	def get(self):
		return self.ctx.get()

	def forward(self, step):
		return self.ctx.forward(step)

	def inc(self):
		return self.ctx.inc()

	def reachedEnd(self):
		return self.ctx.reachedEnd()






# -------- PRECOMPILATION --------

#precompiler data
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

#program structure
class program:
	def __init__(self):
		self.globalData = []
		self.types      = []
		self.functions  = []
		self.linkedLibs = []


#ztyp can be declared after zprm & zstc in Z.
#However, here in Python, we must declare it before to allow dataItem definition and so, zstc.
#Same thing for zfct.
class ztyp:
	def __init__(self, name, isPrm, data, dcnDeg, parent=None):
		self.name    = name
		self.parent  = parent
		self.isPrm   = isPrm
		self.data    = data    #ptr to be cashted into zprm or zstc
		self.dcnDeg  = decnDeg #declination degree
		self.methods = []      #lst[zfct]

class dataItem:
	def __init__(self, ztyp, name, initialValue, constant=False):
		self.ztyp         = ztyp
		self.name         = name
		self.initialValue = initialValue
		self.constant     = constant

class zprm:
	def __init__(self, size):
		self.size = size

class zstc:
	def __init__(self, zCtx, fields): #requires ZCtx for ptr size
		self.fields = fields
		self.size   = zCtx.SIZE_LNG # #ptr

		#compute structure size (raw)
		self.stcSize = 0
		for f in fields.keys():
			self.stcSize += fields[f].size

#compiler data
class cplDat:
	def __init__(self, options):
		self.options = options

		#z abstract elements
		self.modulePrefixes = []
		self.ztypes         = []

		#program concrete elements
		self.dataResult = program()
		self.textResult = ""






# -------- GENERAL --------

#z code context
class zctx:
	def __init__(self,
		filepath, LLI,
		pcpl_cfg, pcpl_itm,
		cpl_opt,  debugMode
	):
		self.LLI       = {}
		self.debugMode = debugMode

		#every imported context & the current one
		initialCtx        = ParsingCtx(filepath, readFile(filepath))
		self.ctx          = initialCtx
		self.imported     = [] #history of every filename imported
		self.subCtxs      = [] #subcontexts currently in use
		self.subCtxs.append(initialCtx)

		#check CPL options
		self.checkCplOpt(cpl_opt)

		#real memory items <<<<<<<<<<<<<<<<<<<<<< to be stored into an enm
		self.SIZE = {
			'BYT':1, 'SHR':2,
			'INT':4, 'LNG':4
		}
		if cpl_opt["ARCH64"]:
			self.SIZE['LNG'] = 8

		#data
		self.ZCIs = None
		self.pcpl = pcplDat_new(pcpl_cfg, pcpl_itm)
		self.cpl  = cplDat(cpl_opt)



	# CFG CHECK

	#each cpl option must be defined
	def checkCplOpt(self, cpl_opt):
		if "ARCH64" not in cpl_opt:
			self.error("Missing compilation option \"ARCH64\" in config file cpl_opt.cfg.")
		if "INTERPRET_COMMON_STRUCTURES" not in cpl_opt:
			self.error("Missing compilation option \"INTERPRET_COMMON_STRUCTURES\" in config file cpl_opt.cfg.")
		if "MAX_INSTRUCTS_NOFUNCTION" not in cpl_opt:
			self.error("Missing compilation option \"MAX_INSTRUCTS_NOFUNCTION\" in config file cpl_opt.cfg.")
		if "CHECK_NULL_STC_BEFORE_METHOD" not in cpl_opt:
			self.error("Missing compilation option \"CHECK_NULL_STC_BEFORE_METHOD\" in config file cpl_opt.cfg.")
		if "OPERATORS_SUPPORTS_INHERITANCE" not in cpl_opt:
			self.error("Missing compilation option \"OPERATORS_SUPPORTS_INHERITANCE\" in config file cpl_opt.cfg.")
		if "METHODS_SUPPORTS_INHERITANCE" not in cpl_opt:
			self.error("Missing compilation option \"METHODS_SUPPORTS_INHERITANCE\" in config file cpl_opt.cfg.")
		if "EMPTY_DATA_ITEM_NULL" not in cpl_opt:
			self.error("Missing compilation option \"EMPTY_DATA_ITEM_NULL\" in config file cpl_opt.cfg.")
		if "LS_CNT_DIGITS" not in cpl_opt:
			self.error("Missing compilation option \"LS_CNT_DIGITS\" in config file cpl_opt.cfg.")



	# PARSING

	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)

	#output
	def debug(self, msg, printSubCtxs=True):
		if self.debugMode:
			print("[ DEBUG ] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())

	def warning(self, msg):
		print("[WARNING] " + msg)
		for ctx in self.subCtxs:
			print("    At " + ctx.toStr())

	def error(self, msg):
		print("[ ERROR ] " + msg)
		for ctx in self.subCtxs:
			print("    At " + ctx.toStr())
		exit(1)

	def internal(self, msg):
		print("[INT ERR] " + msg)
		for ctx in self.subCtxs:
			print("    At " + ctx.toStr())
		exit(2)



	# SUBCONTEXTS

	#file contexts return true if successfully openned (false means : file already processed => ignoring it)
	def openNewSubCtx(self, filepath):
		if not filepath.endswith(".z"):
			filepath += ".z"

		#resolve relativeness of given filepath regarding current context location
		if not filepath.startswith('/'):
			filepath = self.ctx.dirname + '/' + filepath

		#open new subcontext
		try:
			newCtx   = ParsingCtx(filepath, readFile(filepath))
		except FileNotFoundError:
			self.error("File " + filepath + " not found.")
		except IsADirectoryError:
			self.error("Element " + filepath + " is a directory (expected file).")

		#check already openned
		realNewPath = os.path.realpath(newCtx.filepath)
		for c in self.imported:
			if realNewPath == c:
				return False

		#not already openned => add it to importations
		self.ctx = newCtx
		self.subCtxs.append(newCtx)
		self.imported.append(realNewPath)
		return True

	def closeCurrentCtx(self): #return True if no more context remains
		lst_pop(self.subCtxs)
		if lst_isEmpty(self.subCtxs):
			self.ctx = None
			return True
		self.ctx = lst_last(self.subCtxs)
		return False

	def overwriteSubCtxs(self, subCtxs):
		self.subCtxs = subCtxs
		if lst_isEmpty(subCtxs):
			self.ctx = None
		else:
			self.ctx = subCtxs[-1]



	# COMPILATION TOOLS

	#output after precompilation is closely related to ZCIs, no longer to global subCtxs
	def ZCIDebug(self, ZCI, msg):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.debug(msg)

	def ZCIWarning(self, ZCI, msg):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.warning(msg)

	def ZCIError(self, ZCI, msg):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.error(msg)

	def ZCIInternal(self, ZCI, msg):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.internal(msg)

	#move ctx cursor just before the first non-blank character found
	def jumpBlankZone(self, ZCI, missingFieldsIfError):
		while not ZCI.inc():
			if ZCI.get() not in BLANKS:
				return
		if missingFieldsIfError is not None:
			self.ZCIError(ZCI, "Expected something after blank zone : " + missingFieldsIfError)

	#read a name according to the given charset (either blacklist or whitelist)
	# IMPORTANT : Reading ctx from its CURRENT position and move it right AFTER the extracted result
	#also, blacklist is prioritary : if null => use whitelist, else, use it (no matter whitelist value)
	def readName(self, ZCI, missingFieldIfError, blacklist=None, whitelist=DATAITEM_NAME_CHARSET):

		#check initial character first
		c = ZCI.get()
		if blacklist is None:
			error = c not in whitelist
		else:
			error = c in blacklist

		#missing name field
		if error:
			if missingFieldIfError is None:
				return
			self.ZCIError(ZCI, "Missing name : " + missingFieldIfError)

		#read until BLANK or end
		name = c
		while not ZCI.inc():
			c = ZCI.get()
			if blacklist is None:
				if c not in whitelist:
					break
			elif c in blacklist:
				break
			name += c

		#return result
		return name

	def optionnalBlanks(self, ZCI, missingFieldsIfError):
		if ZCI.get() in BLANKS:
			self.jumpBlankZone(ZCI, missingFieldsIfError=missingFieldsIfError)



	# DEBUG

	#modules
	def debugModules(self):
		unprefixedModules = ""
		for mp in self.cpl.modulePrefixes:
			unprefixedModules += "\n - " + unprefixizeModule(mp)
		self.debug("Available modules are :" + unprefixedModules, printSubCtxs=False)
