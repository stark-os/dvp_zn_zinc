#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.stack      import *
from std.io         import *
from std.parsingCtx import *

#charsets
import string






# -------- CONSTANTS --------

#precompiler
PCPL_VAR_NAME_CHARSET = string.ascii_letters + string.digits + '_'

#general syntax
BLANKS           = (" ", "\t")
VAR_NAME_CHARSET = PCPL_VAR_NAME_CHARSET






# -------- PRECOMPILATION --------

#precompiled ZCI
class pzci:
	def __init__(self, ctx, text):
		self.ctx  = ctx
		self.text = text

#precompiler data
class pcplDat:
	def __init__(self, configs, items):
		self.dataResult = {}
		self.items      = items
		self.configs    = configs
		self.ZCIs       = [] #lst[pzci]

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

#includers
INCLUDERS = { '(':')', '[':']', '{':'}' }






# -------- COMPILATION --------

#compiler data
class cplDat:
	def __init__(self, options):
		self.options    = options
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
		self.importedCtxs = Stack()
		self.importedCtxs.push(initialCtx)

		#syntax
		self.scope    = Stack()
		self.includer = Stack()

		#data
		self.zcs  = []
		self.pcpl = pcplDat(pcpl_cfg, pcpl_itm)
		self.cpl  = cplDat(cpl_opt)



	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)



	#output
	def debug(self, msg):
		print("[ DEBUG ] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))

	def warning(self, msg):
		print("[WARNING] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))

	def error(self, msg):
		print("[ ERROR ] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))
		exit(1)

	def internal(self, msg):
		print("[INT ERR] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))
		exit(2)



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
		for c in self.importedCtxs.data:
			if newCtx.filepath == c.filepath:
				print("FILE " + newCtx.filepath + " already processed")
				return False

		#not already openned => add it to importations
		self.ctx = newCtx
		self.importedCtxs.push(newCtx)
		return True

	def closeCurrentCtx(self): #return True if no more context remains
		self.importedCtxs.pop()
		if self.importedCtxs.isEmpty():
			return True
		self.ctx = self.importedCtxs.last()
		return False



	#precompilation
	def appendZCI(self, ZCIText, ZCIBeginningColumnNbr):
		ZCICtx           = self.ctx.copy()
		ZCICtx.columnNbr = ZCIBeginningColumnNbr
		self.pcpl.ZCIs.append(
			pzci(
				ZCICtx,
				ZCIText
			)
		)
