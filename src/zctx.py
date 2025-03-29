#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.string     import *
from std.path       import *
from std.list       import *
from std.io         import *
from std.parsingCtx import *

#charsets
import string






# -------- GENERAL --------

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DEFAULT_NAME_CHARSET            = string.ascii_letters + string.digits + '_'
ZCI_FIRSTWORD_DETECTION_CHARSET = BLANKS + tuple(INCLUDERS.keys())

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

#tools
def unprefixizeModule(modulePrefix):
	if len(modulePrefix) == 0:
		return ""
	return "^" + str_sub(modulePrefix, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1]

#ZCI
class zci:
	def __init__(self, subCtxs, modulePrefix="", pairs=None): #python: ", pairs={}" NEVER ! it will link every instance to the same element => You don't want that !
		self.subCtxs = subCtxs
		if lst_isEmpty(subCtxs):
			self.ctx = None
		else:
			self.ctx = subCtxs[-1]
		if pairs is None:
			pairs = {}
		self.pairs        = pairs #map[unt_l,unt_l]
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

	def updateCtx(self, newCtx):
		self.ctx = newCtx

		#replace the last subctx reference by our newCtx
		lst_pop(self.subCtxs)
		self.subCtxs.append(newCtx)






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
	def __init__(self, name, dcnDeg, size, isStc, fields=[], parent=None, dcns=None):
		self.name    = name
		self.parent  = parent
		self.methods = []     #lst[zfct]
		self.size    = size

		#declination
		self.dcnDeg = dcnDeg #declination degree
		self.dcns   = dcns   #current declination, tab[ztyp]

		#stc related
		self.isStc   = isStc #<=> type "nature" (is primitive / structure)
		self.fields  = fields
		self.stcSize = 0
		if isStc:
			for f in fields:
				self.stcSize += f.zType.size

class dataItem:
	def __init__(self, zType, name, initialValue, constant=False):
		self.zType        = zType
		self.name         = name
		self.initialValue = initialValue
		self.constant     = constant

#compiler data
class cplDat:
	def __init__(self, options, rootTypes):
		self.options = options

		#z abstract elements
		self.modulePrefixes = []
		self.ztypes         = rootTypes

		#program concrete elements
		self.dataResult = program()
		self.textResult = ""






# -------- CONTEXTS --------

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
		rootTypes = [
			ztyp("boo", 0, self.SIZE__BYT, False),
			ztyp("byt", 0, self.SIZE__BYT, False), ztyp("ubyt", 0, self.SIZE__BYT, False), #integers
			ztyp("shr", 0, self.SIZE__SHR, False), ztyp("ushr", 0, self.SIZE__SHR, False),
			ztyp("int", 0, self.SIZE__INT, False), ztyp("uint", 0, self.SIZE__INT, False),
			ztyp("lng", 0, self.SIZE__LNG, False), ztyp("ulng", 0, self.SIZE__LNG, False),
			ztyp("flt", 0, self.SIZE__INT, False), ztyp("dbl",  0, self.SIZE__LNG, False),  #floating point
			ztyp("ptr", 1, self.SIZE__LNG, False) #pointer
		]

		#data
		self.ZCIs = None
		self.pcpl = pcplDat_new(pcpl_cfg, pcpl_itm)
		self.cpl  = cplDat(cpl_opt, rootTypes)



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
	def debug(self, msg, printSubCtxs=True, printLine=True):
		if self.debugMode:
			print("[ DEBUG ] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				self.ctx.printLineIndicator()

	def warning(self, msg, printSubCtxs=True, printLine=True):
		print("[WARNING] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			self.ctx.printLineIndicator()

	def error(self, msg, printSubCtxs=True, printLine=True):
		print("[ ERROR ] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			self.ctx.printLineIndicator()
		exit(1)

	def internal(self, msg, printSubCtxs=True, printLine=True):
		print("[INT ERR] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			self.ctx.printLineIndicator()
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



	# ZCI OUTPUT (cpl)

	#output after precompilation is closely related to ZCIs, no longer to global subCtxs
	def ZCIDebug(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.debug(msg, printSubCtxs=printSubCtxs, printLine=printLine)

	def ZCIWarning(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.warning(msg, printSubCtxs=printSubCtxs, printLine=printLine)

	def ZCIError(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.error(msg, printSubCtxs=printSubCtxs, printLine=printLine)

	def ZCIInternal(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.internal(msg, printSubCtxs=printSubCtxs, printLine=printLine)



	# GENERAL PARSING TOOLS

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
	#
	# /!\ This method must be included in STDZ into ^Parsing.ctx whithout the module prefix part.
	#     Must also include the first 2 lines of comment over it
	#
	def readName(self,
		ZCI,
		missingFieldIfError, #null means "don't raise error if empty"
		blacklist=None, whitelist=DEFAULT_NAME_CHARSET,
		parseModulePrefixes=False,
		modulePrefix_asHeaderOnly=False #means "if any, it must BEGIN with it and be the only occurrence"
	):

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

						#can't continue ? => ending ZCI text without giving the module element to target
						if ZCI.inc():
							zCtx.ZCIError(ZCI, "Missing an element name to target inside that module (reached end of ZCI)")

						#chaining with another module name (potentially) => continue in the same loop, else => break here, we reached our next "name" character
						c = ZCI.get()
						if c == '^':
							currentModuleName = ""
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

			#no longer in first character (maybe, getting rid of the "if" and keeping only the assignation would be more optimized ?)
			if firstCharacter:
				firstCharacter = False

		#missing name field
		if len(name) == 0:
			if missingFieldIfError is None:
				return ""
			self.ZCIError(ZCI, "Missing name : " + missingFieldIfError)

		#return result
		return name

	def optionnalBlanks(self, ZCI, missingFieldsIfError):
		if ZCI.get() in BLANKS:
			self.jumpBlankZone(ZCI, missingFieldsIfError=missingFieldsIfError)

	def endOfZCI(self, ZCIKindIfError):
		if not ZCI.reachedEnd():
			self.ZCIError(ZCI, "Too much elements in " + ZCIKindIfError + " Should stop here.")

	def splitModulePrefix(self, ZCI, name):
		if len(name) == 0:
			return ""
		if name[0] != 'M': #no module prefix
			return ""

		#get only module prefix from name
		modulePrefix    = "M"
		foundUnderscore = False
		for c in name:

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

	#read content inside an includer and strip it from blanks & line feeds.
	# Given ZCI must be at the beginning of that includer (openning peer) and will be forwarded right after it (after closing peer).
	def getIncluderStrippedContent(self, ZCI, IncluderContentIfError):
		peerIndex = ZCI.pairs[ZCI.ctx.icontent.index]
		ZCI.inc()

		#skip beginning blanks
		beginningShift = str_getBeginningStripIndex(
			str_sub(ZCI.ctx.icontent.s, start=ZCI.ctx.icontent.index),
			charset=BLANKS_EXTENDED
		)
		for a in range(beginningShift): #keep a consistent ctx (lineNbr & colmNbr)
			ZCI.inc()

		#get ctx copy from the REAL beginning
		contentCtx = ZCI.ctx.copy()

		#strip ending blanks
		beginningIndex = ZCI.ctx.icontent.index
		content = str_stripEnd(
			str_sub(ZCI.ctx.icontent.s, start=beginningIndex, stop=peerIndex-1),
			charset=BLANKS_EXTENDED
		)

		#forward initial ZCI after ending peer
		ZCI.forward(peerIndex - beginningIndex + 1)

		#return content & its associated ctx for erroring/debugging
		return (contentCtx, content) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< great example of "fly" use (can be solved using tab[atm] for the moment



	# DEBUG

	#modules
	def debugModules(self):
		unprefixedModules = ""
		for mp in self.cpl.modulePrefixes:
			unprefixedModules += "\n - " + unprefixizeModule(mp)
		self.debug("Available modules are :" + unprefixedModules, printSubCtxs=False)

	#cpl steps output
	def cplStep_debugZCIs(self, cplStep):
		if self.debugMode:
			debugOutput = "[\n"
			for ZCI in self.ZCIs:
				content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
				debugOutput += "{module:\"" + ZCI.modulePrefix + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
			debugOutput += "]"
			writeFile("debug/" + path_name(self.initialCtx.filename) + ".c" + cplStep + ".json", debugOutput)



	# ABSTRACT ZCEs PARSING TOOLS

	#expecting a Z type
	def readZType(self, ZCI, ZCIKindIfError):

		#read full type name
		ztModulePrefix = ""
		if ZCI.get() == '^':
			ztRawName      = self.readName(ZCI, "Type name in " + ZCIKindIfError, parseModulePrefix=True, modulePrefix_asHeaderOnly=True) #actually, this is more the "FullName" but without declination prefix (so ~almost~ full)
			ztModulePrefix = self.splitModulePrefix(ZCI, ztRawName)        #save its module prefix elsewhere
			ztRawName      = str_sub(ztRawName, start=len(ztModulePrefix)) # + cut it from the "almost full name" to get only the RAW name
		else:
			ztRawName = self.readName(ZCI, "Type name in " + ZCIKindIfError)
		ztFullName = ztModulePrefix + 'U' + ztRawName

		#1 - check UNDECLINATED variant existence
		ztInstance = None
		for t in self.cpl.ztypes:
			if ztFullName == t.name:
				ztInstance = t #not the definitive one, this is a first base (undeclinated only here)
				break
		if ztInstance is None:
			self.ZCIError(ZCI, "Type " + unprefixizeModule(ztModulePrefix) + ztRawName + " does not exist.")

		#2 - declination list given => solve them
		if ZCI.get() == '[':

			#undeclinable type
			if ztInstance.dcnDeg == 0:
				self.ZCIError(ZCI, "Type " + unprefixizeModule(ztModulePrefix) + ztRawName + " is not declinable (null declination degree).")

			#read declination types
			dcnsTextCtx, dcnsText = self.getIncluderStrippedContent(ZCI, "type declination list")

			#create an alternative ZCI especially to read declination types
			dcnsZCI = zci(dcnsTextCtx, ZCI.subCtxs, modulePrefix=ZCI.modulePrefix, pairs=ZCI.pairs) #same exact copy but starts with dcnsCtx instead

			#read declination types one by one
			dcns = [] #lst[ztyp]
			while True:
				dcns.append(self.readZType(dcnsZCI))

				#must be followed by coma or closing peer
				optionnalBlanks(dcnsZCI, None)
				if dcnsZCI.get() == ']':
					break
				elif dcnsZCI.get() != ',':
					self.ZCIError(dcnsZCI, "Invalid element given in declination types sequence (expected coma separator ',').")
				dcnsZCI.inc()
				optionnalBlanks(dcnsZCI, None)

			#check declination length
			if len(dcns) < ztInstance.dcnDeg:
				self.ZCIError(dcnsZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(ztInstance.dcnDeg) + " required).")
			elif len(dcns) > ztInstance.dcnDeg:
				self.ZCIError(dcnsZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(ztInstance.dcnDeg) + " required).")

			#re-build full type name including declinations this time
			ztFullName = ztModulePrefix + 'D' + ztRawName
			for d in dcns:
				ztFullName += '_' + d.name

			#check for that declination in the currently declared ztypes
			ztInstanceUndeclinated = ztInstance
			ztInstance             = None
			for t in self.cpl.ztypes:
				if ztFullName == t.name:
					ztInstance = t
					break

			#not found => create that declination (this new combination must exist)
			if ztInstance is None:
				self.cpl.ztypes.append(ztInstance)
				ztInstance = ztyp(
					ztFullName, len(dcns),
					ztInstanceUndeclinated.size,
					ztInstanceUndeclinated.isStc,
					fields=ztInstanceUndeclinated.fields, #TODO : copy fields + replace elements affected by declination <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TODO
					parent=ztInstanceUndeclinated,
					dcns=dcns
				)

		#final result
		return ztInstance



	#
	def readKeyValueFields(self, ZCI, typesRequired=False):
		return []

		peerIndex = ZCI.ctx.getCorrespondingPeerIndex(peers=INCLUDERS)
		if peerIndex < 0:
			self.ZCIInternal(ZCI, "Inconsistent use of includers inside type definition block but this should have been checked in step P3.")
		ZCI.inc()

		#skip beginning blanks
		beginningShift = str_getBeginningStripIndex(
			str_sub(ZCI.ctx.icontent.s, start=ZCI.ctx.icontent.index),
			charset=BLANKS_EXTENDED
		)
		for a in range(beginningShift): #keep a consistent ctx (lineNbr & colmNbr)
			ZCI.inc()
		beginningIndex = ZCI.ctx.icontent.index

		#read content in braces includer
		fieldsText = str_stripEnd(
			str_sub(ZCI.ctx.icontent.s, start=beginningIndex, stop=peerIndex-1),
			charset=BLANKS_EXTENDED
		)

		#parse fields
		fields = []
		currentField = dataItem(None, "", None)
		for i in range(len(fieldsText)):
			pass

			#get name
			#currentField.name = zCtx.readName("")

			#optionnal, =, optionnal
			#initialValue = readValue(zCtx, ZCI, constant=True) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

		#empty structure not allowed
		if False: #len(fields) == 0:
			self.ZCIError(ZCI, "No field given in structure type declaration (DCL_TYP), at least one is required.")

		#fields
		return fields
